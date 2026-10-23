$ErrorActionPreference='Stop'
$dir=$PSScriptRoot
$actor=Get-Content (Join-Path (Split-Path (Split-Path $dir)) 'snapshots/2026-10-15-equipped.simc') -Raw
$variants=@'
profileset."H4_ring_318"=finger1=,id=268249,bonus_id=6652/13668/13334/12849,enchant_id=7967
profileset."H4_ring_334"=finger1=,id=268249,bonus_id=6652/13668/13334/12849,ilevel=334,enchant_id=7967
profileset."H7_trinket_318"=trinket2=,id=270173,bonus_id=6652/13334/12849
profileset."H7_trinket_334"=trinket2=,id=270173,bonus_id=6652/13334/12849,ilevel=334
profileset."H4_trinket_334"=trinket2=,id=270166,bonus_id=6652/13334/12849,ilevel=334
profileset."Vault_1H334_with_owned1H321"=main_hand=,id=159645,bonus_id=12849/13440/6652/12701,ilevel=334,enchant_id=8689
profileset."Vault_1H334_with_owned1H321"+=off_hand=,id=171582,bonus_id=8902/7756/12701/12846,enchant_id=8689,content_tuning=440
profileset."Chest334_keep4pc"=chest=,id=271522,redirected_base_stats=251226,bonus_id=12849/13440/41/13662/12699,ilevel=334,enchant_id=7987
profileset."Chest334_keep4pc"+=set_bonus=mid2_2pc=1/mid2_4pc=1
profileset."H4_ring_334_replace_craft"=finger2=,id=268249,bonus_id=6652/13668/13334/12849,ilevel=334,enchant_id=7967
'@
foreach($mode in @('raid','dungeon')){
 $style=if($mode -eq 'raid'){'Patchwerk'}else{'DungeonSlice'}
 $buff=if($mode -eq 'raid'){1}else{0}
 $raw="ptr=0`n"+$actor+"`nflask=flask_of_the_magisters_2`nfood=harandar_celebration`naugmentation=void_touched`npotion=potion_of_recklessness_2`ntemporary_enchant=main_hand:thalassian_phoenix_oil_2/off_hand:thalassian_phoenix_oil_2`noptimal_raid=$buff`noverride.bloodlust=$buff`nthreads=6`nprofileset_work_threads=2`nvary_combat_length=0`nfight_style=$style`nmax_time=240`niterations=4000`nseed=15102726`n"+$variants
 [IO.File]::WriteAllText((Join-Path $dir "vault-$mode.simc"),$raw,[Text.UTF8Encoding]::new($false))
}
