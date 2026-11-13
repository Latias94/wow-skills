# Native run inventory — 2026-11-10

91 existing native runs; 41 full JSON results retained and 50 exploratory JSON results kept locally.

This is a transcription, not a new recommendation. The JSON companion retains exact numeric values, input/result SHA-256, native warnings, stat snapshots and original validation references.

Requested iterations, engine-reported iterations and effective samples are different fields. Short smoke, static and export-reimport runs are not DPS ranking evidence. CI is the 95% half-width of each native mean; acceptance comes from existing validation only.

| Run / original input stem | Kind | Requested | Reported | Samples | Seed | DPS | CI95 ± | Accepted | Full JSON |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| `alternate-raid-ring-reimport` | export_reimport | unknown | 27 | 19 | 26111091 | 337775.544 | 8599.979 | true | retained |
| `comparison-single-target-reimport` | export_reimport | unknown | 27 | 19 | 26111091 | 189569.685 | 1686.101 | true | retained |
| `current-equipped-reimport` | export_reimport | unknown | 27 | 19 | 26111091 | 329843.709 | 7038.231 | true | retained |
| `identity-old70575` | static_snapshot | 20 | 23 | 19 | 26111001 | 262538.960 | 5885.999 | unknown | retained |
| `live70783-aoe-bag_gloves_hm-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 750946.829 | 628.630 | true | retained |
| `live70783-aoe-core_h7-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 756659.504 | 630.876 | true | retained |
| `live70783-aoe-current-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 751787.130 | 630.177 | true | retained |
| `live70783-aoe-legs_delve-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 757351.961 | 637.315 | true | retained |
| `live70783-aoe-legs_h7-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 757167.694 | 641.584 | true | retained |
| `live70783-aoe-owned_h5_prepared-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 701663.484 | 669.213 | true | retained |
| `live70783-aoe-ring_268249-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 752229.020 | 610.792 | true | retained |
| `live70783-aoe-ring_268252-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 704251.433 | 684.464 | true | retained |
| `live70783-aoe-target_mc_sockets-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 761484.712 | 628.494 | true | retained |
| `live70783-aoe-target_mh_keep_crafted_ring-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 764285.114 | 626.317 | true | retained |
| `live70783-slice-bag_gloves_hm-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 330116.768 | 668.370 | true | local only |
| `live70783-slice-bag_gloves_hm-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 329934.718 | 402.923 | true | retained |
| `live70783-slice-cloak_h7_move_lining-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 330424.685 | 681.696 | true | local only |
| `live70783-slice-core_gems_mastery_crit-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 334921.104 | 705.964 | true | local only |
| `live70783-slice-core_gems_mastery_haste-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 333994.449 | 686.225 | true | local only |
| `live70783-slice-core_h7-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 334366.576 | 696.159 | true | local only |
| `live70783-slice-core_h7-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 334570.073 | 402.826 | true | retained |
| `live70783-slice-core_h7_bag_gloves-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 334321.420 | 689.318 | true | local only |
| `live70783-slice-core_keep_ring_268249-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 335572.421 | 703.578 | true | local only |
| `live70783-slice-core_keep_ring_268252-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 332591.155 | 684.657 | true | local only |
| `live70783-slice-core_keep_ring_272150-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 334845.196 | 711.990 | true | local only |
| `live70783-slice-core_ring_268249-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 334986.137 | 683.597 | true | local only |
| `live70783-slice-core_ring_268252-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 332726.996 | 692.344 | true | local only |
| `live70783-slice-core_ring_272150-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 334245.992 | 693.478 | true | local only |
| `live70783-slice-core_three_sockets-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 338230.237 | 718.594 | true | local only |
| `live70783-slice-craft_back_hm-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 329593.431 | 688.226 | true | local only |
| `live70783-slice-craft_feet_hm-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 328766.644 | 686.553 | true | local only |
| `live70783-slice-craft_finger2_hm-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 328963.709 | 675.292 | true | local only |
| `live70783-slice-craft_wrist_hm-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 328513.983 | 706.118 | true | local only |
| `live70783-slice-current-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 327788.070 | 669.997 | true | local only |
| `live70783-slice-current-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 328476.924 | 391.171 | true | retained |
| `live70783-slice-current_gems_mastery_crit-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 329310.857 | 682.348 | true | local only |
| `live70783-slice-current_gems_mastery_haste-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 329757.054 | 684.418 | true | local only |
| `live70783-slice-current_three_sockets-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 332478.167 | 693.262 | true | local only |
| `live70783-slice-flask_haste-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 323337.997 | 675.900 | true | local only |
| `live70783-slice-legs_delve-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 332108.441 | 679.247 | true | local only |
| `live70783-slice-legs_delve-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 332056.364 | 399.870 | true | retained |
| `live70783-slice-legs_h7-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 331985.702 | 678.327 | true | local only |
| `live70783-slice-legs_h7-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 332598.513 | 397.099 | true | retained |
| `live70783-slice-legs_murder-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 331068.951 | 690.887 | true | local only |
| `live70783-slice-legs_waist-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 333035.534 | 690.189 | true | local only |
| `live70783-slice-owned_h5_prepared-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 320644.192 | 676.931 | true | local only |
| `live70783-slice-owned_h5_prepared-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 320649.726 | 389.658 | true | retained |
| `live70783-slice-owned_h5_raw-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 313458.557 | 652.170 | true | local only |
| `live70783-slice-owned_tuned_mc-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 331011.459 | 677.298 | true | local only |
| `live70783-slice-owned_tuned_mh-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 330612.360 | 683.762 | true | local only |
| `live70783-slice-owned_zuljin-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 319439.732 | 630.898 | true | local only |
| `live70783-slice-ring_158366-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 327907.905 | 677.395 | true | local only |
| `live70783-slice-ring_252258-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 328619.227 | 694.084 | true | local only |
| `live70783-slice-ring_268249-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 330889.199 | 688.663 | true | local only |
| `live70783-slice-ring_268249-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 331187.985 | 400.061 | true | retained |
| `live70783-slice-ring_268252-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 322328.523 | 662.574 | true | local only |
| `live70783-slice-ring_268252-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 321836.834 | 388.389 | true | retained |
| `live70783-slice-ring_272148-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 322536.278 | 655.824 | true | local only |
| `live70783-slice-ring_272149-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 330406.904 | 670.948 | true | local only |
| `live70783-slice-ring_272150-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 330251.651 | 677.069 | true | local only |
| `live70783-slice-ring_273792-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 324481.885 | 670.736 | true | local only |
| `live70783-slice-ring_h5_no_socket-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 320528.219 | 683.725 | true | local only |
| `live70783-slice-shoulder_raid_cm-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 328812.543 | 690.481 | true | local only |
| `live70783-slice-target_mc-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 336138.402 | 681.061 | true | local only |
| `live70783-slice-target_mc_h5_ring-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 336828.270 | 688.923 | true | local only |
| `live70783-slice-target_mc_hm_crafts-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 339379.598 | 701.264 | true | local only |
| `live70783-slice-target_mc_keep_crafted_ring-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 338452.766 | 692.941 | true | local only |
| `live70783-slice-target_mc_sockets-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 339378.097 | 700.176 | true | local only |
| `live70783-slice-target_mc_sockets-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 338846.446 | 401.192 | true | retained |
| `live70783-slice-target_mh-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 335670.124 | 709.664 | true | local only |
| `live70783-slice-target_mh_keep_crafted_ring-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 339017.057 | 705.767 | true | local only |
| `live70783-slice-target_mh_keep_crafted_ring-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 338251.649 | 404.756 | true | retained |
| `live70783-slice-target_mh_sockets-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 339243.442 | 712.353 | true | local only |
| `live70783-slice-waist_h7-2000-26111011` | screen_or_smoke | 2000 | 2007 | 1999 | 26111011 | 329932.154 | 679.577 | true | local only |
| `live70783-st-bag_gloves_hm-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 186803.275 | 126.021 | true | retained |
| `live70783-st-core_h7-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 188762.824 | 129.184 | true | retained |
| `live70783-st-current-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 187037.217 | 126.815 | true | retained |
| `live70783-st-legs_delve-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 188421.936 | 127.777 | true | retained |
| `live70783-st-legs_h7-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 188683.134 | 126.813 | true | retained |
| `live70783-st-owned_h5_prepared-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 182362.872 | 121.049 | true | retained |
| `live70783-st-ring_268249-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 187211.004 | 128.133 | true | retained |
| `live70783-st-ring_268252-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 183259.373 | 123.258 | true | retained |
| `live70783-st-target_mc_sockets-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 190226.682 | 133.474 | true | retained |
| `live70783-st-target_mh_keep_crafted_ring-6000-26111029` | final_or_control | 6000 | 6007 | 5999 | 26111029 | 190446.941 | 131.754 | true | retained |
| `live70783-stats-bag_gloves_hm-20-26111003` | static_snapshot | 20 | 27 | 19 | 26111003 | 263953.175 | 9220.546 | true | retained |
| `live70783-stats-core_h7-20-26111003` | static_snapshot | 20 | 27 | 19 | 26111003 | 268612.400 | 7928.355 | true | retained |
| `live70783-stats-current-20-26111001` | static_snapshot | 20 | 27 | 19 | 26111001 | 264003.192 | 6502.472 | true | retained |
| `live70783-stats-owned_tuned_mc-20-26111003` | static_snapshot | 20 | 27 | 19 | 26111003 | 270316.052 | 5454.359 | true | retained |
| `live70783-stats-target_mc_sockets-20-26111003` | static_snapshot | 20 | 27 | 19 | 26111003 | 274397.763 | 5968.776 | true | retained |
| `live70783-stats-target_mh_keep_crafted_ring-20-26111003` | static_snapshot | 20 | 27 | 19 | 26111003 | 272829.022 | 7959.763 | true | retained |
| `recommended-dungeon-reimport` | export_reimport | unknown | 27 | 19 | 26111091 | 331387.561 | 7738.543 | true | retained |
