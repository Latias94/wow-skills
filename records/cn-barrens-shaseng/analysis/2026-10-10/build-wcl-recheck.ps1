param([ValidateSet('raid','dungeon')][string]$Mode)
$ErrorActionPreference = 'Stop'
$base = @(Get-Content (Join-Path $PSScriptRoot "recommended-$Mode.simc") | Where-Object { $_ -notmatch '^#' } | ForEach-Object {
    if ($_ -match '^iterations=') { 'iterations=3500' }
    elseif ($_ -match '^seed=') { 'seed=60102026' }
    else { $_ }
})
$changes = [ordered]@{
    Plain_diamond = @('head=,id=271519,redirected_base_stats=271875,ilevel=334,bonus_id=13847,enchant_id=8017,gem_id=240983')
    Plain_diamond_layout = @('head=,id=271519,redirected_base_stats=271875,ilevel=334,bonus_id=13847,enchant_id=8017,gem_id=240906','neck=,id=268265,ilevel=334,bonus_id=13987,gem_id=240983/240906')
    Tier_hands = @('hands=,id=271520,ilevel=334')
    Crafted_ring_CH = @('finger2=,id=240949,ilevel=331,crafted_stats=32/36,crafting_quality=5,enchant_id=7967,gem_id=240900')
    Crafted_ring_HM = @('finger2=,id=240949,ilevel=331,crafted_stats=36/49,crafting_quality=5,enchant_id=7967,gem_id=240900')
    Ring_keeps_new = @('finger1=,id=240949,ilevel=331,crafted_stats=36/49,crafting_quality=5,enchant_id=7967,gem_id=240906')
    Clickz_core = @('hands=,id=271520,ilevel=334','chest=,id=271522,ilevel=334,enchant_id=7987','finger2=,id=240949,ilevel=331,crafted_stats=32/36,crafting_quality=5,enchant_id=7967,gem_id=240900','trinket2=,id=270173,ilevel=334')
    Nilenga_core = @('hands=,id=271520,ilevel=334','chest=,id=244570,ilevel=331,crafted_stats=32/36,crafting_quality=5,enchant_id=7987','finger2=,id=240949,ilevel=331,crafted_stats=32/36,crafting_quality=5,enchant_id=7967,gem_id=240900','trinket2=,id=270173,ilevel=334')
    Crafted_chest_tier_hands = @('hands=,id=271520,ilevel=334','chest=,id=244570,ilevel=331,crafted_stats=32/36,crafting_quality=5,enchant_id=7987')
    Crafted_chest_HM_tier_hands = @('hands=,id=271520,ilevel=334','chest=,id=244570,ilevel=331,crafted_stats=36/49,crafting_quality=5,enchant_id=7987')
    Other_raid_hands = @('hands=,id=268234,ilevel=334')
    Other_raid_waist = @('waist=,id=268227,ilevel=334,gem_id=240906')
    Dungeon_cloak = @('back=,id=251132,ilevel=334')
    Bisset_crafts = @('back=,id=239656,ilevel=331,bonus_id=12384,crafted_stats=36/49,crafting_quality=5','wrist=,id=244576,ilevel=331,bonus_id=12384,crafted_stats=32/49,crafting_quality=5,gem_id=240906','feet=,id=271521,ilevel=334,enchant_id=7963')
    Dungeon_ring_158366 = @('finger2=,id=158366,ilevel=334,enchant_id=7967,gem_id=240900')
}
$lines = [System.Collections.Generic.List[string]]::new()
$lines.AddRange([string[]]$base)
$lines.Add('profileset_work_threads=2')
foreach($name in $changes.Keys) {
    $first = $true
    foreach($change in $changes[$name]) {
        $op = if($first) { '=' } else { '+=' }
        $lines.Add("profileset.`"$name`"$op$change")
        $first = $false
    }
}
$lines | Set-Content (Join-Path $PSScriptRoot "wcl-recheck-$Mode.simc") -Encoding ascii
Write-Output "${Mode}: 15 WCL-inspired normalized candidates"
