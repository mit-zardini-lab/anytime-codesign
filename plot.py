import yaml
import re
import matplotlib.pyplot as plt
from pathlib import Path
from collections import Counter
import matplotlib.cm as cm
import numpy as np

# Path to the YAML file
yaml_path = Path('coverage_blind_robot.mcdplib/out-query/output.yaml')

# Load the YAML file
def load_yaml(path):
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def extract_data(pretty_str):
    # Regex to find entries like ⟨40 USD,1390.97 s⟩: ... followed by robot info
    pattern = r'⟨([\d.]+) USD,([\d.]+) s⟩:\s*[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|(robot_\d+)\|'
    matches = re.findall(pattern, pretty_str)
    usd_list = []
    sec_list = []
    robot_list = []
    for usd, sec, robot in matches:
        usd_list.append(float(usd))
        sec_list.append(float(sec))
        robot_list.append(robot)
    return usd_list, sec_list, robot_list

def process_robot_string(robot_str):
    # Simply return the robot string as is
    return robot_str

def main():
    data = load_yaml(yaml_path)
    pretty_str = data['optimistic']['imps']['pretty']
    usd_list, sec_list, robot_list = extract_data(pretty_str)

    # Process each robot string as requested
    processed_results = [process_robot_string(robot) for robot in robot_list]
    for robot, robot_desc in zip(robot_list, processed_results):
        print(f"Robot: {robot_desc}")

    # Sort points by increasing x (USD)
    sorted_points = sorted(zip(usd_list, sec_list, processed_results), key=lambda t: t[0])
    usd_list, sec_list, processed_results = zip(*sorted_points)

    # Prepare labels for legend - use the robot description directly
    labels = processed_results

    # Assign a unique color to each point
    colors = cm.get_cmap('tab20', len(usd_list))

    plt.figure(figsize=(10, 6))
    # Set global font size for all text in the plot
    plt.rcParams.update({'font.size': 14})
    # Plot each point with its unique color and add to legend
    handles = []
    for i, (x, y, label) in enumerate(zip(usd_list, sec_list, labels)):
        sc = plt.scatter(x, y, color=colors(i), label=label)
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
    plt.tight_layout()
    plt.legend(handles=handles, loc='best', fontsize=12)
    plt.show()

if __name__ == "__main__":
    main()