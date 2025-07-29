# Bug with calculating the implementations in the solver

When running the command

```bash
mcdp-solve-query system_query --nocache --imp
```

we get the following Pareto front: `↑{⟨40 USD,1390.97 s⟩, ⟨60 USD,24.6716 s⟩, ⟨70 USD,24.6679 s⟩}`, which is correct. However, looking at the implementations realizing each point on the Pareto front, we see that each point is realized by `robot_0`, which is impossible, as the robots available (`robot.mcdp`) look like this:

```plaintext
catalog {
  provides physical_radius [m]
  provides sensoring_radius [m]
  provides speed [m/s]

  requires cost [USD]
  requires angular_actuation_error_budget [rad]

  0.5 m, 0.5 m, 0.5 m/s <--| robot_0 |--> 70.00 USD, 0.01 rad
  1.0 m, 1.0 m, 0.5 m/s <--| robot_1 |--> 120.00 USD, 0.01 rad
  1.5 m, 1.5 m, 0.5 m/s <--| robot_2 |--> 170.00 USD, 0.01 rad
  0.5 m, 0.5 m, 0.5 m/s <--| robot_3 |--> 60.00 USD, 0.02 rad
  1.0 m, 1.0 m, 0.5 m/s <--| robot_4 |--> 110.00 USD, 0.02 rad
  1.5 m, 1.5 m, 0.5 m/s <--| robot_5 |--> 160.00 USD, 0.02 rad
  0.5 m, 0.5 m, 0.5 m/s <--| robot_6 |--> 50.00 USD, 0.03 rad
  1.0 m, 1.0 m, 0.5 m/s <--| robot_7 |--> 100.00 USD, 0.03 rad
  1.5 m, 1.5 m, 0.5 m/s <--| robot_8 |--> 150.00 USD, 0.03 rad
  0.5 m, 0.5 m, 0.5 m/s <--| robot_9 |--> 40.00 USD, 0.04 rad
  1.0 m, 1.0 m, 0.5 m/s <--| robot_10 |--> 90.00 USD, 0.04 rad
  1.5 m, 1.5 m, 0.5 m/s <--| robot_11 |--> 140.00 USD, 0.04 rad
}
```

That is, the correct implementations are:

* `⟨40 USD,1390.97 s⟩`: `robot_9`
* `⟨60 USD,24.6716 s⟩`: `robot_3`
* `⟨70 USD,24.6679 s⟩`: `robot_0`

We think that this is related to a bug in the mcdp solver.