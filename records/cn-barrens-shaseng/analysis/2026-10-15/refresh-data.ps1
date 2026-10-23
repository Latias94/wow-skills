$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$previous = Join-Path (Split-Path $dir) '2026-10-10'
$oldHtml = Get-Content (Join-Path $previous 'dashboard.html') -Raw
$oldData = [regex]::Match($oldHtml, '<script id="report-data" type="application/json">(.*?)</script>', 'Singleline').Groups[1].Value | ConvertFrom-Json
$items = foreach ($id in @(281029,281215,281236)) {
    $url = "https://nether.wowhead.com/tooltip/item/${id}?locale=4&ilvl=334"
    $tip = Invoke-RestMethod $url -TimeoutSec 25
    [ordered]@{
        id=$id; retrieved_at=(Get-Date).ToString('o'); source=$url
        name=$tip.name; tooltip=$tip.tooltip; icon=$tip.icon
        previous_name=$oldData.items."$id".name
        previous_tooltip=$oldData.items."$id".tooltip
    }
}
[IO.File]::WriteAllText((Join-Path $dir 'wowhead-live-items.json'), (ConvertTo-Json -InputObject @($items) -Depth 8), [Text.UTF8Encoding]::new($false))
foreach ($mode in @('raid','dungeon')) {
    $raw = Get-Content (Join-Path $previous "practical-$mode.simc") -Raw
    $raw = $raw -replace '(?m)^ptr=1\r?$', 'ptr=0'
    $raw = $raw -replace '(?m)^seed=\d+\r?$', 'seed=15102026'
    $raw = $raw -replace '(?m)^iterations=\d+\r?$', 'iterations=6000'
    $raw = "# Recheck of October 10 candidates with October 15 live data; old gear/talents retained.`n" + $raw
    $raw += "`n" + 'profileset."Old_ring_Atroxus"=finger2=,id=273792,ilevel=334,enchant_id=7967,gem_id=240900' + "`n"
    $raw += 'profileset."Crafted_ring_CM"=finger2=,id=240949,ilevel=331,crafted_stats=32/49,crafting_quality=5,enchant_id=7967,gem_id=240900' + "`n"
    [IO.File]::WriteAllText((Join-Path $dir "recheck-$mode.simc"),$raw,[Text.UTF8Encoding]::new($false))
    $clean = Get-Content (Join-Path $previous "recommended-$mode.simc") -Raw
    $clean = $clean -replace '(?m)^ptr=1\r?$', 'ptr=0'
    $clean = $clean -replace '(?m)^# Attainable.*\r?$', '# October 15 live recheck; same October 10 gear/talents, not a current character snapshot.'
    $clean = $clean -replace '(?m)^seed=\d+\r?$', 'seed=15102026'
    $clean = $clean -replace '(?m)^iterations=\d+\r?$', 'iterations=6000'
    [IO.File]::WriteAllText((Join-Path $dir "recommended-$mode.simc"),$clean,[Text.UTF8Encoding]::new($false))
}
