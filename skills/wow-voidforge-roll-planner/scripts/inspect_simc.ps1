#Requires -Version 7.0
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$SimcPath,
    [Parameter(Mandatory)][string]$OutputPath,
    [int]$Locale = 4,
    [int]$DataEnvironment = 1,
    [switch]$Force
)

$ErrorActionPreference = 'Stop'
$inputFile = (Resolve-Path -LiteralPath $SimcPath).Path
$outputFile = [System.IO.Path]::GetFullPath($OutputPath)
if ($inputFile -eq $outputFile) { throw 'Input and output paths must differ.' }
if ((Test-Path -LiteralPath $outputFile) -and -not $Force) {
    throw 'Output exists. Choose a new snapshot path or explicitly use -Force.'
}
$slots = @('head','neck','shoulder','back','chest','wrist','hands','waist',
    'legs','feet','finger1','finger2','trinket1','trinket2','main_hand','off_hand')
$seen = @{}
$items = foreach ($line in Get-Content -LiteralPath $inputFile) {
    if ($line -notmatch '^([a-z0-9_]+)=(.*)$') { continue }
    $slot = $Matches[1]
    $value = $Matches[2]
    if ($slot -notin $slots) { continue }
    if ($seen.ContainsKey($slot)) { throw "Duplicate equipped slot: $slot" }
    $seen[$slot] = $true
    $attributes = @{}
    foreach ($part in $value.Split(',')) {
        $pair = $part.Split('=', 2)
        if ($pair.Count -eq 2) { $attributes[$pair[0]] = $pair[1] }
    }
    if (-not $attributes.ContainsKey('id')) { throw "Missing item ID: $slot" }
    $itemId = [int]$attributes['id']
    $bonus = $attributes['bonus_id']
    $url = 'https://nether.wowhead.com/tooltip/item/{0}?dataEnv={1}&locale={2}' -f $itemId,$DataEnvironment,$Locale
    if ($bonus) { $url += '&bonus=' + ($bonus -replace '/', ':') }
    $row = [ordered]@{
        slot = $slot; item_id = $itemId; bonus_ids = $bonus
        gem_ids = $attributes['gem_id']; enchant_id = $attributes['enchant_id']
        name = $null; item_level = $null; upgrade_text = $null
        slot_type = $null; inventory_type = $null; secondary_ratings = @{}
        source = $url; error = $null
    }
    try {
        $tooltip = Invoke-RestMethod -Uri $url -TimeoutSec 30
        $html = $tooltip.tooltip
        $level = [regex]::Match($html, '<!--ilvl-->(\d+)')
        if (-not $level.Success) { throw 'Tooltip has no explicit item level.' }
        $row.name = $tooltip.name
        $row.item_level = [int]$level.Groups[1].Value
        $row.upgrade_text = ([regex]::Match($html, '(?:升级：|Upgrade:)(.*?)</span>').Groups[1].Value -replace '<[^>]+>', '').Trim()
        $row.slot_type = ([regex]::Match($html, '<table width="100%"><tr><td>(.*?)</td>').Groups[1].Value -replace '<[^>]+>', '').Trim()
        if ($row.slot_type -in @('双手','Two-Hand')) { $row.inventory_type = 'two_hand' }
        foreach ($stat in @{crit=32;haste=36;mastery=49;versatility=40}.GetEnumerator()) {
            $rating = [regex]::Match($html, '<!--rtg' + $stat.Value + '-->([\d,]+)')
            if ($rating.Success) {
                $row.secondary_ratings[$stat.Key] = [int]($rating.Groups[1].Value -replace ',', '')
            }
        }
    } catch {
        $row.error = $_.Exception.Message
    }
    [pscustomobject]$row
}
$items = @($items)
$average = $null
$required = $slots | Where-Object { $_ -ne 'off_hand' }
$complete = @($required | Where-Object { -not $seen.ContainsKey($_) }).Count -eq 0
$mainHand = $items | Where-Object slot -eq 'main_hand'
$twoHand = $mainHand.inventory_type -eq 'two_hand'
if ($complete -and @($items | Where-Object error).Count -eq 0) {
    if ($twoHand -and -not $seen.ContainsKey('off_hand')) {
        $average = (($items | Measure-Object item_level -Sum).Sum + $mainHand.item_level) / 16
    } elseif (-not $twoHand -and $seen.ContainsKey('off_hand')) {
        $average = ($items | Measure-Object item_level -Sum).Sum / 16
    }
}
$result = [ordered]@{
    schema_version = 1; retrieved_at = (Get-Date).ToString('o')
    simc_path = $inputFile; data_environment = $DataEnvironment; locale = $Locale
    equipped_average = $average; items = $items
    limitations = 'Tooltip lookup only; no gems/enchants/passives in ratings, no talent decoding or DPS simulation.'
}
$parent = Split-Path -Parent $outputFile
[System.IO.Directory]::CreateDirectory($parent) | Out-Null
[System.IO.File]::WriteAllText($outputFile, ($result | ConvertTo-Json -Depth 8), [System.Text.UTF8Encoding]::new($false))
Write-Output $outputFile
if (@($items | Where-Object error).Count -gt 0) {
    Write-Warning 'Some tooltip lookups failed; see per-item errors. Average was withheld.'
}
