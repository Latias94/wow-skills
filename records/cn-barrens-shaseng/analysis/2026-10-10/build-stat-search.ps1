param(
    [ValidateSet('raid', 'dungeon')][string]$Mode,
    [string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$source = Join-Path $PSScriptRoot 'target-bis.simc'
$base = @(Get-Content $source | Where-Object { $_ -notmatch '^#' -and $_ -notmatch '^\s*$' })
$base = @($base | Where-Object { $_ -notmatch '^(fight_style|max_time|iterations|seed)=' })
if ($Mode -eq 'raid') {
    $base = @($base | ForEach-Object {
        if ($_ -match '^trinket2=') { 'trinket2=,id=270173,ilevel=334' }
        elseif ($_ -match '^chest=') { 'chest=,id=271522,redirected_base_stats=281236,ilevel=334,bonus_id=14049,enchant_id=7987' }
        else { $_ }
    })
    $base += 'fight_style=Patchwerk', 'max_time=240'
} else {
    $base += 'fight_style=DungeonSlice', 'max_time=360'
}
$base += 'iterations=1200', 'seed=10102026', 'profileset_work_threads=2'
$pairs = [ordered]@{ HM = '36/49'; CM = '32/49'; CH = '32/36' }
$flasks = [ordered]@{
    M = 'flask_of_the_magisters_2'
    H = 'flask_of_the_blood_knights_2'
    C = 'flask_of_the_shattered_sun_2'
}
$lines = [System.Collections.Generic.List[string]]::new()
$lines.AddRange([string[]]$base)
foreach ($w in $pairs.Keys) {
    foreach ($f in $pairs.Keys) {
        foreach ($a in $flasks.Keys) {
            $name = "W_${w}_F_${f}_Flask_${a}"
            $lines.Add("profileset.`"$name`"=wrist=,id=244576,ilevel=331,bonus_id=12384,crafted_stats=$($pairs[$w]),crafting_quality=5,gem_id=240908")
            $lines.Add("profileset.`"$name`"+=feet=,id=244569,ilevel=331,bonus_id=12384,crafted_stats=$($pairs[$f]),crafting_quality=5,enchant_id=7963")
            $lines.Add("profileset.`"$name`"+=flask=$($flasks[$a])")
        }
    }
}
# Preserve three gem families while changing the three flexible Garnet sockets.
foreach ($g in @('240904', '240906', '240908')) {
    $name = "Garnet_$g"
    foreach ($slot in @('wrist','waist','finger1')) {
        $line = $base | Where-Object { $_ -match "^$slot=" }
        $line = $line -replace 'gem_id=240908', "gem_id=$g"
        $op = if ($slot -eq 'wrist') { '=' } else { '+=' }
        $lines.Add("profileset.`"$name`"$op$line")
    }
}
foreach ($e in @('7965','8039','7991')) {
    $name = "Enchant_$e"
    if ($e -eq '7965') {
        foreach ($slot in @('finger1','finger2')) {
            $line = ($base | Where-Object { $_ -match "^$slot=" }) -replace 'enchant_id=7967', 'enchant_id=7965'
            $op = if ($slot -eq 'finger1') { '=' } else { '+=' }
            $lines.Add("profileset.`"$name`"$op$line")
        }
    } else {
        $slot = if ($e -eq '8039') { 'main_hand' } else { 'head' }
        $line = ($base | Where-Object { $_ -match "^$slot=" }) -replace 'enchant_id=\d+', "enchant_id=$e"
        $lines.Add("profileset.`"$name`"=$line")
    }
}
$lines | Set-Content -LiteralPath $OutputPath -Encoding ascii
Write-Output "Generated $Mode stat search: 33 profilesets -> $OutputPath"
