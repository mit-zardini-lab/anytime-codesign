import yaml
import re
import matplotlib.pyplot as plt
from pathlib import Path
import matplotlib.cm as cm
import numpy as np
from collections import defaultdict
import os
import argparse

# Paths
out_query_path = Path('coverage_blind_robot.mcdplib/out-query')
robot_catalog_path = Path('coverage_blind_robot.mcdplib/robot_catalog.yaml')

def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def extract_data(pretty_str):
    pattern = r'⟨([\d.]+) USD,([\d.]+) s⟩:.*?(robot_\d+)'
    matches = re.findall(pattern, pretty_str, re.DOTALL)
    usd_list = []
    sec_list = []
    robot_list = []
    for usd, sec, robot in matches:
        usd_list.append(float(usd))
        sec_list.append(float(sec))
        robot_list.append(robot)
    return usd_list, sec_list, robot_list

def find_robot_by_cost(robot_catalog, target_cost):
    """Find robot name by matching the cost"""
    for robot_name, specs in robot_catalog['implementations'].items():
        robot_cost = float(specs['r_min'][0].split()[0])
        if abs(robot_cost - target_cost) < 0.01:
            return robot_name, specs
    return None, None

def create_robot_label(robot_name, specs):
    """Create a descriptive label for the robot"""
    if specs is None:
        return robot_name
    
    f_max = specs['f_max']
    r_min = specs['r_min']
    
    position_range = f"[{f_max[0]}, {f_max[1]}, {f_max[2]}]"
    cost_precision = f"[{r_min[0]}, {r_min[1]}]"
    
    return f"{robot_name}: {position_range} @ {cost_precision}"

def process_robot_string(robot_str, robot_catalog, usd_cost):
    """Process robot string and create descriptive label"""
    robot_name, specs = find_robot_by_cost(robot_catalog, usd_cost)
    if robot_name:
        return create_robot_label(robot_name, specs)
    else:
        return robot_str

def parse_filename(filename):
    """Parse filename to extract number and environment"""
    # Remove .yaml extension
    name = filename.replace('.yaml', '')
    # Split by underscore
    parts = name.split('_', 1)  # Split into at most 2 parts
    if len(parts) == 2:
        try:
            number = int(parts[0])
            environment = parts[1]
            return number, environment
        except ValueError:
            return None, None
    return None, None

def get_yaml_files_data():
    """Get all YAML files and organize by number and environment"""
    files_data = defaultdict(dict)  # {number: {environment: filepath}}
    
    if not out_query_path.exists():
        print(f"Directory {out_query_path} does not exist")
        return files_data
    
    for file_path in out_query_path.glob('*.yaml'):
        number, environment = parse_filename(file_path.name)
        if number is not None and environment is not None:
            files_data[number][environment] = file_path
    
    return files_data

