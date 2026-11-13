# Native run inventory — 2026-10-26

51 existing native runs; 25 full JSON results retained and 26 exploratory JSON results kept locally.

This is a transcription, not a new recommendation. The JSON companion retains exact numeric values, input/result SHA-256, native warnings, stat snapshots and original validation references.

Requested iterations, engine-reported iterations and effective samples are different fields. Short smoke, static and export-reimport runs are not DPS ranking evidence. CI is the 95% half-width of each native mean; acceptance comes from existing validation only.

| Run / original input stem | Kind | Requested | Reported | Samples | Seed | DPS | CI95 ± | Accepted | Full JSON |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `gear-compat341-raid-current` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 214749.125 | 155.611 | true | retained |
| `gear-compat341-raid-elite_full` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 218280.073 | 159.635 | true | retained |
| `gear-compat341-raid-literal-current` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 214693.597 | 154.912 | true | retained |
| `gear-compat341-raid-raid_ring_334` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 214675.902 | 154.562 | true | retained |
| `gear-compat341-raid-waist_331_cm` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 215617.718 | 158.174 | true | retained |
| `gear-compat341-slice-current` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 302151.604 | 354.449 | true | retained |
| `gear-compat341-slice-elite_full` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 308707.247 | 359.525 | true | retained |
| `gear-compat341-slice-literal-current` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 303341.692 | 355.300 | true | retained |
| `gear-compat341-slice-raid_ring_334` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 304309.311 | 353.001 | true | retained |
| `gear-compat341-slice-waist_331_cm` | final_or_control | 6000 | 6007 | 5999 | 2610202631 | 304988.706 | 358.371 | true | retained |
| `gear-compat341-smoke-raid-current` | screen_or_smoke | 40 | 47 | 39 | 2610202631 | 213980.996 | 2013.670 | true | local only |
| `gear-compat341-smoke-slice-current` | screen_or_smoke | 40 | 47 | 39 | 2610202631 | 303015.760 | 4533.747 | true | local only |
| `gear-compat341-unbuffed-current` | static_snapshot | 40 | 47 | 39 | 2610202631 | 158900.298 | 1197.900 | true | retained |
| `gear-compat341-unbuffed-elite_full` | static_snapshot | 40 | 47 | 39 | 2610202631 | 160592.097 | 1568.634 | true | retained |
| `gear-compat341-unbuffed-literal-current` | static_snapshot | 40 | 47 | 39 | 2610202631 | 157506.266 | 1462.960 | true | retained |
| `gear-elite-smoke-raid` | screen_or_smoke | 40 | 47 | 39 | 2610202603 | 218607.489 | 2139.443 | true | local only |
| `gear-elite-smoke-slice` | screen_or_smoke | 40 | 47 | 39 | 2610202603 | 308183.506 | 4097.638 | true | local only |
| `gear-elite-unbuffed` | static_snapshot | 40 | 47 | 39 | 2610202603 | 160677.394 | 1290.418 | true | retained |
| `gear-screen-literal-raid-current` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 214012.382 | 202.403 | true | local only |
| `gear-screen-literal-slice-current` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 301622.248 | 457.595 | true | local only |
| `gear-screen-raid-all_crafts_hm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 211810.152 | 196.755 | true | local only |
| `gear-screen-raid-cloak_hm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 213684.140 | 198.910 | true | local only |
| `gear-screen-raid-current` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 213921.873 | 201.428 | true | local only |
| `gear-screen-raid-elite_full` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 217066.301 | 208.918 | true | local only |
| `gear-screen-raid-one_gem_hm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 213664.103 | 200.386 | true | local only |
| `gear-screen-raid-raid_ring_334` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 213541.349 | 200.844 | true | local only |
| `gear-screen-raid-ring_hm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 213080.965 | 202.282 | true | local only |
| `gear-screen-raid-waist_331_cm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 214744.669 | 204.297 | true | local only |
| `gear-screen-slice-all_crafts_hm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 298291.287 | 460.074 | true | local only |
| `gear-screen-slice-cloak_hm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 301537.965 | 466.070 | true | local only |
| `gear-screen-slice-current` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 300773.105 | 469.908 | true | local only |
| `gear-screen-slice-elite_full` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 307332.671 | 472.008 | true | local only |
| `gear-screen-slice-one_gem_hm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 301115.865 | 456.876 | true | local only |
| `gear-screen-slice-raid_ring_334` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 303236.407 | 457.909 | true | local only |
| `gear-screen-slice-ring_hm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 299352.686 | 457.126 | true | local only |
| `gear-screen-slice-waist_331_cm` | screen_or_smoke | 3500 | 3507 | 3499 | 2610202611 | 303443.334 | 471.049 | true | local only |
| `gear-smoke-aoe` | screen_or_smoke | 40 | 47 | 39 | 2610202602 | 687403.378 | 6981.674 | true | local only |
| `gear-smoke-raid` | screen_or_smoke | 40 | 47 | 39 | 2610202602 | 212285.110 | 1801.769 | true | local only |
| `gear-smoke-raw` | screen_or_smoke | 30 | 37 | 29 | 2610202601 | 156853.347 | 1818.734 | true | local only |
| `gear-smoke-slice` | screen_or_smoke | 40 | 47 | 39 | 2610202602 | 303200.464 | 4018.908 | true | local only |
| `gear-talents-raid-bisset` | final_or_control | 3500 | 3507 | 3499 | 2610202641 | 220540.003 | 201.575 | true | retained |
| `gear-talents-raid-user` | final_or_control | 3500 | 3507 | 3499 | 2610202641 | 214886.770 | 203.732 | true | retained |
| `gear-talents-slice-bisset` | final_or_control | 3500 | 3507 | 3499 | 2610202641 | 312138.897 | 478.891 | true | retained |
| `gear-talents-slice-user` | final_or_control | 3500 | 3507 | 3499 | 2610202641 | 302459.517 | 462.903 | true | retained |
| `gear-unbuffed` | static_snapshot | 40 | 47 | 39 | 2610202602 | 155730.055 | 1494.840 | true | retained |
| `gear-verify-raid-current` | final_or_control | 6000 | 6007 | 5999 | 2610202621 | 213885.594 | 152.144 | true | retained |
| `gear-verify-raid-raid_ring_334` | final_or_control | 6000 | 6007 | 5999 | 2610202621 | 213824.756 | 156.548 | true | retained |
| `gear-verify-raid-waist_331_cm` | final_or_control | 6000 | 6007 | 5999 | 2610202621 | 214923.008 | 154.325 | true | retained |
| `gear-verify-slice-current` | final_or_control | 6000 | 6007 | 5999 | 2610202621 | 301146.412 | 359.007 | true | retained |
| `gear-verify-slice-raid_ring_334` | final_or_control | 6000 | 6007 | 5999 | 2610202621 | 303274.479 | 353.353 | true | retained |
| `gear-verify-slice-waist_331_cm` | final_or_control | 6000 | 6007 | 5999 | 2610202621 | 303602.024 | 357.435 | true | retained |
