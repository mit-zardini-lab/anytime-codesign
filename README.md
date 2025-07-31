# Bug with calculating the implementations in the solver

When running the command

```bash
mcdp-solve-query system_query --nocache --imp
```

we get the following Pareto front: `↑{⟨40 USD,1390.97 s⟩, ⟨60 USD,24.6716 s⟩, ⟨70 USD,24.6679 s⟩}`, which is correct. However, looking at the implementations realizing each point on the Pareto front, we see that each point is realized by `robot_0`, which is impossible, as the robots available (`robot.mcdp`) look like this:

```plaintext
# robot.mcdp
dp {
  provides physical_radius [m]
  provides sensoring_radius [m]
  provides speed [m/s]

  requires cost [USD]
  requires angular_actuation_error_budget [rad]

  implemented-by yaml resource("robot_catalog.yaml")
}
```

```yaml
# robot_catalog.yaml
F:
- m
- m
- m/s
R:
- USD
- rad
implementations:
  robot_0:
    f_max:
    - 0.5 m
    - 0.5 m
    - 0.5 m/s
    r_min:
    - 70.00 USD
    - 0.01 rad
  robot_1:
    f_max:
    - 1.0 m
    - 1.0 m
    - 0.5 m/s
    r_min:
    - 120.00 USD
    - 0.01 rad
  robot_2:
    f_max:
    - 1.5 m
    - 1.5 m
    - 0.5 m/s
    r_min:
    - 170.00 USD
    - 0.01 rad
  robot_3:
    f_max:
    - 0.5 m
    - 0.5 m
    - 0.5 m/s
    r_min:
    - 60.00 USD
    - 0.02 rad
  robot_4:
    f_max:
    - 1.0 m
    - 1.0 m
    - 0.5 m/s
    r_min:
    - 110.00 USD
    - 0.02 rad
  robot_5:
    f_max:
    - 1.5 m
    - 1.5 m
    - 0.5 m/s
    r_min:
    - 160.00 USD
    - 0.02 rad
  robot_6:
    f_max:
    - 0.5 m
    - 0.5 m
    - 0.5 m/s
    r_min:
    - 50.00 USD
    - 0.03 rad
  robot_7:
    f_max:
    - 1.0 m
    - 1.0 m
    - 0.5 m/s
    r_min:
    - 100.00 USD
    - 0.03 rad
  robot_8:
    f_max:
    - 1.5 m
    - 1.5 m
    - 0.5 m/s
    r_min:
    - 150.00 USD
    - 0.03 rad
  robot_9:
    f_max:
    - 0.5 m
    - 0.5 m
    - 0.5 m/s
    r_min:
    - 40.00 USD
    - 0.04 rad
  robot_10:
    f_max:
    - 1.0 m
    - 1.0 m
    - 0.5 m/s
    r_min:
    - 90.00 USD
    - 0.04 rad
  robot_11:
    f_max:
    - 1.5 m
    - 1.5 m
    - 0.5 m/s
    r_min:
    - 140.00 USD
    - 0.04 rad
```

That is, the correct implementations are:

* `⟨40 USD,1390.97 s⟩`: `robot_9`
* `⟨60 USD,24.6716 s⟩`: `robot_3`
* `⟨70 USD,24.6679 s⟩`: `robot_0`

We think that this is related to a bug in the mcdp solver. Interestingly, going back in the history of docker images, we discovered the following:

* `20250715`: bug still there
* `20250708`: bug still there
* `20250622`: bug still there
* `20250419`: bug still there
* `20241204`: bug still there
* `20241106`: no bug

So it seems the bug was introduced from version `20241106` to version `20241204`. We recall a discussion with Gioele, in which he mentioned that around late 2024 (circa 2024-10 to 2024-11), a bug related to displaying the correct implementation for the Ferrari project has been fixed - maybe the bug was introduced during that update.