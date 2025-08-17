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

# Another bug related to implementations

Another bug we became aware of regards no display of implementations at all. We built a very simple setup to demonstrate the bug. The following catalog is given (`test_cat.mcdp`):

```plaintext
# test_cat.mcdp
catalog {
    provides area [m^2]
    requires cost [USD]

    12 m^2 <-| imp1 |-> 10 USD
    14 m^2 <-| imp2 |-> 10 USD
}
```

When running the following query (`working_cat_query.mcdp_query.yaml`):

```yaml
title: Query query_fleet_designer_000
description: ''
model: '`test_cat'
query:
  query_type: FixFunMinRes
  max_r:
    cost: "100 USD"
  min_f:
    area: "12 m^2"
  optimize_for:
  - cost
```

we get the expected result (`working_output.yaml`) which also shows that `imp1` is the optimal implementation:

```yaml
optimistic:
  minimals: frozenset({(Decimal('10.000000000'),)})
  pretty: ↑{⟨10 USD⟩}
  imps:
    pretty: '↑{⟨10 USD⟩: imp1}'
pessimistic:
  minimals: frozenset({(Decimal('10.000000000'),)})
  pretty: ↑{⟨10 USD⟩}
  imps:
    pretty: '↑{⟨10 USD⟩: imp1}'
```

However, when running the query asking for 14 m^2 as functionality (`bug_cat_query.mcdp_query.yaml`):

```yaml
title: Query query_fleet_designer_000
description: ''
model: '`test_cat'
query:
  query_type: FixFunMinRes
  max_r:
    cost: "100 USD"
  min_f:
    area: "14 m^2"
  optimize_for:
  - cost
```

we get the following result (`bug_output.yaml`):

```yaml
optimistic:
  minimals: frozenset({(Decimal('10.000000000'),)})
  pretty: ↑{⟨10 USD⟩}
  imps:
    pretty: '↑{⟨10 USD⟩: ⟨·,⟨10ᵒᵖ⟩⟩ ⟨⟨⟨⟩,⟨USD⟩⟩⟩}'
pessimistic:
  minimals: frozenset({(Decimal('10.000000000'),)})
  pretty: ↑{⟨10 USD⟩}
  imps:
    pretty: '↑{⟨10 USD⟩: ⟨·,⟨10ᵒᵖ⟩⟩ ⟨⟨⟨⟩,⟨USD⟩⟩⟩}'
```

Hence, we see that it is possible to get 14 m^2 of coverage for 10 USD, but there are no implementations displayed (it should be `imp2`).

Similiar to above, we tested the queries also for version `20241106` of the mcdp solver. However, this bug is also present in that version (the only difference is that in the working example `imp2` is shown as optimal, which is also correct as both `imp1` and `imp2` have the same cost).

## Remarks
The problem also persists when instead of using `catalog {}`, we implement the catalog in a separate `yaml` file (see `test_cat_yaml.mcdp`).

Interestingly, when instead of using the `yaml representation` of the query:

```bash
mcdp-solve-query bug_cat_query --nocache --imp
```

we use `mcdp-solve`:

```bash
mcdp-solve test_cat "12 m^2" --nocache --imp
mcdp-solve test_cat "14 m^2" --nocache --imp
```

the error no longer exists. The results for the first query is:

```yaml
optimistic:
  minimals: frozenset({(Decimal('10.000000000'),)})
  pretty: ↑{⟨10 USD⟩}
  all_solutions:
  - r: ⟨10 USD⟩
    assignment:
      functionality: {}
      resources: {}
      b: imp1
      sub: {}
pessimistic:
  minimals: frozenset({(Decimal('10.000000000'),)})
  pretty: ↑{⟨10 USD⟩}
  all_solutions:
  - r: ⟨10 USD⟩
    assignment:
      functionality: {}
      resources: {}
      b: imp1
      sub: {}

```

and the result for the second query is:

```yaml
optimistic:
  minimals: frozenset({(Decimal('10.000000000'),)})
  pretty: ↑{⟨10 USD⟩}
  all_solutions:
  - r: ⟨10 USD⟩
    assignment:
      functionality: {}
      resources: {}
      b: imp2
      sub: {}
pessimistic:
  minimals: frozenset({(Decimal('10.000000000'),)})
  pretty: ↑{⟨10 USD⟩}
  all_solutions:
  - r: ⟨10 USD⟩
    assignment:
      functionality: {}
      resources: {}
      b: imp2
      sub: {}
```

**Note:** It is also interesting to note, that the output prints are different (entry wise) when running `mcdp-solve-query` and `mcdp-solve`, respectively.