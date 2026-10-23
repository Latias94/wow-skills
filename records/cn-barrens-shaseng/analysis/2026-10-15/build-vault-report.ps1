$ErrorActionPreference='Stop'
$dir=$PSScriptRoot
$labels=@{H4_ring_318='H4戒指318替换321猎捕手戒';H4_ring_334='H4戒指334替换321猎捕手戒';H4_ring_334_replace_craft='H4戒指334替换331制造戒';H7_trinket_318='H7饰品318替换无底袋';H7_trinket_334='H7饰品334替换无底袋';H4_trinket_334='H4饰品334替换无底袋';Vault_1H334_with_owned1H321='低保单手334＋包内雄狮之爪321';Chest334_keep4pc='低保胸334化生，保留四件套'}
$summary=[ordered]@{date='2026-10-15';vault_status='offered_not_claimed';recommendation=268249;runs=[ordered]@{}}
$sections=foreach($mode in @('raid','dungeon')){
 $j=Get-Content (Join-Path $dir "vault-final-$mode.json") -Raw|ConvertFrom-Json
 $p=$j.sim.players[0];$baseline=$p.collected_data.dps.mean
 $rows=foreach($r in ($j.sim.profilesets.results|Sort-Object mean -Descending)){
  $delta=100*($r.mean/$baseline-1)
  "<tr><td>$($labels[$r.name])</td><td>$($delta.ToString('+0.00;-0.00;0.00'))%</td><td>$([math]::Round($r.mean)) ±$([math]::Round($r.mean_error))</td></tr>"
 }
 $summary.runs[$mode]=[ordered]@{baseline=$baseline;baseline_standard_error=$p.collected_data.dps.mean_std_dev;git=$j.git_revision;dbc=$j.sim.options.dbc;iterations=$j.sim.options.iterations;seed=$j.sim.options.seed;results=$j.sim.profilesets.results}
 $heading=if($mode -eq 'raid'){'团本单体'}else{'大秘境模型'}
 "<section><h2>$heading</h2><p>基准 $([math]::Round($baseline)) DPS；$($j.sim.options.fight_style)，240秒，6000次，seed 15103726。</p><div class='scroll'><table><thead><tr><th>只更换所列装备</th><th>相对当前</th><th>DPS ±95%区间半宽</th></tr></thead><tbody>$($rows -join '')</tbody></table></div><p><a href='vault-final-$mode.json'>原始结果</a> · <a href='vault-$mode.simc'>测试输入（初筛默认，复测覆盖6000次及新种子）</a></p></section>"
}
$html=@"
<!doctype html><html lang='zh-CN'><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><link rel='icon' href='data:,'><title>沙僧 · 10月15日低保选择</title><style>:root{color-scheme:dark}*{box-sizing:border-box}body{background:#111413;color:#e8eee9;font:14px/1.75 'Segoe UI','Microsoft YaHei',sans-serif;margin:0}main{max-width:1000px;margin:auto;padding:30px 24px}h1{font-size:26px}h2{font-size:19px}a{color:#67dfa4}section{padding:18px 0;border-bottom:1px solid #354239}.notice{padding:12px 16px;border-left:3px solid #e3c579;background:#252319}.scroll{overflow:auto}table{border-collapse:collapse;min-width:650px;width:100%}td,th{text-align:left;padding:9px;border-bottom:1px solid #354239}.muted{color:#a6b4aa}.item{display:block;min-height:40px}</style><script>window.whTooltips={colorLinks:false,iconizeLinks:false,renameLinks:false};</script><script src='https://wow.zamimg.com/js/tooltips.js' async></script><main><p class='muted'>贫瘠之地 · 沙僧 · 天神踏风 · 2026-10-15周四低保</p><h1>首选邪恶炼金师指环，减少为H4戒指定向R</h1><p><a class='item' href='https://www.wowhead.com/cn/item=268249' data-wowhead='item=268249&amp;domain=cn&amp;bonus=6652:13668:13334:12849'>邪恶炼金师指环 · 318 · 神话1/6 · 自带插槽</a></p><div class='notice'>建议而非已领取。五件318候选均为神话1/6、目标上限334；279的头／戒不建议。升满模拟不表示当前纹章、金币足够，也不保证领取后立刻获得所列提升。</div><section><h2>为什么选择戒指</h2><p>它仍是新团本戒指之外的另一个目标戒指，大米与团本均有用；不依赖新团本饰品是否掉落。H7饰品是单体备选，当前大米换无底袋收益有限，新触须又是后续大米候选。H4饰品未胜出，武器是单手而非长柄，需与包内单手组成配装，实测未领先。</p><p>升满后替换哪枚戒指按完整配装决定，不能只看装等。当前导出bonus与crafted_stats有冲突，SimC按bonus解析制造戒为暴击急速；请先核对游戏装备面板，再决定是否卸下331制造戒。318立即使用仅测了替换321猎捕手戒，不把334结论直接套用。</p></section><section><h2>本周R币路线更新</h2><p>你现在已装备H8特效头、心和项链，因此H8主要缺长柄268215，不再沿用“头武器心都缺”的旧路线。新团本戒指／触须都缺；一个池多个目标与H8单目标应按实际剩余池比较，不编概率。</p><p>若拿H4戒指：停止为戒指专门R H4；H4肩膀仍有价值，但你已有321套装肩，不能只为肩默认加币。保留低保期间先R也可：如果先R出了同戒指，再比较H7饰品或其他候选；这不是在剩余池未知时默认要求你R H4。</p><p>导出显示晦暗虚空核心3418有1枚，3511为0；不是沿用上周两币，也未记录消费。特效头和心的获取方式未提供，不能由“已装备”推断R池已排除。</p></section>
$($sections -join '')
<section><h2>模型与装备检查</h2><p>使用当前用户导出的实际装备、当前天赋及新增omnium天赋；正式服SimC 3dcabb94dd、12.1.5.70391。包含四件套与两件奥纹美化；胸替代显式维持四件套且化生资格须在游戏内确认。备选单手使用包内雄狮之爪321、双手均附魔和武器油。未强制把现有装备升级，也未改变制造位置。</p><p>Rune of Unleashed Fire仍有触发目标假设的未验证提示；DungeonSlice不是实际路线。饰品、胸、武器的小差异需考虑模拟误差。新增插槽未补宝石，保持当前空槽，故戒指结果未额外计入新宝石收益。历史初筛的胸方案未显式维持四件套，最终仅以本页复测为准。</p></section><p><a href='../2026-10-10/dashboard.html'>完整BiS与获取路线</a> · <a href='update.html'>正式服更新复核</a> · <a href='vault-summary.json'>低保实测摘要</a></p></main></html>
"@
[IO.File]::WriteAllText((Join-Path $dir 'vault.html'),$html,[Text.UTF8Encoding]::new($false))
[IO.File]::WriteAllText((Join-Path $dir 'vault-summary.json'),($summary|ConvertTo-Json -Depth 20),[Text.UTF8Encoding]::new($false))
'Generated vault.html and vault-summary.json'
