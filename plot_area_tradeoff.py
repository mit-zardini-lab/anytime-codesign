import yaml
import re
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter
import matplotlib.cm as cm
import numpy as np

# Path to the YAML file
yaml_path = Path('coverage_blind_robot.mcdplib/out-query/output.yaml')
robot_catalog_path = Path('coverage_blind_robot.mcdplib/robot_catalog.yaml')

# Load the YAML file
def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def extract_data(pretty_str):
    # Regex to find entries like ⟨100 USD,39.3996 s⟩: ... followed by robot info
    # The robot_X appears much later in the string, so we need a more flexible pattern
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
        robot_cost = float(specs['r_min'][0].split()[0])  # Extract USD value
        if abs(robot_cost - target_cost) < 0.01:  # Small tolerance for floating point comparison
            return robot_name, specs
    return None, None

def create_robot_label(robot_name, specs):
    """Create a descriptive label for the robot"""
    if specs is None:
        return robot_name
    
    # Extract specifications
    f_max = specs['f_max']
    r_min = specs['r_min']
    
    # Format: robot_X: [x,y,v] @ [cost, precision]
    position_range = f"[{f_max[0]}, {f_max[1]}, {f_max[2]}]"
    cost_precision = f"[{r_min[0]}, {r_min[1]}]"
    
    return f"{robot_name}: {position_range} @ {cost_precision}"

def process_robot_string(robot_str, robot_catalog, usd_cost):
    """Process robot string and create descriptive label"""
    robot_name, specs = find_robot_by_cost(robot_catalog, usd_cost)
    if robot_name:
        return create_robot_label(robot_name, specs)
    else:
        return robot_str  # Fallback to original if not found

def main():
    data = load_yaml(yaml_path)
    robot_catalog = load_yaml(robot_catalog_path)
    pretty_str = data['optimistic']['imps']['pretty']
    usd_list, sec_list, robot_list = extract_data(pretty_str)

    # Check if we have data
    if not usd_list:
        print("No data found. Check the regex pattern or YAML structure.")
        print(f"Pretty string: {pretty_str[:200]}...")
        return

    # Process each robot string with catalog lookup
    processed_results = [process_robot_string(robot, robot_catalog, usd) 
                        for robot, usd in zip(robot_list, usd_list)]
    for robot, robot_desc in zip(robot_list, processed_results):
        print(f"Robot: {robot_desc}")

    # Sort points by increasing x (USD)
    sorted_points = sorted(zip(usd_list, sec_list, processed_results), key=lambda t: t[0])
    usd_list, sec_list, processed_results = zip(*sorted_points)

    # Prepare labels for legend - use the robot description directly
    labels = processed_results

    # Assign a unique color to each point
    colors = cm.get_cmap('tab20', len(usd_list))

    plt.figure(figsize=(16, 8))  # Wider figure to accommodate legend
    # Set global font size for all text in the plot
    plt.rcParams.update({'font.size': 14})
    # Plot each point with its unique color and add to legend
    handles = []
    for i, (x, y, label) in enumerate(zip(usd_list, sec_list, labels)):
        sc = plt.scatter(x, y, color=colors(i), label=label, s=100)  # Increased marker size
        handles.append(sc)

    # Get y-axis upper limit for filling
    y_max = max(sec_list) * 1.05

    # Draw axis-parallel (step) lines and fill above them (use black for lines)
    for i in range(len(usd_list) - 1):
        x0, y0 = usd_list[i], sec_list[i]
        x1, y1 = usd_list[i+1], sec_list[i+1]
        plt.plot([x0, x1], [y0, y0], 'k--', linewidth=1)
        plt.fill_between([x0, x1], y0, y_max, color='orange', alpha=0.3)
        plt.plot([x1, x1], [y0, y1], 'k--', linewidth=1)
        plt.fill_between([x1, x1], [y0], [y_max], color='orange', alpha=0.3)

    plt.xlabel('USD', fontsize=18)
    plt.ylabel('Seconds', fontsize=18)
    plt.title('Tradeoff: Robot USD vs Seconds', fontsize=20)
    plt.xticks(fontsize=16)
    plt.yticks(fontsize=16)
    plt.grid(True)
    
    # Create legend and adjust layout
    plt.legend(handles=handles, loc='center left', bbox_to_anchor=(1, 0.5), fontsize=10)
    plt.tight_layout()
    plt.subplots_adjust(right=0.7)  # Make room for legend on the right
    plt.show()

if __name__ == "__main__":
    main()