def plot_tradeoff_subplot(ax, env_data, env_colors, title, show_shadow=True):
    """Plot tradeoff in a subplot with separate lines per environment"""
    if not env_data:
        ax.text(0.5, 0.5, 'No data', ha='center', va='center', transform=ax.transAxes)
        ax.set_title(title)
        return
    
    legend_handles = []
    
    # First, find the global y_max and x_max for all environments in this subplot
    all_y_values = []
    all_x_values = []
    for environment, (usd_list, sec_list, processed_results) in env_data.items():
        if sec_list:
            all_y_values.extend(sec_list)
        if usd_list:
            all_x_values.extend(usd_list)
    
    if all_y_values:
        y_max = max(all_y_values) * 1.05
    else:
        y_max = 100  # fallback value
        
    if all_x_values:
        x_max = max(all_x_values) * 1.05
    else:
        x_max = 300  # fallback value
    
    # Plot each environment as a separate line
    for environment, (usd_list, sec_list, processed_results) in env_data.items():
        if not usd_list:
            continue
            
        # Sort points by increasing x (USD)
        sorted_points = sorted(zip(usd_list, sec_list, processed_results), key=lambda t: t[0])
        usd_sorted, sec_sorted, labels_sorted = zip(*sorted_points)
        
        # Get environment color
        env_color = env_colors[environment]
        
        # Plot all points for this environment with the same color
        scatter = ax.scatter(usd_sorted, sec_sorted, color=env_color, s=50, label=environment)
        
        # Add to legend handles
        legend_handles.append(plt.Line2D([0], [0], marker='o', color=env_color, 
                                       markerfacecolor=env_color, 
                                       markersize=8, label=environment, linewidth=2))
        
        # Draw axis-parallel (step) lines for this environment
        if sec_sorted:
            for i in range(len(usd_sorted) - 1):
                x0, y0 = usd_sorted[i], sec_sorted[i]
                x1, y1 = usd_sorted[i+1], sec_sorted[i+1]
                ax.plot([x0, x1], [y0, y0], color=env_color, linestyle='--', linewidth=1)
                
                # Only add shadow/fill if show_shadow is True
                if show_shadow:
                    ax.fill_between([x0, x1], y0, y_max, color=env_color, alpha=0.2)
                
                ax.plot([x1, x1], [y0, y1], color=env_color, linestyle='--', linewidth=1)
            
            # Fill from the last point to the global right edge (only if show_shadow is True)
            if show_shadow and usd_sorted and sec_sorted:
                last_x = usd_sorted[-1]
                last_y = sec_sorted[-1]
                
                # Fill to the global x_max
                ax.fill_between([last_x, x_max], last_y, y_max, color=env_color, alpha=0.2)
    
    # Set the x-axis limit to ensure the plot shows the full range
    ax.set_xlim(left=min(all_x_values) * 0.95 if all_x_values else 0, right=x_max)
    
    # Add legend to this subplot in the upper right
    if legend_handles:
        ax.legend(handles=legend_handles, loc='upper right', fontsize=10, 
                 frameon=True, fancybox=True, shadow=True)
    
    ax.set_xlabel('USD')
    ax.set_ylabel('Seconds')
    ax.set_title(title)
    ax.grid(True)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Plot tradeoff analysis across different covered areas and environments')
    parser.add_argument('--shadow', action='store_true', 
                       help='Show shaded areas in the plot')
    args = parser.parse_args()
    
    # Load robot catalog
    try:
        robot_catalog = load_yaml(robot_catalog_path)
    except FileNotFoundError:
        print(f"Robot catalog not found at {robot_catalog_path}")
        robot_catalog = None
    
    # Get all YAML files organized by number and environment
    files_data = get_yaml_files_data()
    
    if not files_data:
        print("No YAML files found matching the pattern {number}_{environment}.yaml")
        return
    
    # Get unique numbers (sorted) and environments
    numbers = sorted(files_data.keys())
    all_environments = set()
    for number_data in files_data.values():
        all_environments.update(number_data.keys())
    environments = sorted(all_environments)
    
    print(f"Found numbers: {numbers}")
    print(f"Found environments: {environments}")
    print(f"Shadow enabled: {args.shadow}")
    
    # Create subplot grid: 1 row, len(numbers) columns
    fig, axes = plt.subplots(1, len(numbers), figsize=(5 * len(numbers), 6))
    
    # Handle case where there's only one subplot
    if len(numbers) == 1:
        axes = [axes]
    
    # Set global font size
    plt.rcParams.update({'font.size': 12})
    
    # For legend - collect environment colors (use new matplotlib colormap syntax)
    cmap = plt.get_cmap('tab10')
    env_colors = {env: cmap(i) for i, env in enumerate(environments)}
    
    # Plot each number (column)
    for col_idx, number in enumerate(numbers):
        ax = axes[col_idx]
        
        # Organize data by environment for this number
        env_data = {}
        
        for environment in environments:
            if environment in files_data[number]:
                file_path = files_data[number][environment]
                try:
                    data = load_yaml(file_path)
                    pretty_str = data['optimistic']['imps']['pretty']
                    usd_list, sec_list, robot_list = extract_data(pretty_str)
                    
                    if usd_list and robot_catalog:
                        processed_results = [process_robot_string(robot, robot_catalog, usd) 
                                           for robot, usd in zip(robot_list, usd_list)]
                        env_data[environment] = (usd_list, sec_list, processed_results)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        # Plot this number's data with shadow control
        plot_tradeoff_subplot(ax, env_data, env_colors, f"Minimum covered area: {number} m²", 
                             show_shadow=args.shadow)
    
    plt.suptitle('Tradeoff Analysis Across Different Covered Areas and Environments', 
                 fontsize=16, y=0.95)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()