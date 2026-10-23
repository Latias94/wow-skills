$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
$slots = @('head','neck','shoulder','back','chest','wrist','hands','waist','legs','feet','finger1','finger2','trinket1','trinket2','main_hand')
$profiles = [ordered]@{}
foreach ($mode in @('raid','dungeon')) {
    $raw = Get-Content (Join-Path $dir "recommended-$mode.simc") -Raw
    $gear = foreach($line in $raw.Split("`n")) {
        if($line -notmatch '^([a-z0-9_]+)=(.*)$' -or $Matches[1] -notin $slots) { continue }
        $slot=$Matches[1]; $parts=$Matches[2].Trim().Split(','); $row=[ordered]@{slot=$slot}
        foreach($part in $parts) { $pair=$part.Split('=',2); if($pair.Count -eq 2){$row[$pair[0]]=$pair[1]} }
        $row
    }
    $profiles[$mode]=[ordered]@{raw=$raw;gear=@($gear)}
}
$bosses=@(
    @{key='h8';name="H8 · Ula'tek";priority='核心';items=@(271875,268215,270175,268265);note='项链已获得并排除；追特效头、长柄、心。拿齐目标后停止，不以清空奖励池为目的。';spec='酒仙候选，实际预览确认';date='当前可打'},
    @{key='new';name="新团本 · Kith'ix";priority='核心候选';items=@(281029,281215,281236);note='大秘境优先戒指与饰品；胸是团本单体候选。新特效模型有未验证提示。';spec='踏风候选，开放后确认';date='计划2026-10-15开放'},
    @{key='h4';name='H4 · Vashnik the Malignant';priority='补齐';items=@(268246,268249,270166);note='肩与戒指仍是目标；不能因新戒指就跳过。270166为池内干扰项示例，未确认为本配装毕业。H4编号以游戏内Boss名核对。';spec='切拾取后的完整池待确认';date='当前可打'},
    @{key='h7';name='H7 · The Coiled Altar';priority='补齐／单体';items=@(268253,268256,268225,270173,268211);note='腰、腿、披风为护甲路线，饰品为单体路线。长柄到手后单手武器价值降低；披风有近似替代。';spec='踏风候选，完整池待确认';date='当前可打'},
    @{key='h2';name='H2 · Entombed Sentinels';priority='备选';items=@(270165);note='单体／大秘境候选复测均未超过当前目标饰品，不建议为补位默认追加R币。';spec='完整池待确认';date='当前可打'},
    @{key='explorers';name='H3 · The Lost Explorers';priority='护甲备选';items=@(268227,270164);note='268227腰带是高手使用且已测的近似替代；无底袋有高手使用，但未超过本次新饰品候选。';spec='完整池待确认';date='当前可打'},
    @{key='h5';name='H5 · Sszorak';priority='护甲备选';items=@(268234,268252);note='手套268234在补测中与目标手套近似持平；戒指268252仅列来源观察，尚未模拟。按实际剩余池判断，不默认追加R币。';spec='完整池待确认';date='当前可打'},
    @{key='h1';name="H1 · Nek'zali the Soulcoiler";priority='未测备选';items=@(268235,268240,268248,268266);note='皮甲胸、护腕、披风、戒指的候选来源，尚未完成全配装对照；不是已确认BiS，也不是完整奖励池。';spec='拾取资格与剩余池待确认';date='当前可打'},
    @{key='h6';name='H6 · The Twin Fangs';priority='未测备选';items=@(268261,268251,270171);note='鞋、项链与饰品来源观察，未完成目标配装对照。鞋可用于移动制造美化位置；已有H8项链时避免仅为填格重复追项链。';spec='拾取资格与剩余池待确认';date='当前可打'},
    @{key='murder';name='密谋小径 · Murder Row';priority='大秘境／低保';items=@(251124,251132,251135);note='手、披风、护腕的替代路线；普通结算不能视为保证获得模拟的神话轨道334。';spec='踏风；低保独立比较';date='当前可打'},
    @{key='dungeon';name='其他地下城戒指';priority='大秘境／低保';items=@(252258,158366);note='新团本前可用旧戒指或制造戒指补位；最终戒指目标为H4＋新团本。具体地下城来源以物品页和游戏手册核对。';spec='来源核对后获取';date='当前候选'},
    @{key='craft';name='制造业';priority='自由补位';items=@(244576,244569,239656,240949,244570,244572,244573);note='不超过两件美化；普通制造戒指／胸可成为第三、第四件制造。位置随实际掉落调整，不能凭高手持有率要求重造。';spec='331，自选属性';date='当前可做'}
)
$ids=@($profiles.Values.gear | ForEach-Object {[int]$_.id; if($_.redirected_base_stats){[int]$_.redirected_base_stats}; if($_.gem_id){$_.gem_id.Split('/') | ForEach-Object {[int]$_}}}) + @($bosses | ForEach-Object {$_.items})
$ids=@(($ids + @(271520)) | Sort-Object -Unique)
$items=[ordered]@{}
$cached=@{}
$existing=Join-Path $dir 'dashboard.html'
if(Test-Path $existing){
    $match=[regex]::Match((Get-Content $existing -Raw),'<script id="report-data" type="application/json">(.*?)</script>',[Text.RegularExpressions.RegexOptions]::Singleline)
    if($match.Success){$old=$match.Groups[1].Value | ConvertFrom-Json;foreach($p in $old.items.PSObject.Properties){if($p.Value.icon){$cached[$p.Name]=$p.Value}}}
}
foreach($id in $ids) {
    if($cached.ContainsKey("$id")){$items["$id"]=$cached["$id"];continue}
    try {
        $endpoint=if($id -ge 281000){'https://nether.wowhead.com/ptr-2/tooltip/item/'}else{'https://nether.wowhead.com/tooltip/item/'}
        $t=Invoke-RestMethod "${endpoint}${id}?locale=4" -TimeoutSec 12
        $iconUrl="https://wow.zamimg.com/images/wow/icons/large/$($t.icon).jpg"
        $bytes=(Invoke-WebRequest $iconUrl -TimeoutSec 12).RawContentStream.ToArray()
        $items["$id"]=[ordered]@{name=$t.name;icon="data:image/jpeg;base64,$([Convert]::ToBase64String($bytes))";iconUrl=$iconUrl;tooltip=$t.tooltip}
        Write-Output "Cached item $id $($t.name)"
    } catch {
        $items["$id"]=[ordered]@{name="物品 $id";icon=$null;tooltip=$null;error=$_.Exception.Message}
        Write-Warning "Item $id unavailable; using fallback"
    }
}
$runs=[ordered]@{}
$liveItemIds=@()
$liveSnapshot=Join-Path (Split-Path $dir) '2026-10-15/wowhead-live-items.json'
if(Test-Path $liveSnapshot){
    foreach($live in (Get-Content $liveSnapshot -Raw|ConvertFrom-Json)){
        $key=[string]$live.id
        if($items.Contains($key)){
            $items[$key].name=$live.name
            $items[$key].tooltip=$live.tooltip
            $liveItemIds+=[int]$live.id
        }
    }
}
foreach($name in @('practical-raid','practical-dungeon','wcl-verify-raid','wcl-verify-dungeon','wcl-recheck-raid','wcl-recheck-dungeon')) {
    $j=Get-Content (Join-Path $dir "$name.json") -Raw | ConvertFrom-Json
    $p=$j.sim.players[0]
    $runs[$name]=[ordered]@{baseline=$p.collected_data.dps.mean;stderr=$p.collected_data.dps.mean_std_dev;iterations=$j.sim.options.iterations;seed=$j.sim.options.seed;model=$j.sim.options.fight_style;seconds=$j.sim.options.max_time;results=$j.sim.profilesets.results}
}
$stats=[ordered]@{}
foreach($mode in @('raid','dungeon')){
    $j=Get-Content (Join-Path $dir "unbuffed-recommended-$mode.json") -Raw | ConvertFrom-Json
    $stats[$mode]=$j.sim.players[0].collected_data.buffed_stats.stats | Select-Object crit_rating,haste_rating,mastery_rating,versatility_rating
}
$vault=@(
    @{key='waist';label='H3腰带：低保优先补位';items=@(268227);priority='优先补缺';reason='已测接近目标腰带。H3目前关注腰带；无底袋不是最终大秘境饰品目标，没必要只为这条腰带主动追加R。';condition='缺神话腰带，低保版本能达到目标轨道，且没有更大的武器／核心特效提升时可拿。';route='取消为H3腰带追加R的计划；腰带槽补齐后降低H7腰带的目标价值。';limit='不是独有BiS，H7腰带／制造腰带仍可替代。'},
    @{key='hands';label='H5／密谋手套：低保优先补位';items=@(268234,251124,271520);priority='优先补缺';reason='H5手套、密谋手套及套装手均有实测近似替代依据。H5戒指未证明是最终目标，不为单独补手盲目追加R。';condition='缺神话手套；换装后保留四件套，或有资源且预览确认可以化生。其他低保没有更强核心提升时可拿。';route='不再为H5手套专门R，也不必强求密谋指定手套；接受已测近似来源。';limit='不同来源不是同一件装备；以实际属性、宝石孔和整套模拟决定。'},
    @{key='cloak';label='密谋／H7披风：接受低保替代';items=@(251132,268253);priority='优先补缺';reason='密谋披风已测与目标接近；H7披风是目标路线。若H7只剩披风有价值，确定的低保可避免为这一个部位赌池。';condition='缺神话披风，且当前最终方案没有把披风设为美化位；有更强武器／特效提升时仍要比较。';route='补齐披风后移除为该槽专门R H7的需求；护腕＋鞋美化路线可继续保留。';limit='若改做披风美化，不应再为重复的披风槽优先拿低保。'},
    @{key='h7armor';label='H7腰／腿：只缺一件时低保截取';items=@(268256,268225);priority='按剩余目标';reason='两件都是目标护甲，但H7还可能有披风、单体饰品等价值。不能把当前H7一概视为低收益池。';condition='低保出现缺少的神话目标且不破四件套；如果H7其余目标已齐，只追这件时更适合直接拿。';route='更新H7目标清单；只有剩余有效目标不足以支撑R时才停，并非拿一件就无条件停。';limit='单体饰品270173在团本有价值；大米新饰品到手后它不是必追目标。'},
    @{key='h4';label='H4肩／戒：只剩一个目标时可拿';items=@(268246,268249);priority='按剩余目标';reason='肩膀和戒指都在目标配装，未来新戒指并不替代第二个戒指位置。若已拿其中一件，低保出另一件可减少定向R需求。';condition='神话轨道且确实替换缺口；肩膀需核对化生，戒指比较两枚现有戒指而非只比较一个槽。';route='两个目标齐后停止为这套目标R H4；未齐前按实际剩余池继续比较H7。';limit='H4仍有多个目标时不能声称只有一个有用；需核对Boss名称和实际拾取池。'},
    @{key='core';label='H8核心：低保有出同样要优先比较';items=@(268215,271875,270175);priority='核心优先';reason='武器、特效头、心是核心缺口。不要为了省一次补护甲的R，放弃明显更大的核心提升。';condition='低保实际能提供该物品，轨道及效果bonus正确且仍缺；与本周其他候选做完整配装比较。';route='拿到后该目标不再需要专门R；其余核心仍缺时，H8继续保持优先。';limit='这里只给遇到时的选择建议，不保证低保能开出；项链268265已拥有，不列入。'},
    @{key='new';label='新团本目标：开放后再比较';items=@(281029,281215,281236);priority='未来候选';reason='戒指／饰品对应大米候选，胸偏团本单体。若未来低保能出且符合目标，可减少新团本定向R需求。';condition='2026-10-15计划开放之后，确认实际低保资格、版本及特效实现；不是本周已存在的选项。';route='按获得结果移除追逐目标；大米戒指＋饰品齐后不为单体胸默认继续清池。';limit='新特效尚有模型局限，不能作为无条件秒选承诺。'}
)
$data=[ordered]@{date='2026-10-10';profiles=$profiles;bosses=$bosses;items=$items;runs=$runs;stats=$stats;vault=$vault;liveItemIds=$liveItemIds;sample=(Get-Content (Join-Path $dir 'wcl-top5-evidence.json') -Raw | ConvertFrom-Json)}
$json=($data | ConvertTo-Json -Depth 20 -Compress).Replace('</','<\/')
$template=Get-Content (Join-Path $dir 'dashboard.template.html') -Raw
$html=$template.Replace('__REPORT_DATA__',$json)
[IO.File]::WriteAllText((Join-Path $dir 'dashboard.html'),$html,[Text.UTF8Encoding]::new($false))
Write-Output 'Generated standalone dashboard.html'
