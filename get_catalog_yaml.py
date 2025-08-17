import itertools
import yaml

theta_max = ['0.01','0.02','0.03','0.04']
radius_body = ['0.5', '1.0', '1.5']
radius_sensor = ['1.0', '1.5', '2.0', '3.0']
robot_speeds = ['0.5', '1.0', '1.5']  # Fixed speed for all robots

# Create the catalog structure
catalog = {
    'F': [
        'm',  # physical_radius
        'm',  # sensoring_radius
        'm/s' # speed
    ],
    'R': [
        'USD', # cost
        'rad'  # angular_actuation_error_budget
    ],
    'implementations': {}
}

# Generate implementations
costs = []
for i, (t, r_body, r_sensor, speed) in enumerate(itertools.product(theta_max, radius_body, radius_sensor, robot_speeds)):
    t_val = float(t)
    r_body_val = float(r_body)
    r_sensor_val = float(r_sensor)
    cost = int(r_body_val * 50 + r_sensor_val * 50 - t_val * 1000 + 30 + float(speed) * 10)
    if cost in costs:
        print(f"Warning: Duplicate cost {cost} for robot_{i}")
        # Adapt cost slightly to ensure uniqueness
        while cost in costs:
            cost += 10
    costs.append(cost)

    impl_name = f"robot_{i}"
    
    catalog['implementations'][impl_name] = {
        'f_max': [
            f'{r_body_val} m',    # physical_radius
            f'{r_sensor_val} m',    # sensoring_radius
            f'{speed} m/s'          # speed
        ],
        'r_min': [
            f'{cost:.2f} USD', # cost
            f'{t} rad'         # angular_actuation_error_budget
        ]
    }

# Write to YAML file
with open("coverage_blind_robot.mcdplib/robot_catalog.yaml", "w") as f:
    yaml.dump(catalog, f, default_flow_style=False, sort_keys=False)