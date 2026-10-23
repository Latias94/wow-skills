param(
    [ValidateSet('raid', 'dungeon')][string]$Mode,
    [string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$lines = [System.Collections.Generic.List[string]]::new()
$base = @(Get-Content (Join-Path $PSScriptRoot "search-$Mode.simc") | Where-Object { $_ -notmatch '^profileset\.' })
$lines.AddRange([string[]]($base -replace '^iterations=1200$', 'iterations=3000' -replace '^seed=10102026$', 'seed=20102026'))
$pairs = [ordered]@{ HM = '36/49'; CM = '32/49' }
foreach ($pair in $pairs.Keys) {
    foreach ($flask in @('flask_of_the_magisters_2','flask_of_the_shattered_sun_2','flask_of_the_blood_knights_2')) {
        foreach ($gem in @('240908','240906')) {
            $name = "Joint_${pair}_${flask}_G${gem}"
            $lines.Add("profileset.`"$name`"=wrist=,id=244576,ilevel=331,bonus_id=12384,crafted_stats=$($pairs[$pair]),crafting_quality=5,gem_id=$gem")
            $lines.Add("profileset.`"$name`"+=feet=,id=244569,ilevel=331,bonus_id=12384,crafted_stats=$($pairs[$pair]),crafting_quality=5,enchant_id=7963")
            $lines.Add("profileset.`"$name`"+=waist=,id=268256,ilevel=334,gem_id=$gem")
            $lines.Add("profileset.`"$name`"+=finger1=,id=268249,ilevel=334,enchant_id=7967,gem_id=$gem")
            $lines.Add("profileset.`"$name`"+=flask=$flask")
        }
    }
}
$changes = [ordered]@{
    Known_neck_variant = @('neck=,id=268265,ilevel=334,bonus_id=13987,gem_id=240914/240890')
    Atroxus_instead_new_ring = @('finger2=,id=252258,ilevel=334,enchant_id=7967,gem_id=240900')
    New_ring_instead_H4 = @('finger1=,id=281029,ilevel=334,enchant_id=7967,gem_id=240908','finger2=,id=252258,ilevel=334,enchant_id=7967,gem_id=240900')
    Old_chest = @('chest=,id=271522,ilevel=334,enchant_id=7987')
    New_chest = @('chest=,id=271522,redirected_base_stats=281236,ilevel=334,bonus_id=14049,enchant_id=7987')
    H7_passive = @('trinket2=,id=270173,ilevel=334')
    H2_core = @('trinket2=,id=270165,ilevel=334')
    Explorer_bag = @('trinket2=,id=270164,ilevel=334')
    New_passive = @('trinket2=,id=281215,ilevel=334')
    Tier_shoulder = @('shoulder=,id=271517,ilevel=334,enchant_id=8001')
    Craft_cloak_shoes = @('back=,id=239656,ilevel=331,bonus_id=12384,crafted_stats=36/49,crafting_quality=5','wrist=,id=251135,ilevel=334,gem_id=240908')
}
foreach ($name in $changes.Keys) {
    $first = $true
    foreach ($change in $changes[$name]) {
        $op = if ($first) { '=' } else { '+=' }
        $lines.Add("profileset.`"$name`"$op$change")
        $first = $false
    }
}
$lines | Set-Content -LiteralPath $OutputPath -Encoding ascii
Write-Output "Generated $Mode joint search: 23 profilesets"
