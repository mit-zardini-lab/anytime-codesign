import itertools

theta_max = ['0.02','0.04']
radius = ['0.5', '1.0', '1.5']

lines = []
lines.append("mcdp {")
lines.append("  provides physical_radius [m]")
lines.append("  provides sensoring_radius [m]")
lines.append("  provides speed [m/s]")
lines.append("")
lines.append("  requires cost [USD]")
lines.append("  requires angular_actuation_error_budget [rad]")
lines.append("")

for i, (t, r) in enumerate(itertools.product(theta_max, radius)):
    t_val = float(t)
    r_val = float(r)
    cost = r_val * 100 - t_val * 1000 + 30
    line = f"  {r} m, {r} m, 0.5 m/s <--| robot_{i} |--> {cost:.2f} USD, {t} rad"
    lines.append(line)

lines.append("}")

# Write to file
with open("coverage_blind_robot.mcdplib/robot.mcdp", "w") as f:
    f.write("\n".join(lines))