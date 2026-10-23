param([ValidateSet('raid', 'dungeon')][string]$Mode)
$ErrorActionPreference = 'Stop'
$inputPath = Join-Path $PSScriptRoot "joint-$Mode.simc"
$report = Get-Content (Join-Path $PSScriptRoot "joint-$Mode.json") -Raw | ConvertFrom-Json
$inputLines = @(Get-Content $inputPath)
$base = @($inputLines | Where-Object { $_ -notmatch '^profileset\.' })
$shortlist = @($report.sim.profilesets.results | Where-Object name -Like 'Joint_*' | Sort-Object mean -Descending | Select-Object -First 3)
$selected = $shortlist[0].name
$prefix = 'profileset."' + $selected + '"'
$edits = @($inputLines | Where-Object { $_.StartsWith($prefix) } | ForEach-Object { $_.Substring($prefix.Length) -replace '^\+?=', '' })
foreach ($edit in $edits) {
    $key = $edit.Split('=', 2)[0]
    $base = @($base | ForEach-Object { if ($_.StartsWith("$key=")) { $edit } else { $_ } })
}
$base = @($base | Where-Object { $_ -notmatch '^profileset_work_threads=' } | ForEach-Object {
    if ($_ -match '^monk=') { "monk=Shaseng_Optimized_$Mode" }
    elseif ($_ -match '^iterations=') { 'iterations=10000' }
    elseif ($_ -match '^seed=') { 'seed=30102026' }
    else { $_ }
})
$base | Set-Content (Join-Path $PSScriptRoot "optimized-$Mode.simc") -Encoding ascii
# Recheck close stat candidates and equipment after combining the winning stat settings.
$check = [System.Collections.Generic.List[string]]::new()
$check.AddRange([string[]]($base -replace '^iterations=10000$', 'iterations=5000'))
$check.Add('profileset_work_threads=2')
foreach ($rival in $shortlist | Select-Object -Skip 1) {
    $p = 'profileset."' + $rival.name + '"'
    $check.AddRange([string[]]@($inputLines | Where-Object { $_.StartsWith($p) }))
}
$alternativePair = if ($selected -like 'Joint_CM_*') { 'Joint_HM_*' } else { 'Joint_CM_*' }
$rival = $report.sim.profilesets.results | Where-Object name -Like $alternativePair | Sort-Object mean -Descending | Select-Object -First 1
$p = 'profileset."' + $rival.name + '"'
$check.AddRange([string[]]@($inputLines | Where-Object { $_.StartsWith($p) }))
if ($Mode -eq 'raid') {
    $check.Add('profileset."Original_target"=chest=,id=271522,ilevel=334,enchant_id=7987')
    $check.Add('profileset."Original_target"+=trinket2=,id=281215,ilevel=334')
} else {
    $check.Add('profileset."Original_target"=chest=,id=271522,ilevel=334,enchant_id=7987')
}
foreach ($slot in @('wrist','feet','waist','finger1','flask')) {
    $original = Get-Content (Join-Path $PSScriptRoot 'target-bis.simc') | Where-Object { $_.StartsWith("$slot=") }
    $check.Add("profileset.`"Original_target`"+=$original")
}
foreach ($name in @('Known_neck_variant','Old_chest','New_chest','H7_passive','H2_core','New_passive','New_ring_instead_H4','Craft_cloak_shoes')) {
    $p = 'profileset."' + $name + '"'
    $check.AddRange([string[]]@($inputLines | Where-Object { $_.StartsWith($p) }))
}
$check | Set-Content (Join-Path $PSScriptRoot "verify-$Mode.simc") -Encoding ascii
[ordered]@{
    mode = $Mode
    selected_profile = $selected
    shortlist = $shortlist
    selection_status = 'Screening winner pending independent-seed verification; near ties are not proven rankings.'
} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $PSScriptRoot "selection-$Mode.json") -Encoding utf8
Write-Output "$Mode screening candidate: $selected"
