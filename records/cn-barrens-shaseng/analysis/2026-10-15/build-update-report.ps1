$ErrorActionPreference='Stop'
$dir=$PSScriptRoot
$encode={param($s) [Net.WebUtility]::HtmlEncode([string]$s)}
$items=Get-Content (Join-Path $dir 'wowhead-live-items.json') -Raw|ConvertFrom-Json
$oldHtml=Get-Content (Join-Path (Split-Path $dir) '2026-10-10/dashboard.html') -Raw
$oldData=[regex]::Match($oldHtml,'<script id="report-data" type="application/json">(.*?)</script>','Singleline').Groups[1].Value|ConvertFrom-Json
$labels=@{Alternative_neck_13708='另一项链属性版本（非当前已有版）';Haste_mastery_crafts='腕鞋改急速精通';Old_chest='新胸换普通套装胸';New_chest='普通胸换新胸';New_passive='H7饰品换新触须';H7_passive='新触须换H7饰品';Haste_flask='改急速合剂';Crit_flask='改暴击合剂';Old_ring_Atroxus='新戒指换旧273792戒指';Crafted_ring_CM='新戒指换331制造暴击精通戒指'}
$summaries=[ordered]@{}
$tables=foreach($mode in @('raid','dungeon')){
    $j=Get-Content (Join-Path $dir "live-$mode.json") -Raw|ConvertFrom-Json
    if($j.git_revision -ne '3dcabb94dd'){throw "Unexpected build revision $($j.git_revision)"}
    if($j.sim.options.dbc.version_used -ne 'Live'){throw 'Expected live data'}
    $p=$j.sim.players[0];$baseline=$p.collected_data.dps.mean
    $rows=foreach($r in $j.sim.profilesets.results){
        $delta=100*($r.mean/$baseline-1)
        "<tr><td>$(& $encode $labels[$r.name])</td><td>$([math]::Round($r.mean).ToString('N0'))</td><td>$($delta.ToString('+0.00;-0.00;0.00'))%</td><td>±$([math]::Round($r.mean_error,1))</td></tr>"
    }
    $summaries[$mode]=[ordered]@{baseline=$baseline;baseline_standard_error=$p.collected_data.dps.mean_std_dev;iterations=$j.sim.options.iterations;seed=$j.sim.options.seed;dbc=$j.sim.options.dbc;git_revision=$j.git_revision;results=$j.sim.profilesets.results;warnings=$j.notifications}
    $heading=if($mode -eq 'raid'){'团本单体 · 新胸＋H7饰品'}else{'大秘境 · 普通胸＋新触须'}
    "<section><h2>$heading</h2><p>基准 $([math]::Round($baseline).ToString('N0')) DPS；$($j.sim.options.fight_style)，$($j.sim.options.max_time)秒，6000次迭代，seed 15102026。</p><div class='scroll'><table><thead><tr><th>相对基准改动</th><th>DPS</th><th>变化</th><th>95%区间半宽</th></tr></thead><tbody>$($rows -join '')</tbody></table></div><p class='muted'>小差距需结合误差比较；误差重叠不证明等效。不同模式DPS不能横比。</p><a href='recommended-$mode.simc' download>下载正式服模式配装 SimC</a> · <a href='live-$mode.json'>原始结果 JSON</a></section>"
}
$cards=foreach($i in $items){
    $plain=[Net.WebUtility]::HtmlDecode(($i.tooltip -replace '<[^>]+>',' ')) -replace '\s+',' '
    $cachedIcon=$oldData.items."$($i.id)".icon
    "<article><h3><a href='https://www.wowhead.com/cn/item=$($i.id)' data-wowhead='item=$($i.id)&amp;domain=cn&amp;ilvl=334'><img src='$cachedIcon' alt='' width='32' height='32' style='vertical-align:middle;margin-right:10px;border-radius:3px'>$(& $encode $i.name)</a></h3><p class='muted'>ID $($i.id) · 正式服简体中文 · 对照装等334</p><p>$(& $encode $plain)</p></article>"
}
$summary=[ordered]@{checked_at=(Get-Date).ToString('o');source_commit='3dcabb94dd32f786786c67541dfd10db9f39e43b';previous_commit='71a76b73cc';character_snapshot_date='2026-10-10';runs=$summaries}
[IO.File]::WriteAllText((Join-Path $dir 'update-summary.json'),($summary|ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
$html=@"
<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link rel="icon" href="data:,"><title>沙僧 · 10月15日正式服复核</title>
<style>:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#111413;color:#e8eee9;font:14px/1.75 'Segoe UI','Microsoft YaHei',sans-serif}main{max-width:1100px;margin:auto;padding:30px 24px}h1{font-size:27px}h2{font-size:20px}h3{font-size:16px}a{color:#67dfa4}p{overflow-wrap:anywhere}.muted{color:#a6b4aa}section{padding:20px 0;border-bottom:1px solid #354239}article{padding:12px 0;border-bottom:1px solid #29372f}.notice{border-left:3px solid #e3c579;padding:10px 16px;background:#252319;color:#e3d8b9}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;min-width:620px}td,th{text-align:left;border-bottom:1px solid #354239;padding:9px}td:not(:first-child){font-variant-numeric:tabular-nums}a:focus-visible{outline:2px solid #67dfa4}a[data-wowhead]{display:block;min-height:32px}</style>
<script>window.whTooltips={colorLinks:false,iconizeLinks:false,renameLinks:false};</script><script src="https://wow.zamimg.com/js/tooltips.js" async></script><main>
<p class="muted">贫瘠之地 · 沙僧 · 天神踏风</p><h1>2026年10月15日 · 新团本正式服数据复核</h1>
<p>SimC 已更新到 3dcabb94dd，正式服 12.1.5.70391，数据热修 2026-10-14。保留原天赋与可达334掉落／331制造边界。</p>
<div class="notice">这是10月10日目标配装的更新复测，不是10月15日角色装备、低保、R币余额或团本开放状态的实时记录。旧档案不自动成为本周事实。</div>
<section><h2>数据变化与边界</h2><p>三件目标已能从Wowhead正式服读取简体中文，统一334装等的主要属性与效果数值和旧PTR快照一致。这里只核对踏风三件已知目标，不是完整Boss拾取池。Wowhead普通掉落率不能作为R币概率。</p><p>新戒指及新胸的SimC代码仍提示群伤假定不分摊；触须新目标触发已有实现，但DungeonSlice不代表实际副本路线。进入正式服数据库不等于所有机制已验证。</p>$($cards -join '')</section>
$($tables -join '')
<section><h2>获取路线如何处理</h2><p>在这些受控模型内继续保留两套候选：大秘境用新戒指＋触须；团本用新胸＋H7饰品。新装备机制限制仍需保留，不据微小差距宣称全局BiS。</p><p>H8未齐的核心、新团本戒指／饰品仍是追逐方向；H4戒指是另一个戒指位，不因新戒指而淘汰。低保优先截取单目标缺口的原则继续适用。实际分配需要本周余额、已获取装备与奖励预览。</p></section>
<p><a href="../2026-10-10/dashboard.html">返回完整装备报告与低保建议</a> · <a href="wowhead-live-items.json">Wowhead原始快照</a> · <a href="update-summary.json">复测摘要</a> · <a href="https://github.com/simulationcraft/simc/commit/3dcabb94dd32f786786c67541dfd10db9f39e43b">SimC提交</a></p></main></html>
"@
[IO.File]::WriteAllText((Join-Path $dir 'update.html'),$html,[Text.UTF8Encoding]::new($false))
'Generated update.html and update-summary.json'
