# Native run inventory — 2026-10-29

372 existing native runs; 154 full JSON results retained and 218 exploratory JSON results kept locally.

This is a transcription, not a new recommendation. The JSON companion retains exact numeric values, input/result SHA-256, native warnings, stat snapshots and original validation references.

Requested iterations, engine-reported iterations and effective samples are different fields. Short smoke, static and export-reimport runs are not DPS ranking evidence. CI is the 95% half-width of each native mean; acceptance comes from existing validation only.

| Run / original input stem | Kind | Requested | Reported | Samples | Seed | DPS | CI95 ± | Accepted | Full JSON |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `aoe-cloak_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 699527.334 | 766.601 | true | local only |
| `aoe-current-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 700346.435 | 785.277 | true | local only |
| `aoe-current-40-26102901` | screen_or_smoke | 40 | 47 | 39 | 26102901 | 704329.625 | 5391.343 | true | local only |
| `aoe-flask_crit-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 700645.767 | 817.216 | true | local only |
| `aoe-flask_haste-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 696681.820 | 838.427 | true | local only |
| `aoe-gems_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 699602.946 | 800.269 | true | local only |
| `aoe-glove_art-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 700331.013 | 785.097 | true | local only |
| `aoe-glove_cm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 702150.069 | 763.592 | true | local only |
| `aoe-legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 706686.224 | 784.998 | true | local only |
| `aoe-shoulder324-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 701588.576 | 778.529 | true | local only |
| `aoe-shoulder334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 704470.868 | 795.792 | true | local only |
| `aoe-waist_cm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 705259.609 | 745.171 | true | local only |
| `aoe-waist_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 704826.734 | 776.080 | true | local only |
| `craft-placement-aoe-armor334_owned-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 715901.946 | 554.415 | true | retained |
| `craft-placement-aoe-armor334_raidcloak-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 714254.618 | 561.145 | true | retained |
| `craft-placement-aoe-shoulder334_belt331-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 712173.093 | 561.980 | true | retained |
| `craft-placement-aoe-shoulder334_owned-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 705678.197 | 581.675 | true | retained |
| `craft-placement-aoe-shoulder334_raidcloak-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 707676.669 | 553.903 | true | retained |
| `craft-placement-slice-armor334_owned-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 312839.572 | 365.350 | true | retained |
| `craft-placement-slice-armor334_raidcloak-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 313596.018 | 367.477 | true | retained |
| `craft-placement-slice-shoulder334_belt331-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 310384.952 | 355.886 | true | retained |
| `craft-placement-slice-shoulder334_owned-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 307640.475 | 364.361 | true | retained |
| `craft-placement-slice-shoulder334_raidcloak-6000-26102991` | final_or_control | 6000 | 6007 | 5999 | 26102991 | 308895.362 | 356.406 | true | retained |
| `literal-stats-current-40-26102901` | static_snapshot | 40 | 47 | 39 | 26102901 | 160864.629 | 1505.611 | true | retained |
| `native70575-aoe-current-40-26102901` | screen_or_smoke | 40 | 47 | 39 | 26102901 | 703399.381 | 5680.234 | true | local only |
| `native70575-aoe-current-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 700508.191 | 507.495 | true | retained |
| `native70575-aoe-delve_craft_now-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 713738.827 | 789.013 | true | local only |
| `native70575-aoe-delve_legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 702857.967 | 790.792 | true | local only |
| `native70575-aoe-delve_legs334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 702568.336 | 520.455 | true | retained |
| `native70575-aoe-delve_shoulder321-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 702834.241 | 824.600 | true | local only |
| `native70575-aoe-delve_shoulder334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 706020.390 | 815.705 | true | local only |
| `native70575-aoe-delve_shoulder334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 705827.400 | 544.676 | true | retained |
| `native70575-aoe-flask_crit-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 700752.036 | 543.685 | true | retained |
| `native70575-aoe-flask_haste-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 696372.777 | 552.616 | true | retained |
| `native70575-aoe-gems_hm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 698750.432 | 518.990 | true | retained |
| `native70575-aoe-glove_cm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 702185.268 | 501.916 | true | retained |
| `native70575-aoe-h7_legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 703409.898 | 785.426 | true | local only |
| `native70575-aoe-h7_waist334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 704249.954 | 765.718 | true | local only |
| `native70575-aoe-legs334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 706160.882 | 511.755 | true | retained |
| `native70575-aoe-post_both-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 707164.358 | 515.112 | true | retained |
| `native70575-aoe-post_both_raid_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 716330.235 | 515.475 | true | retained |
| `native70575-aoe-post_both_ring-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 703802.634 | 514.632 | true | retained |
| `native70575-aoe-post_both_ring_272147_socket-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 700275.816 | 857.948 | true | local only |
| `native70575-aoe-post_both_ring_272148_socket-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 703830.560 | 818.957 | true | local only |
| `native70575-aoe-post_both_ring_272150_socket-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 701490.038 | 799.822 | true | local only |
| `native70575-aoe-post_both_ring_socket-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 706587.461 | 507.258 | true | retained |
| `native70575-aoe-post_both_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 714616.591 | 524.826 | true | retained |
| `native70575-aoe-post_legs-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 702915.814 | 513.528 | true | retained |
| `native70575-aoe-post_legs_ring-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 699417.548 | 508.840 | true | retained |
| `native70575-aoe-post_legs_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 709373.614 | 531.372 | true | retained |
| `native70575-aoe-post_waist-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 705503.457 | 510.336 | true | retained |
| `native70575-aoe-post_waist_legs-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 707602.895 | 511.311 | true | retained |
| `native70575-aoe-post_waist_ring-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 701806.595 | 501.924 | true | retained |
| `native70575-aoe-post_waist_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 711659.419 | 527.423 | true | retained |
| `native70575-aoe-route-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 745940.098 | 832.125 | true | local only |
| `native70575-aoe-route-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 745607.120 | 559.564 | true | retained |
| `native70575-aoe-route_craft_waist-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 745652.355 | 853.620 | true | local only |
| `native70575-aoe-route_craft_waist-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 747596.131 | 543.457 | true | retained |
| `native70575-aoe-route_crit_flask-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 745298.083 | 861.764 | true | local only |
| `native70575-aoe-route_haste_flask-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 742386.078 | 929.221 | true | local only |
| `native70575-aoe-route_haste_gems-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 745607.145 | 851.946 | true | local only |
| `native70575-aoe-route_raid_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 747501.478 | 542.108 | true | retained |
| `native70575-aoe-shoulder334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 704229.748 | 512.242 | true | retained |
| `native70575-aoe-tendril334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 727459.745 | 841.134 | true | local only |
| `native70575-aoe-tendril334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 726371.387 | 530.128 | true | retained |
| `native70575-aoe-tendril341-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 730434.565 | 827.548 | true | local only |
| `native70575-aoe-tendril341-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 730050.469 | 530.573 | true | retained |
| `native70575-aoe-tendril341_no_heart-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 704202.948 | 771.953 | true | local only |
| `native70575-aoe-waist_cm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 706943.253 | 500.928 | true | retained |
| `native70575-literal-stats-current-40-26102901` | static_snapshot | 40 | 47 | 39 | 26102901 | 160731.766 | 1493.879 | true | retained |
| `native70575-slice-current-40-26102901` | screen_or_smoke | 40 | 47 | 39 | 26102901 | 302648.637 | 4819.628 | true | local only |
| `native70575-slice-current-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 306458.299 | 330.690 | true | retained |
| `native70575-slice-delve_craft_now-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 310373.301 | 505.559 | true | local only |
| `native70575-slice-delve_legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 308463.988 | 506.212 | true | local only |
| `native70575-slice-delve_legs334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 308465.680 | 332.570 | true | retained |
| `native70575-slice-delve_shoulder321-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 306006.220 | 490.763 | true | local only |
| `native70575-slice-delve_shoulder334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 307974.453 | 497.640 | true | local only |
| `native70575-slice-delve_shoulder334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 307642.418 | 329.317 | true | retained |
| `native70575-slice-flask_crit-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 303721.918 | 327.954 | true | retained |
| `native70575-slice-flask_haste-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 302863.545 | 325.189 | true | retained |
| `native70575-slice-gems_hm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 305870.764 | 332.765 | true | retained |
| `native70575-slice-glove_cm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 306739.617 | 335.560 | true | retained |
| `native70575-slice-h7_legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 308804.668 | 515.678 | true | local only |
| `native70575-slice-h7_waist334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 309117.623 | 510.269 | true | local only |
| `native70575-slice-legs334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 308748.451 | 333.798 | true | retained |
| `native70575-slice-post_both-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 311163.870 | 341.350 | true | retained |
| `native70575-slice-post_both_raid_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 313609.057 | 344.204 | true | retained |
| `native70575-slice-post_both_ring-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 310573.352 | 332.883 | true | retained |
| `native70575-slice-post_both_ring_272147_socket-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 307970.127 | 505.650 | true | local only |
| `native70575-slice-post_both_ring_272148_socket-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 309394.799 | 499.594 | true | local only |
| `native70575-slice-post_both_ring_272150_socket-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 310335.023 | 507.713 | true | local only |
| `native70575-slice-post_both_ring_socket-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 311629.068 | 332.144 | true | retained |
| `native70575-slice-post_both_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 312811.077 | 341.545 | true | retained |
| `native70575-slice-post_legs-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 308679.191 | 330.752 | true | retained |
| `native70575-slice-post_legs_ring-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 308285.320 | 329.194 | true | retained |
| `native70575-slice-post_legs_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 309726.675 | 332.611 | true | retained |
| `native70575-slice-post_waist-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 308713.518 | 333.116 | true | retained |
| `native70575-slice-post_waist_legs-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 310927.865 | 339.320 | true | retained |
| `native70575-slice-post_waist_ring-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 308810.389 | 335.645 | true | retained |
| `native70575-slice-post_waist_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 310750.810 | 329.955 | true | retained |
| `native70575-slice-route-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 323382.722 | 549.483 | true | local only |
| `native70575-slice-route-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 324013.194 | 362.265 | true | retained |
| `native70575-slice-route_craft_waist-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 323387.018 | 551.167 | true | local only |
| `native70575-slice-route_craft_waist-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 323168.583 | 360.897 | true | retained |
| `native70575-slice-route_crit_flask-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 320113.661 | 547.042 | true | local only |
| `native70575-slice-route_haste_flask-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 320071.782 | 541.575 | true | local only |
| `native70575-slice-route_haste_gems-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 323592.970 | 553.740 | true | local only |
| `native70575-slice-route_raid_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 324913.642 | 362.499 | true | retained |
| `native70575-slice-shoulder334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 308275.241 | 331.497 | true | retained |
| `native70575-slice-tendril334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 314104.684 | 543.029 | true | local only |
| `native70575-slice-tendril334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 314725.577 | 350.925 | true | retained |
| `native70575-slice-tendril341-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 315760.165 | 537.666 | true | local only |
| `native70575-slice-tendril341-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 316382.578 | 359.858 | true | retained |
| `native70575-slice-tendril341_no_heart-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 306646.912 | 512.496 | true | local only |
| `native70575-slice-waist_cm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 308648.117 | 333.275 | true | retained |
| `native70575-st-current-40-26102901` | screen_or_smoke | 40 | 47 | 39 | 26102901 | 177642.161 | 1833.055 | true | local only |
| `native70575-st-current-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 177586.482 | 117.358 | true | retained |
| `native70575-st-delve_craft_now-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 180037.355 | 178.389 | true | local only |
| `native70575-st-delve_legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178534.153 | 174.838 | true | local only |
| `native70575-st-delve_shoulder321-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177652.445 | 173.408 | true | local only |
| `native70575-st-delve_shoulder334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178718.464 | 171.577 | true | local only |
| `native70575-st-flask_crit-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 177333.716 | 113.820 | true | retained |
| `native70575-st-flask_haste-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 176723.846 | 114.290 | true | retained |
| `native70575-st-gems_hm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 177447.496 | 116.110 | true | retained |
| `native70575-st-glove_cm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 177801.213 | 117.425 | true | retained |
| `native70575-st-h7_legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178516.670 | 176.534 | true | local only |
| `native70575-st-h7_waist334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178745.458 | 176.733 | true | local only |
| `native70575-st-legs334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 178941.608 | 117.800 | true | retained |
| `native70575-st-post_both_raid_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 181187.828 | 118.959 | true | retained |
| `native70575-st-route-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178818.922 | 171.433 | true | local only |
| `native70575-st-route-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 178956.825 | 111.628 | true | retained |
| `native70575-st-route_craft_waist-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178895.733 | 167.990 | true | local only |
| `native70575-st-route_craft_waist-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 178781.703 | 110.060 | true | retained |
| `native70575-st-route_crit_flask-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178437.291 | 163.031 | true | local only |
| `native70575-st-route_haste_flask-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177468.990 | 173.122 | true | local only |
| `native70575-st-route_haste_gems-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178652.244 | 168.348 | true | local only |
| `native70575-st-route_raid_shoulder-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 179071.270 | 112.901 | true | retained |
| `native70575-st-shoulder334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 178544.406 | 118.543 | true | retained |
| `native70575-st-tendril334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 174522.259 | 163.885 | true | local only |
| `native70575-st-tendril334-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 174449.136 | 109.108 | true | retained |
| `native70575-st-tendril341-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 175159.037 | 164.961 | true | local only |
| `native70575-st-tendril341-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 175129.615 | 109.266 | true | retained |
| `native70575-st-tendril341_no_heart-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 172894.178 | 168.113 | true | local only |
| `native70575-st-waist_cm-7000-26102921` | final_or_control | 7000 | 7007 | 6999 | 26102921 | 178681.448 | 118.520 | true | retained |
| `native70575-stats-current-40-26102901` | static_snapshot | 40 | 47 | 39 | 26102901 | 159824.766 | 1560.195 | true | retained |
| `native70575-stats-post_both_shoulder-40-26102931` | static_snapshot | 40 | 47 | 39 | 26102931 | 161935.119 | 1520.442 | true | retained |
| `native70575-stats-route-40-26102931` | static_snapshot | 40 | 47 | 39 | 26102931 | 160455.322 | 1401.301 | true | retained |
| `slice-cloak_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 306977.216 | 493.574 | true | local only |
| `slice-current-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 306628.964 | 510.798 | true | local only |
| `slice-current-40-26102901` | screen_or_smoke | 40 | 47 | 39 | 26102901 | 302858.497 | 4818.357 | true | local only |
| `slice-flask_crit-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 303593.064 | 498.272 | true | local only |
| `slice-flask_haste-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 303087.496 | 494.865 | true | local only |
| `slice-gems_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 305985.172 | 502.855 | true | local only |
| `slice-glove_art-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 306618.747 | 510.764 | true | local only |
| `slice-glove_cm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 306933.378 | 510.301 | true | local only |
| `slice-legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 308171.659 | 517.598 | true | local only |
| `slice-shoulder324-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 306343.512 | 508.114 | true | local only |
| `slice-shoulder334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 308322.919 | 510.979 | true | local only |
| `slice-waist_cm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 308851.270 | 513.148 | true | local only |
| `slice-waist_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 308090.091 | 498.038 | true | local only |
| `st-cloak_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177842.149 | 180.397 | true | local only |
| `st-current-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177622.581 | 174.797 | true | local only |
| `st-current-40-26102901` | screen_or_smoke | 40 | 47 | 39 | 26102901 | 177636.586 | 1834.258 | true | local only |
| `st-flask_crit-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177439.869 | 176.827 | true | local only |
| `st-flask_haste-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 176773.180 | 173.451 | true | local only |
| `st-gems_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177427.765 | 178.102 | true | local only |
| `st-glove_art-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177605.299 | 175.017 | true | local only |
| `st-glove_cm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177851.290 | 178.204 | true | local only |
| `st-legs334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178842.902 | 181.575 | true | local only |
| `st-shoulder324-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 177820.137 | 174.967 | true | local only |
| `st-shoulder334-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178657.929 | 182.319 | true | local only |
| `st-waist_cm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178733.926 | 182.864 | true | local only |
| `st-waist_hm-3000-26102911` | screen_or_smoke | 3000 | 3007 | 2999 | 26102911 | 178410.274 | 180.349 | true | local only |
| `stats-current-40-26102901` | final_or_control | 40 | 47 | 39 | 26102901 | 159788.818 | 1564.707 | true | retained |
| `talents-tendril-aoe-bisset_1026-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 775875.670 | 471.677 | true | retained |
| `talents-tendril-aoe-bisset_1026-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 775482.938 | 844.591 | true | local only |
| `talents-tendril-aoe-icy_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 746321.788 | 832.330 | true | local only |
| `talents-tendril-aoe-local_guide_aoe-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 776498.845 | 822.026 | true | local only |
| `talents-tendril-aoe-method_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 740255.394 | 876.862 | true | local only |
| `talents-tendril-aoe-user-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 746841.182 | 460.867 | true | retained |
| `talents-tendril-aoe-user-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 746541.721 | 819.340 | true | local only |
| `talents-tendril-aoe-user_short_cd-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 777839.751 | 448.117 | true | retained |
| `talents-tendril-aoe-user_short_cd-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 776774.032 | 821.875 | true | local only |
| `talents-tendril-aoe-user_short_cd_martial-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 775899.453 | 471.160 | true | retained |
| `talents-tendril-aoe-user_short_cd_martial-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 775633.183 | 846.709 | true | local only |
| `talents-tendril-aoe-user_short_cd_martial-craft_cm_pair_mastery_gems-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 776267.808 | 458.271 | true | retained |
| `talents-tendril-slice-bisset_1026-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 334623.899 | 313.199 | true | retained |
| `talents-tendril-slice-bisset_1026-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 334236.265 | 567.336 | true | local only |
| `talents-tendril-slice-icy_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 324360.833 | 544.484 | true | local only |
| `talents-tendril-slice-local_guide_aoe-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 333184.045 | 566.282 | true | local only |
| `talents-tendril-slice-method_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 325071.210 | 556.941 | true | local only |
| `talents-tendril-slice-user-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 324120.148 | 302.949 | true | retained |
| `talents-tendril-slice-user-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 323891.954 | 557.815 | true | local only |
| `talents-tendril-slice-user_short_cd-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 333282.505 | 310.334 | true | retained |
| `talents-tendril-slice-user_short_cd-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 333461.704 | 566.398 | true | local only |
| `talents-tendril-slice-user_short_cd_martial-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 334611.964 | 313.054 | true | retained |
| `talents-tendril-slice-user_short_cd_martial-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 334230.961 | 565.837 | true | local only |
| `talents-tendril-slice-user_short_cd_martial-craft_cm_pair_mastery_gems-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 335302.622 | 316.290 | true | retained |
| `talents-tendril-slice-user_short_cd_martial-craft_cm_pair_mastery_gems-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 335342.416 | 566.590 | true | local only |
| `talents-tendril-slice-user_short_cd_martial-flask_crit-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 330961.640 | 566.228 | true | local only |
| `talents-tendril-slice-user_short_cd_martial-flask_haste-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 330354.466 | 559.102 | true | local only |
| `talents-tendril-slice-user_short_cd_martial-gems_240898-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 334860.056 | 556.973 | true | local only |
| `talents-tendril-slice-user_short_cd_martial-rings_advanced_mastery-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 328608.716 | 560.839 | true | local only |
| `talents-tendril-st-bisset_1026-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 182803.150 | 96.470 | true | retained |
| `talents-tendril-st-bisset_1026-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 182818.435 | 175.771 | true | local only |
| `talents-tendril-st-icy_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 178746.348 | 168.850 | true | local only |
| `talents-tendril-st-local_guide_aoe-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 178061.402 | 168.865 | true | local only |
| `talents-tendril-st-method_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 183634.233 | 177.871 | true | local only |
| `talents-tendril-st-user-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 178928.346 | 92.899 | true | retained |
| `talents-tendril-st-user-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 178722.501 | 171.843 | true | local only |
| `talents-tendril-st-user_short_cd-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 178334.490 | 93.543 | true | retained |
| `talents-tendril-st-user_short_cd-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 178318.886 | 169.364 | true | local only |
| `talents-tendril-st-user_short_cd_martial-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 182810.644 | 96.473 | true | retained |
| `talents-tendril-st-user_short_cd_martial-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 182822.449 | 175.837 | true | local only |
| `talents-tendril-st-user_short_cd_martial-craft_cm_pair_mastery_gems-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 182707.987 | 97.968 | true | retained |
| `talents-zuljin-aoe-bisset_1026-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 743493.789 | 447.286 | true | retained |
| `talents-zuljin-aoe-bisset_1026-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 743366.471 | 839.614 | true | local only |
| `talents-zuljin-aoe-icy_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 714587.629 | 811.682 | true | local only |
| `talents-zuljin-aoe-local_guide_aoe-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 744000.170 | 784.805 | true | local only |
| `talents-zuljin-aoe-method_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 710253.909 | 829.908 | true | local only |
| `talents-zuljin-aoe-user-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 715110.258 | 440.817 | true | retained |
| `talents-zuljin-aoe-user-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 714036.873 | 823.204 | true | local only |
| `talents-zuljin-aoe-user_short_cd-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 745526.357 | 433.176 | true | retained |
| `talents-zuljin-aoe-user_short_cd-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 744130.325 | 784.274 | true | local only |
| `talents-zuljin-aoe-user_short_cd_martial-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 743498.620 | 447.194 | true | retained |
| `talents-zuljin-aoe-user_short_cd_martial-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 743254.561 | 836.569 | true | local only |
| `talents-zuljin-aoe-user_short_cd_martial-craft_cm_pair_mastery_gems-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 744256.940 | 432.411 | true | retained |
| `talents-zuljin-slice-bisset_1026-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 323308.019 | 288.418 | true | retained |
| `talents-zuljin-slice-bisset_1026-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 323444.513 | 547.584 | true | local only |
| `talents-zuljin-slice-icy_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 313040.126 | 510.181 | true | local only |
| `talents-zuljin-slice-local_guide_aoe-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 322012.904 | 542.158 | true | local only |
| `talents-zuljin-slice-method_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 314222.662 | 507.643 | true | local only |
| `talents-zuljin-slice-user-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 313160.648 | 282.305 | true | retained |
| `talents-zuljin-slice-user-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 313101.795 | 514.281 | true | local only |
| `talents-zuljin-slice-user_short_cd-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 321899.221 | 294.442 | true | retained |
| `talents-zuljin-slice-user_short_cd-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 322269.761 | 542.203 | true | local only |
| `talents-zuljin-slice-user_short_cd_martial-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 323294.843 | 288.307 | true | retained |
| `talents-zuljin-slice-user_short_cd_martial-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 323473.471 | 547.860 | true | local only |
| `talents-zuljin-slice-user_short_cd_martial-craft_cm_pair_mastery_gems-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 324126.469 | 294.221 | true | retained |
| `talents-zuljin-slice-user_short_cd_martial-craft_cm_pair_mastery_gems-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 324136.663 | 545.229 | true | local only |
| `talents-zuljin-slice-user_short_cd_martial-flask_crit-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 320955.363 | 529.125 | true | local only |
| `talents-zuljin-slice-user_short_cd_martial-flask_haste-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 320079.451 | 527.593 | true | local only |
| `talents-zuljin-slice-user_short_cd_martial-gems_240898-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 323205.517 | 529.855 | true | local only |
| `talents-zuljin-slice-user_short_cd_martial-rings_advanced_mastery-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 318238.420 | 520.380 | true | local only |
| `talents-zuljin-st-bisset_1026-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 184736.694 | 100.288 | true | retained |
| `talents-zuljin-st-bisset_1026-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 184802.021 | 181.062 | true | local only |
| `talents-zuljin-st-icy_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 180877.052 | 179.017 | true | local only |
| `talents-zuljin-st-local_guide_aoe-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 180295.513 | 176.129 | true | local only |
| `talents-zuljin-st-method_mplus-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 185433.951 | 186.070 | true | local only |
| `talents-zuljin-st-user-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 180823.095 | 98.707 | true | retained |
| `talents-zuljin-st-user-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 181067.494 | 176.328 | true | local only |
| `talents-zuljin-st-user_short_cd-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 180409.412 | 97.184 | true | retained |
| `talents-zuljin-st-user_short_cd-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 180538.053 | 176.373 | true | local only |
| `talents-zuljin-st-user_short_cd_martial-baseline-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 184743.249 | 100.319 | true | retained |
| `talents-zuljin-st-user_short_cd_martial-baseline-3000-26102961` | screen_or_smoke | 3000 | 3007 | 2999 | 26102961 | 184785.774 | 180.910 | true | local only |
| `talents-zuljin-st-user_short_cd_martial-craft_cm_pair_mastery_gems-10000-26102971` | final_or_control | 10000 | 10007 | 9999 | 26102971 | 184652.279 | 103.354 | true | retained |
| `tuning-tendril-aoe-baseline-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 746726.832 | 421.317 | true | retained |
| `tuning-tendril-aoe-craft_back_hm-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 745906.919 | 417.342 | true | retained |
| `tuning-tendril-aoe-craft_cm_pair_mastery_gems-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 747280.251 | 409.165 | true | retained |
| `tuning-tendril-aoe-diamond_three_colors-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 747228.179 | 416.787 | true | retained |
| `tuning-tendril-aoe-gems_240898-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 745219.066 | 418.673 | true | retained |
| `tuning-tendril-slice-baseline-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 323698.184 | 274.385 | true | retained |
| `tuning-tendril-slice-baseline-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323795.338 | 551.132 | true | local only |
| `tuning-tendril-slice-craft_back_cm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 324367.283 | 564.374 | true | local only |
| `tuning-tendril-slice-craft_back_hm-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 324551.296 | 276.440 | true | retained |
| `tuning-tendril-slice-craft_back_hm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 324694.406 | 562.842 | true | local only |
| `tuning-tendril-slice-craft_cm_pair-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 324443.468 | 557.672 | true | local only |
| `tuning-tendril-slice-craft_cm_pair_mastery_gems-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 325052.986 | 276.779 | true | retained |
| `tuning-tendril-slice-craft_cm_pair_mastery_gems-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 324984.133 | 550.201 | true | local only |
| `tuning-tendril-slice-craft_feet_ch-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 322344.072 | 559.117 | true | local only |
| `tuning-tendril-slice-craft_feet_hm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323097.857 | 558.378 | true | local only |
| `tuning-tendril-slice-craft_finger2_ch-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 318633.863 | 529.015 | true | local only |
| `tuning-tendril-slice-craft_finger2_hm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 321900.828 | 539.684 | true | local only |
| `tuning-tendril-slice-craft_hands_ch-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323069.431 | 561.405 | true | local only |
| `tuning-tendril-slice-craft_hands_cm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323446.534 | 558.019 | true | local only |
| `tuning-tendril-slice-craft_wrist_ch-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 322415.816 | 544.276 | true | local only |
| `tuning-tendril-slice-craft_wrist_hm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323970.655 | 555.934 | true | local only |
| `tuning-tendril-slice-diamond_powerful-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323759.803 | 550.422 | true | local only |
| `tuning-tendril-slice-diamond_three_colors-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 324535.325 | 276.631 | true | retained |
| `tuning-tendril-slice-diamond_three_colors-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 324017.508 | 555.048 | true | local only |
| `tuning-tendril-slice-flask_crit-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 319857.332 | 535.376 | true | local only |
| `tuning-tendril-slice-flask_haste-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 320168.475 | 543.872 | true | local only |
| `tuning-tendril-slice-gems_240888-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 322731.598 | 548.429 | true | local only |
| `tuning-tendril-slice-gems_240890-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323399.225 | 545.224 | true | local only |
| `tuning-tendril-slice-gems_240892-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323146.096 | 555.493 | true | local only |
| `tuning-tendril-slice-gems_240896-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323817.178 | 539.911 | true | local only |
| `tuning-tendril-slice-gems_240898-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 324232.099 | 277.826 | true | retained |
| `tuning-tendril-slice-gems_240898-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 324515.202 | 538.575 | true | local only |
| `tuning-tendril-slice-gems_240900-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 324105.228 | 566.940 | true | local only |
| `tuning-tendril-slice-gems_240904-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323093.577 | 549.528 | true | local only |
| `tuning-tendril-slice-gems_240906-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 323391.724 | 550.515 | true | local only |
| `tuning-tendril-slice-gems_240908-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 324162.492 | 558.222 | true | local only |
| `tuning-tendril-slice-rings_advanced_haste-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 317694.320 | 541.370 | true | local only |
| `tuning-tendril-slice-rings_advanced_mastery-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 317999.461 | 529.620 | true | local only |
| `tuning-tendril-slice-rings_crit-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 317550.713 | 540.643 | true | local only |
| `tuning-tendril-slice-rings_haste-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 317154.300 | 550.991 | true | local only |
| `tuning-tendril-slice-rings_mastery-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 317924.155 | 527.929 | true | local only |
| `tuning-tendril-st-baseline-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 178771.460 | 85.334 | true | retained |
| `tuning-tendril-st-craft_back_hm-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 178818.272 | 84.825 | true | retained |
| `tuning-tendril-st-craft_cm_pair_mastery_gems-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 179204.169 | 86.700 | true | retained |
| `tuning-tendril-st-gems_240898-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 178792.494 | 86.205 | true | retained |
| `tuning-tendril-stats-baseline-40-26102931` | static_snapshot | 40 | 47 | 39 | 26102931 | 159507.610 | 1095.025 | true | retained |
| `tuning-tendril-stats-craft_cm_pair_mastery_gems-40-26102931` | static_snapshot | 40 | 47 | 39 | 26102931 | 159955.175 | 1388.423 | true | retained |
| `tuning-zuljin-aoe-baseline-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 714965.667 | 401.811 | true | retained |
| `tuning-zuljin-aoe-craft_back_hm-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 712879.346 | 399.308 | true | retained |
| `tuning-zuljin-aoe-craft_cm_pair_mastery_gems-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 716624.390 | 389.539 | true | retained |
| `tuning-zuljin-aoe-diamond_three_colors-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 714692.938 | 404.480 | true | retained |
| `tuning-zuljin-aoe-gems_240898-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 714599.285 | 396.095 | true | retained |
| `tuning-zuljin-slice-baseline-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 312847.409 | 258.230 | true | retained |
| `tuning-zuljin-slice-baseline-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 312966.039 | 526.440 | true | local only |
| `tuning-zuljin-slice-craft_back_cm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 313061.095 | 523.205 | true | local only |
| `tuning-zuljin-slice-craft_back_hm-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 313288.859 | 255.966 | true | retained |
| `tuning-zuljin-slice-craft_back_hm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 313101.929 | 517.890 | true | local only |
| `tuning-zuljin-slice-craft_cm_pair-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 313659.669 | 525.858 | true | local only |
| `tuning-zuljin-slice-craft_cm_pair_mastery_gems-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 314069.829 | 259.950 | true | retained |
| `tuning-zuljin-slice-craft_cm_pair_mastery_gems-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 314174.119 | 517.668 | true | local only |
| `tuning-zuljin-slice-craft_feet_ch-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 311583.038 | 519.145 | true | local only |
| `tuning-zuljin-slice-craft_feet_hm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 312130.989 | 508.296 | true | local only |
| `tuning-zuljin-slice-craft_finger2_ch-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 308537.560 | 499.520 | true | local only |
| `tuning-zuljin-slice-craft_finger2_hm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 309604.574 | 501.034 | true | local only |
| `tuning-zuljin-slice-craft_hands_ch-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 312455.709 | 513.457 | true | local only |
| `tuning-zuljin-slice-craft_hands_cm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 313248.621 | 507.367 | true | local only |
| `tuning-zuljin-slice-craft_wrist_ch-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 311700.516 | 512.629 | true | local only |
| `tuning-zuljin-slice-craft_wrist_hm-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 311950.714 | 513.184 | true | local only |
| `tuning-zuljin-slice-diamond_powerful-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 312877.290 | 526.408 | true | local only |
| `tuning-zuljin-slice-diamond_three_colors-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 312922.032 | 255.325 | true | retained |
| `tuning-zuljin-slice-diamond_three_colors-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 313357.491 | 522.952 | true | local only |
| `tuning-zuljin-slice-flask_crit-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 311118.736 | 530.687 | true | local only |
| `tuning-zuljin-slice-flask_haste-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 309509.024 | 503.263 | true | local only |
| `tuning-zuljin-slice-gems_240888-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 311523.062 | 524.885 | true | local only |
| `tuning-zuljin-slice-gems_240890-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 312418.353 | 525.211 | true | local only |
| `tuning-zuljin-slice-gems_240892-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 312687.467 | 496.870 | true | local only |
| `tuning-zuljin-slice-gems_240896-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 311902.511 | 509.614 | true | local only |
| `tuning-zuljin-slice-gems_240898-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 312983.756 | 257.230 | true | retained |
| `tuning-zuljin-slice-gems_240898-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 313368.249 | 515.083 | true | local only |
| `tuning-zuljin-slice-gems_240900-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 312605.783 | 516.883 | true | local only |
| `tuning-zuljin-slice-gems_240904-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 311722.325 | 511.766 | true | local only |
| `tuning-zuljin-slice-gems_240906-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 312461.665 | 514.784 | true | local only |
| `tuning-zuljin-slice-gems_240908-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 313038.344 | 509.271 | true | local only |
| `tuning-zuljin-slice-rings_advanced_haste-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 307397.177 | 490.071 | true | local only |
| `tuning-zuljin-slice-rings_advanced_mastery-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 308235.392 | 495.573 | true | local only |
| `tuning-zuljin-slice-rings_crit-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 307685.982 | 505.479 | true | local only |
| `tuning-zuljin-slice-rings_haste-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 307039.760 | 498.678 | true | local only |
| `tuning-zuljin-slice-rings_mastery-3000-26102941` | screen_or_smoke | 3000 | 3007 | 2999 | 26102941 | 307588.158 | 507.271 | true | local only |
| `tuning-zuljin-st-baseline-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 180859.728 | 90.827 | true | retained |
| `tuning-zuljin-st-craft_back_hm-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 180661.587 | 88.492 | true | retained |
| `tuning-zuljin-st-craft_cm_pair_mastery_gems-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 181185.496 | 91.886 | true | retained |
| `tuning-zuljin-st-gems_240898-12000-26102951` | final_or_control | 12000 | 12007 | 11999 | 26102951 | 180824.179 | 90.155 | true | retained |
| `tuning-zuljin-stats-baseline-40-26102931` | static_snapshot | 40 | 47 | 39 | 26102931 | 161756.526 | 1580.014 | true | retained |
| `tuning-zuljin-stats-craft_cm_pair_mastery_gems-40-26102931` | static_snapshot | 40 | 47 | 39 | 26102931 | 163516.169 | 1255.473 | true | retained |
| `two-crafts-user-aoe-baseline-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 706181.875 | 754.169 | true | local only |
| `two-crafts-user-aoe-baseline-8000-261029111` | final_or_control | 8000 | 8007 | 7999 | 261029111 | 706640.090 | 493.034 | true | retained |
| `two-crafts-user-aoe-belt_cm-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 713437.675 | 732.400 | true | local only |
| `two-crafts-user-aoe-belt_cm-8000-261029111` | final_or_control | 8000 | 8007 | 7999 | 261029111 | 713119.939 | 486.170 | true | retained |
| `two-crafts-user-aoe-belt_hm-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 711190.002 | 718.829 | true | local only |
| `two-crafts-user-aoe-belt_hm-8000-261029111` | final_or_control | 8000 | 8007 | 7999 | 261029111 | 711344.763 | 488.153 | true | retained |
| `two-crafts-user-aoe-belt_legs_cm_oldhands-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 710554.381 | 745.368 | true | local only |
| `two-crafts-user-aoe-belt_legs_cm_oldhands-8000-261029111` | final_or_control | 8000 | 8007 | 7999 | 261029111 | 711268.609 | 482.657 | true | retained |
| `two-crafts-user-aoe-belt_legs_hm_gloves334-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 709301.276 | 763.421 | true | local only |
| `two-crafts-user-aoe-belt_legs_hm_oldhands-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 706564.406 | 743.384 | true | local only |
| `two-crafts-user-aoe-belt_loa-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 712519.083 | 724.098 | true | local only |
| `two-crafts-user-slice-baseline-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 307436.132 | 469.951 | true | local only |
| `two-crafts-user-slice-baseline-8000-261029111` | final_or_control | 8000 | 8007 | 7999 | 261029111 | 307688.082 | 309.581 | true | retained |
| `two-crafts-user-slice-belt_cm-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 310236.204 | 482.590 | true | local only |
| `two-crafts-user-slice-belt_cm-8000-261029111` | final_or_control | 8000 | 8007 | 7999 | 261029111 | 310598.248 | 313.793 | true | retained |
| `two-crafts-user-slice-belt_hm-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 309607.087 | 468.914 | true | local only |
| `two-crafts-user-slice-belt_hm-8000-261029111` | final_or_control | 8000 | 8007 | 7999 | 261029111 | 309731.158 | 312.255 | true | retained |
| `two-crafts-user-slice-belt_legs_cm_oldhands-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 309733.661 | 478.750 | true | local only |
| `two-crafts-user-slice-belt_legs_cm_oldhands-8000-261029111` | final_or_control | 8000 | 8007 | 7999 | 261029111 | 309405.146 | 309.488 | true | retained |
| `two-crafts-user-slice-belt_legs_hm_gloves334-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 310031.065 | 466.744 | true | local only |
| `two-crafts-user-slice-belt_legs_hm_oldhands-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 307942.258 | 478.157 | true | local only |
| `two-crafts-user-slice-belt_loa-3500-261029101` | screen_or_smoke | 3500 | 3507 | 3499 | 261029101 | 309561.996 | 470.699 | true | local only |
