import yaml
import matplotlib.pyplot as plt
import numpy as np
from collections import defaultdict
import re

def extract_numeric_value(value_str):
    """Extract numeric value from a string like '39.8011 s' or '17.5424 m^2'"""
    if isinstance(value_str, (int, float)):
        return float(value_str)
    
    # Use regex to find the first number in the string
    match = re.search(r'[\d.]+', str(value_str))
    if match:
        return float(match.group())
    return None

def get_type_key(r_min, f_max):
    """Extract the first three values from r_min and the rad value from f_max to define the type"""
    type_values = []
    
    # Get first three values from r_min
    if len(r_min) >= 3:
        for i in range(3):
            val = extract_numeric_value(r_min[i])
            if val is not None:
                type_values.append(val)
            else:
                return None
    else:
        return None
    
    # Get rad value from f_max (should be the FIRST element, not second!)
    if len(f_max) >= 1:
        rad_val = extract_numeric_value(f_max[0])  # FIRST element is rad value
        if rad_val is not None:
            type_values.append(rad_val)
        else:
            return None
    else:
        return None
    
    return tuple(type_values) if len(type_values) == 4 else None

def select_types_to_display(type_data):
    """Allow user to select which types to display"""
    if not type_data:
        print("No valid data found!")
        return {}
        
    print("\nAvailable types:")
    type_list = list(type_data.keys())
    
    for i, type_key in enumerate(type_list):
        data_count = len(type_data[type_key]['times'])
        print(f"  {i+1}: Type ({type_key[0]}, {type_key[1]}, {type_key[2]}, {type_key[3]} rad) - {data_count} points")
    
    print(f"\nOptions:")
    print(f"  - Enter numbers separated by commas (e.g., '1,3,5') to select specific types")
    print(f"  - Enter 'all' to display all types")
    print(f"  - Press Enter to display all types")
    
    user_input = input("\nYour selection: ").strip()
    
    if user_input == '' or user_input.lower() == 'all':
        return type_data
    
    try:
        # Parse user selection
        selected_indices = [int(x.strip()) - 1 for x in user_input.split(',')]
        selected_types = {}
        
        for idx in selected_indices:
            if 0 <= idx < len(type_list):
                type_key = type_list[idx]
                selected_types[type_key] = type_data[type_key]
            else:
                print(f"Warning: Index {idx+1} is out of range, skipping...")
        
        if not selected_types:
            print("No valid types selected. Displaying all types.")
            return type_data
        
        print(f"\nSelected {len(selected_types)} type(s) for display.")
        return selected_types
        
    except ValueError:
        print("Invalid input format. Displaying all types.")
        return type_data

def main():
    # Read the YAML file
    with open('coverage_blind_robot.mcdplib/coverage_algorithm_catalogues/square15_coverage_algorithm_catalogue.yaml', 'r') as file:
        data = yaml.safe_load(file)
    
    # Dictionary to store data by type
    type_data = defaultdict(lambda: {'times': [], 'areas': []})
    
    # Process implementations
    implementations = data.get('implementations', {})
    
    print(f"Processing {len(implementations)} implementations...")
    processed_count = 0
    skipped_count = 0
    
    for impl_name, impl_data in implementations.items():
        # Skip if implementation doesn't have required data
        if 'r_min' not in impl_data or 'f_max' not in impl_data:
            print(f"Skipping {impl_name}: missing r_min or f_max")
            skipped_count += 1
            continue
            
        r_min = impl_data['r_min']
        f_max = impl_data['f_max']
        
        # Check if we have enough data
        if len(r_min) < 4:
            print(f"Skipping {impl_name}: r_min has only {len(r_min)} elements, need 4")
            skipped_count += 1
            continue
            
        if len(f_max) < 3:
            print(f"Skipping {impl_name}: f_max has only {len(f_max)} elements, need 3")
            skipped_count += 1
            continue
        
        # Get type (first three values of r_min + rad value from f_max)
        type_key = get_type_key(r_min, f_max)
        if type_key is None:
            print(f"Skipping {impl_name}: could not extract type")
            skipped_count += 1
            continue
            
        # Extract time (last value in r_min)
        time = extract_numeric_value(r_min[-1])  # Last element should be time
        
        # Extract area (last value in f_max) - should be index 2 based on your structure
        area = extract_numeric_value(f_max[2])  # Third element should be area
            
        # Store data if both time and area are valid
        if time is not None and area is not None:
            type_data[type_key]['times'].append(time)
            type_data[type_key]['areas'].append(area)
            processed_count += 1
            print(f"Processed {impl_name}: type={type_key}, time={time}, area={area}")
        else:
            print(f"Skipping {impl_name}: could not extract time or area")
            skipped_count += 1
    
    print(f"\nProcessing complete: {processed_count} processed, {skipped_count} skipped.")
    
    # Print summary information
    print(f"Found {len(type_data)} different types:")
    for type_key, data in type_data.items():
        print(f"  Type {type_key}: {len(data['times'])} data points")
    
    # Let user select which types to display
    selected_type_data = select_types_to_display(type_data)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    colors = plt.cm.tab10(np.linspace(0, 1, len(selected_type_data)))
    
    for i, (type_key, data) in enumerate(selected_type_data.items()):
        times = data['times']
        areas = data['areas']
        
        # Sort by time for better line plotting
        sorted_pairs = sorted(zip(times, areas))
        sorted_times, sorted_areas = zip(*sorted_pairs) if sorted_pairs else ([], [])
        
        # Create label for the type (now includes rad value)
        type_label = f"Type ({type_key[0]}, {type_key[1]}, {type_key[2]}, {type_key[3]} rad)"
        
        # Plot the data
        plt.plot(sorted_times, sorted_areas, 'o-', color=colors[i], 
                label=type_label, linewidth=2, markersize=6)
    
    plt.xlabel('Time (s)')
    plt.ylabel('Coverage Area (m²)')
    plt.title('Coverage Area vs Time by Configuration Type')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    main()