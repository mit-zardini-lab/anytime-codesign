import itertools
import yaml

theta_max = ['0.01','0.02','0.03','0.04']
radius = ['0.5', '1.0', '1.5']

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
for i, (t, r) in enumerate(itertools.product(theta_max, radius)):
    t_val = float(t)
    r_val = float(r)
    cost = r_val * 100 - t_val * 1000 + 30
    
    impl_name = f"robot_{i}"
    
    catalog['implementations'][impl_name] = {
        'f_max': [
            f'{r} m',    # physical_radius
            f'{r} m',    # sensoring_radius  
            '0.5 m/s'    # speed
        ],
        'r_min': [
            f'{cost:.2f} USD', # cost
            f'{t} rad'         # angular_actuation_error_budget
        ]
    }

# Write to YAML file
with open("coverage_blind_robot.mcdplib/robot_catalog.yaml", "w") as f:
    yaml.dump(catalog, f, default_flow_style=False, sort_keys=False)