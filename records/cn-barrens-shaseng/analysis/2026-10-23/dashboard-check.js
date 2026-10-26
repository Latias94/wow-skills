
    'use strict';
    (() => {
      const $ = id => document.getElementById(id);
      const list = value => Array.isArray(value) ? value : [];
      const record = value => value !== null && typeof value === 'object' && !Array.isArray(value) ? value : {};
      const present = value => value !== undefined && value !== null && value !== '';
      const numeric = value => (typeof value === 'number' || typeof value === 'string' && value.trim() !== '') && Number.isFinite(Number(value)) ? Number(value) : null;
      const numberText = value => {
        const number = numeric(value);
        return number === null ? '未提供' : number.toLocaleString('zh-CN', { maximumFractionDigits: 2 });
      };
      const display = value => {
        if (!present(value)) return '未提供';
        if (typeof value === 'boolean') return value ? '是' : '否';
        if (typeof value === 'object') return JSON.stringify(value, null, 2);
        return String(value);
      };
      const node = (tag, className, text) => {
        const element = document.createElement(tag);
        if (className) element.className = className;
        if (text !== undefined) element.textContent = text;
        return element;
      };
      const empty = text => node('p', 'empty', text);
      const replace = (id, ...children) => $(id).replaceChildren(...children);
      const modeLabel = value => ({ raid: '团本', dungeon: '大秘境' })[value] || display(value);
      const stageLabel = value => ({ screen: '初筛', verify: '复测', current: '当前实装', target: '目标配装', targets: '目标初筛', practical: '当前装改进', upgrade: '目标装升级', 'upgrade-current': '当前装升级', weapons: '武器与制造升级', refine: '细化优化' })[value] || display(value);
      const slotLabels = { head: '头部', neck: '项链', shoulder: '肩部', shoulders: '肩部', back: '披风', chest: '胸部', wrist: '护腕', wrists: '护腕', hands: '手套', waist: '腰带', legs: '腿部', feet: '鞋', finger1: '戒指一', finger2: '戒指二', trinket1: '饰品一', trinket2: '饰品二', main_hand: '主手武器', off_hand: '副手武器' };
      const fieldLabels = { date: '报告日期', patch: '版本', character: '角色', engine_commit: '模拟器提交', wow_version: '游戏 / 引擎版本', hotfix_date: '热修日期', snapshot: '快照口径', budget: 'R币预算', scope: '研究 / 样本范围', average_ilevel: '当前平均装等', catalyst_charges: '化生次数', sockets: '孔位记录', empty_sockets: '现有空孔', armor_upgrade_track: '护甲升级轨道', upgrade_materials: '特殊强化材料', historical_wcl: 'WCL 历史样本', wcl_review: '本次日志复盘', flask: '合剂', food: '食物', potion: '药水', augmentation: '符文', augment_rune: '符文', temporary_enchant: '临时附魔', weapon_oil: '武器油', oil: '武器油', bloodlust: '嗜血', buffs: '增益', note: '说明' };
      const facts = entries => {
        const dl = node('dl', 'facts');
        for (const [key, value] of entries) dl.append(node('dt', '', fieldLabels[key] || key), node('dd', '', display(value)));
        return dl;
      };
      const state = { mode: '', D: {}, runs: [], owned: new Set() };
      let feedbackTimer;
      function feedback(message) {
        clearTimeout(feedbackTimer);
        $('feedback').textContent = '';
        feedbackTimer = setTimeout(() => { $('feedback').textContent = message; }, 30);
      }
      function item(id) { return record(record(state.D.items)[String(id)]); }
      function itemName(id) { return present(item(id).name) ? display(item(id).name) : '物品 #' + display(id); }
      function validItemID(id) { return /^\d+$/.test(String(id)) && Number(id) > 0; }
      function ids(value) {
        const values = Array.isArray(value) ? value : present(value) ? String(value).split(/[/:,\s]+/) : [];
        return [...new Set(values.filter(validItemID).map(String))];
      }
      function bonusValue(value) { return ids(value).join(':'); }
      function itemLink(id, gear, className = '') {
        if (!validItemID(id)) return node('span', className, itemName(id));
        const link = node('a', className, itemName(id));
        const params = new URLSearchParams({ item: String(id), domain: 'cn' });
        if (gear && numeric(gear.ilevel) > 0) params.set('ilvl', String(gear.ilevel));
        if (gear && bonusValue(gear.bonus_id)) params.set('bonus', bonusValue(gear.bonus_id));
        link.href = 'https://www.wowhead.com/cn/item=' + encodeURIComponent(String(id));
        const query = [];
        if (params.has('ilvl')) query.push('ilvl=' + encodeURIComponent(params.get('ilvl')));
        if (params.has('bonus')) query.push('bonus=' + params.get('bonus'));
        if (query.length) link.href += '?' + query.join('&');
        link.dataset.wowhead = Array.from(params, ([key, value]) => key + '=' + value).join('&');
        link.dataset.whIconAdded = 'true';
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        return link;
      }
      function itemIcon(id) {
        const wrapper = node('span', 'item-icon', '物');
        wrapper.setAttribute('aria-hidden', 'true');
        const source = item(id).icon;
        if (typeof source === 'string' && /^data:image\//i.test(source)) {
          const image = node('img');
          image.alt = '';
          image.width = 44;
          image.height = 44;
          image.loading = 'lazy';
          image.addEventListener('error', () => image.remove(), { once: true });
          image.src = source;
          wrapper.append(image);
        }
        return wrapper;
      }
      function refreshTooltips() {
        if (typeof window.$WowheadPower?.refreshLinks === 'function') {
          try { window.$WowheadPower.refreshLinks(); } catch { /* Optional network enhancement. */ }
        }
      }
      function renderGear(rootID, value, current = false) {
        const root = $(rootID);
        root.replaceChildren();
        const gear = list(value);
        if (!gear.length) { root.append(empty('未提供这套装备的逐槽记录。')); return; }
        for (const rawGear of gear) {
          const g = record(rawGear);
          const row = node('article', 'gear-row');
          const main = node('div');
          const top = node('div', 'gear-top');
          const owned = g.owned === true || current && g.owned !== false;
          top.append(node('span', '', slotLabels[g.slot] || display(g.slot)), node('span', 'ilevel', '装等 ' + numberText(g.ilevel)));
          const name = itemLink(g.id, g, 'item-name');
          if (name.tagName === 'A') name.setAttribute('aria-label', (slotLabels[g.slot] || display(g.slot)) + '：' + itemName(g.id) + '，装等 ' + numberText(g.ilevel) + '，中文正式服物品页（新窗口）');
          main.append(top, name);
          const statusLine = node('div', 'item-detail');
          statusLine.append(node('span', 'tag' + (owned ? ' green' : ''), owned ? '已拥有' : g.owned === false ? '未拥有' : '拥有状态未记录'), node('span', '', ' ID ' + display(g.id)));
          main.append(statusLine);
          const source = present(g.source) ? g.source : item(g.id).source;
          if (present(source)) main.append(node('p', 'item-detail', '来源：' + display(source)));
          if (present(g.note)) main.append(node('p', 'item-detail', display(g.note)));
          const modifiers = [];
          if (present(g.bonus_id)) modifiers.push('bonus：' + display(g.bonus_id));
          if (present(g.enchant_id)) modifiers.push('附魔：' + display(g.enchant_id));
          if (present(g.crafted_stats)) modifiers.push('制造属性：' + display(g.crafted_stats));
          if (present(g.redirected_base_stats)) modifiers.push('基础属性重定向：' + display(g.redirected_base_stats));
          if (modifiers.length) main.append(node('p', 'item-detail mono', modifiers.join(' · ')));
          const gems = ids(g.gem_id);
          if (gems.length) {
            const mods = node('div', 'mods');
            for (const id of gems) {
              const gem = itemLink(id, null, 'gem');
              gem.replaceChildren(itemIcon(id), node('span', '', itemName(id)));
              gem.setAttribute('aria-label', '宝石：' + itemName(id) + '（新窗口）');
              mods.append(gem);
            }
            main.append(mods);
          }
          if (present(item(g.id).tooltip)) {
            const detail = node('details', 'offline-tip');
            detail.append(node('summary', '', '离线物品说明'), node('pre', '', display(item(g.id).tooltip)));
            main.append(detail);
          }
          row.append(itemIcon(g.id), main);
          root.append(row);
        }
      }
      function setRaw(kind, value) {
        const raw = typeof value === 'string' ? value : '';
        $(kind + '-raw').value = raw;
        $(kind + '-raw').placeholder = '未提供 SimC 原文。';
        document.querySelectorAll('[data-export="' + kind + '"]').forEach(button => { button.disabled = !raw.trim(); });
      }
      function renderMetadata() {
        const meta = record(state.D.meta);
        const character = typeof meta.character === 'string' ? meta.character : '沙僧';
        const patch = present(meta.patch) ? display(meta.patch) : '版本未记录';
        $('report-title').textContent = character + ' · ' + patch + ' 装备实验室';
        document.title = character + ' · ' + patch + ' 第二周装备实验室';
        const tags = [['日期', meta.date], ['版本', meta.wow_version], ['热修', meta.hotfix_date]];
        replace('meta-strip', ...tags.map(([label, value]) => node('span', 'tag', label + ' ' + display(value))));
        const metadata = facts(Object.keys(fieldLabels).filter(key => Object.prototype.hasOwnProperty.call(meta, key)).map(key => [key, meta[key]]));
        $('metadata').replaceChildren(...metadata.childNodes);
        const budget = numeric(meta.budget);
        const budgetText = budget === null ? display(meta.budget) : numberText(budget) + ' 枚';
        const metrics = [
          [budgetText, '本次 R币预算'],
          [String(list(record(state.D.current).gear).length) + ' 槽', '当前装备记录'],
          [String(state.runs.length) + ' 批', '已记录模拟批次'],
          [String(['raid', 'dungeon'].filter(key => Object.prototype.hasOwnProperty.call(record(state.D.profiles), key)).length) + ' 套', '已提供目标配装']
        ];
        replace('metrics', ...metrics.map(([value, label]) => {
          const metric = node('div', 'metric');
          metric.append(node('strong', '', value), node('span', '', label));
          return metric;
        }));
        $('footer-meta').textContent = character + ' · ' + display(meta.date) + ' · ' + patch + ' · 引擎 ' + display(meta.engine_commit) + ' · 游戏版本 ' + display(meta.wow_version);
        $('budget-tag').textContent = '预算 ' + budgetText;
        $('budget-notice').textContent = budget === 0
          ? '本次快照预算为 0 枚：以下为后续获取与停止条件参考，本次没有可分配的 R币。页面不会生成消费安排。'
          : budget === null
            ? '预算按嵌入记录展示；没有明确可用枚数时，不生成消费次数或分配建议。'
            : '本次快照预算为 ' + budgetText + '。路线优先级与停止条件来自分析记录；目标清单本身不代表完整奖励池。';
        const snapshot = meta.snapshot;
        if (snapshot && typeof snapshot === 'object' && !Array.isArray(snapshot)) {
          replace('current-snapshot', facts(Object.entries(snapshot)));
          $('current-snapshot').style.marginBottom = '18px';
        } else {
          replace('current-snapshot', present(snapshot) ? node('p', 'small', display(snapshot)) : node('p', 'small', '未提供额外的实装、孔位与资源快照。'));
        }
      }
      function renderTextList(id, value, fallback, ordered = false) {
        const values = list(value).filter(present);
        if (!values.length) { replace(id, empty(fallback)); return; }
        const root = node(ordered ? 'ol' : 'ul', ordered ? 'conclusions' : 'limitations');
        root.append(...values.map(text => node('li', '', display(text))));
        replace(id, root);
      }
      function renderProfile() {
        const profile = record(record(state.D.profiles)[state.mode]);
        document.querySelectorAll('[data-profile]').forEach(button => {
          button.disabled = !Object.prototype.hasOwnProperty.call(record(state.D.profiles), button.dataset.profile);
          button.setAttribute('aria-pressed', String(button.dataset.profile === state.mode));
        });
        $('profile-description').textContent = profile.note || (state.mode ? modeLabel(state.mode) + ' · 已提供的目标配置，不自动认定为全局最优或已获得。' : '尚未提供团本或大秘境目标配置。');
        renderGear('target-gear', profile.gear);
        $('stats-title').textContent = (state.mode ? modeLabel(state.mode) + ' · ' : '') + '无消耗品属性等级';
        const fields = [['crit_rating', '暴击'], ['haste_rating', '急速'], ['mastery_rating', '精通'], ['versatility_rating', '全能']];
        const stats = record(profile.stats);
        const total = fields.reduce((sum, [key]) => sum + Math.max(0, numeric(stats[key]) ?? 0), 0);
        const root = $('stats');
        root.replaceChildren();
        for (const [key, label] of fields) {
          const stat = node('div', 'stat');
          const line = node('div', 'stat-label');
          line.append(node('span', '', label), node('b', '', numberText(stats[key])));
          const track = node('div', 'track');
          track.setAttribute('aria-hidden', 'true');
          const bar = node('span');
          bar.style.width = (total ? Math.max(0, numeric(stats[key]) ?? 0) / total * 100 : 0) + '%';
          track.append(bar);
          stat.append(line, track);
          root.append(stat);
        }
        if (profile.stats_context) root.append(node('p', 'small', profile.stats_context));
        const consumables = profile.consumables;
        replace('consumables', consumables && typeof consumables === 'object' && !Array.isArray(consumables)
          ? Object.keys(consumables).length ? facts(Object.entries(consumables)) : empty('未提供消耗品口径。')
          : present(consumables) ? node('p', 'small', display(consumables)) : empty('未提供消耗品口径。'));
        setRaw('target', profile.raw);
        $('target-raw-summary').textContent = '查看、复制或下载' + (state.mode ? modeLabel(state.mode) : '目标') + ' SimC 原文';
        $('target-raw-label').textContent = (state.mode ? modeLabel(state.mode) : '目标') + '配置 · 原文只读';
        refreshTooltips();
      }
      function signed(value, digits = 2) {
        return (value > 0 ? '+' : '') + value.toLocaleString('zh-CN', { minimumFractionDigits: digits, maximumFractionDigits: digits });
      }
      function intervalText(mean, halfWidth) {
        return '[' + numberText(mean - halfWidth) + ', ' + numberText(mean + halfWidth) + ']';
      }
      function setupRunFilters() {
        const modes = [...new Set(state.runs.map(run => run.mode).filter(present))];
        for (const mode of modes) {
          const option = node('option', '', modeLabel(mode));
          option.value = String(mode);
          $('run-mode').append(option);
        }
        updateStageOptions();
      }
      function updateStageOptions() {
        const previous = $('run-stage').value;
        const mode = $('run-mode').value;
        const stages = [...new Set(state.runs.filter(run => !mode || String(run.mode) === mode).map(run => run.stage).filter(present))];
        replace('run-stage', node('option', '', '全部阶段'));
        $('run-stage').firstChild.value = '';
        for (const stage of stages) {
          const option = node('option', '', stageLabel(stage));
          option.value = String(stage);
          $('run-stage').append(option);
        }
        if (stages.some(stage => String(stage) === previous)) $('run-stage').value = previous;
      }
      function resultRow(result, baseline, baselineError, isBaseline = false) {
        const r = record(result);
        const row = node('tr', isBaseline ? 'baseline-row' : '');
        const label = node('th', '', isBaseline ? '本批次基准' : display(present(r.label) ? r.label : r.name));
        label.scope = 'row';
        if (r.provisional) label.append(node('br'), node('span', 'tag gold', '暂定 / 待验证'));
        const mean = numeric(r.mean);
        const error = numeric(r.error);
        const validError = error !== null && error >= 0;
        const meanCell = node('td', 'num', mean === null ? '未提供' : numberText(mean));
        const errorCell = node('td', 'num', validError ? '± ' + numberText(error) : '未提供');
        if (mean !== null && validError) errorCell.append(node('span', 'interval-note mono', intervalText(mean, error)));
        const deltaCell = node('td', 'num');
        const intervalCell = node('td', 'num');
        const assessment = node('td', 'small');
        if (isBaseline) {
          deltaCell.textContent = '0.00 / 0.00%';
          intervalCell.textContent = '—';
          assessment.textContent = '本批次参照';
        } else if (mean === null || baseline === null) {
          deltaCell.textContent = '无法计算';
          intervalCell.textContent = '未提供';
          assessment.textContent = '缺少均值或基准';
        } else {
          const delta = mean - baseline;
          deltaCell.textContent = signed(delta) + (baseline > 0 ? ' / ' + signed(delta / baseline * 100) + '%' : ' / 百分比不可用');
          if (validError && baselineError !== null) {
            // Combine reported 95% half-widths under an independence approximation.
            const combined = Math.hypot(error, baselineError);
            intervalCell.textContent = intervalText(delta, combined);
            const overlaps = Math.abs(delta) <= combined;
            const direction = overlaps ? 'neutral' : delta > 0 ? 'positive' : 'negative';
            deltaCell.classList.add(direction);
            assessment.textContent = overlaps ? '近似区间含0' : delta > 0 ? '近似区间全为正' : '近似区间全为负';
            assessment.classList.add(direction);
          } else {
            intervalCell.textContent = '未提供';
            assessment.textContent = '误差不全，不判断';
          }
          if (r.provisional) assessment.append(node('br'), node('span', '', '结论仍属暂定'));
        }
        row.append(label, meanCell, errorCell, deltaCell, intervalCell, assessment);
        return row;
      }
      function renderRuns() {
        const mode = $('run-mode').value;
        const stage = $('run-stage').value;
        const runs = state.runs.filter(run => (!mode || String(run.mode) === mode) && (!stage || String(run.stage) === stage));
        $('run-count').textContent = '显示 ' + runs.length + ' / ' + state.runs.length + ' 批次 · ' + runs.reduce((sum, run) => sum + list(run.results).length, 0) + ' 条候选';
        const root = $('runs');
        root.replaceChildren();
        if (!runs.length) { root.append(empty(state.runs.length ? '当前筛选下没有已记录的模拟。' : '尚未提供模拟批次；本页不填入示例结果。')); return; }
        runs.forEach(run => {
          const article = node('article', 'run');
          const head = node('div', 'run-head');
          head.append(node('h3', '', display(present(run.label) ? run.label : run.key)));
          const tags = node('div');
          tags.append(node('span', 'tag green', modeLabel(run.mode)), node('span', 'tag gold', stageLabel(run.stage)));
          head.append(tags);
          const metadata = node('div', 'run-meta');
          for (const [label, value] of [['批次', run.key], ['模型', run.model], ['时长（秒）', run.seconds], ['迭代', run.iterations], ['种子', run.seed]]) metadata.append(node('span', '', label + ' ' + display(value)));
          article.append(head, metadata);
          const table = node('table');
          table.append(node('caption', '', '均值单位为 DPS；误差与差值区间单位为 DPS。差值由本表均值减基准计算，百分比以本批次基准为分母。'));
          const thead = node('thead');
          const header = node('tr');
          for (const label of ['配置 / 候选', '平均 DPS', '均值95%误差 / 区间', '相对基准 DPS / %', '差值95%区间（近似）', '区间说明']) {
            const th = node('th', '', label);
            th.scope = 'col';
            header.append(th);
          }
          thead.append(header);
          const tbody = node('tbody');
          const baseline = numeric(run.baseline);
          const stderr = numeric(run.stderr);
          const baselineError = stderr !== null && stderr >= 0 ? 1.96 * stderr : null;
          tbody.append(resultRow({ mean: run.baseline, error: baselineError }, baseline, baselineError, true));
          for (const result of list(run.results)) tbody.append(resultRow(result, baseline, baselineError));
          table.append(thead, tbody);
          const scroll = node('div', 'table-scroll');
          scroll.tabIndex = 0;
          scroll.setAttribute('role', 'region');
          scroll.setAttribute('aria-label', display(run.label || run.key) + '结果表，可横向滚动');
          scroll.append(table);
          article.append(scroll);
          if (!list(run.results).length) article.append(node('p', 'small', '本批次仅记录基准，未提供候选结果。'));
          const suppliedDeltas = list(run.results).filter(result => present(record(result).delta));
          if (suppliedDeltas.length) {
            const details = node('details');
            details.append(node('summary', '', '生成器记录的 delta 原值（不推定单位）'), facts(suppliedDeltas.map(result => [display(result.label || result.name), result.delta])));
            article.append(details);
          }
          root.append(article);
        });
      }
      function routeItems(value) {
        const values = ids(value);
        if (!values.length) return node('p', 'small', '无记录');
        const ul = node('ul', 'item-list');
        for (const id of values) {
          const li = node('li');
          li.append(itemLink(id), node('span', 'small mono', ' #' + id));
          ul.append(li);
        }
        return ul;
      }
      function renderRoutes() {
        const root = $('routes');
        root.replaceChildren();
        const routes = list(state.D.routes);
        if (!routes.length) { root.append(empty('未提供本次获取路线；不沿用历史消费建议。')); return; }
        routes.forEach((rawRoute, index) => {
          const route = record(rawRoute);
          const excluded = new Set(ids(route.excluded));
          const targets = ids(route.targets);
          const owned = targets.filter(id => state.owned.has(id));
          const pending = targets.filter(id => !state.owned.has(id) && !excluded.has(id));
          const article = node('article', 'route');
          const heading = node('div', 'route-heading');
          heading.append(node('p', 'route-rank', String(index + 1).padStart(2, '0') + ' / ROUTE'), node('h3', '', display(route.boss)));
          if (present(route.priority)) heading.append(node('span', 'tag gold', '优先级 ' + display(route.priority)));
          if (present(route.spec)) heading.append(node('span', 'tag', '拾取 ' + display(route.spec)));
          const body = node('div');
          if (present(route.note)) body.append(node('p', 'small', display(route.note)));
          const groups = node('div', 'route-groups');
          for (const [label, values] of [['待补齐 / 拥有未确认', pending], ['已拥有目标', owned], ['已R排除（独立记录）', [...excluded]]]) {
            const group = node('div', 'route-group');
            group.append(node('h4', '', label + ' · ' + values.length), routeItems(values));
            groups.append(group);
          }
          body.append(groups);
          const stop = typeof route.stop === 'boolean' ? route.stop ? '已标记停止' : '未标记停止；具体条件未提供' : display(route.stop);
          body.append(node('p', 'route-stop', '停止条件：' + stop));
          article.append(heading, body);
          root.append(article);
        });
        refreshTooltips();
      }
      function sourceLink(source) {
        const title = present(source.title) ? display(source.title) : '未命名来源';
        if (typeof source.url !== 'string' || !source.url.trim()) return node('span', '', title + '（未提供链接）');
        const raw = source.url.trim();
        // Allow web links and relative evidence files, but never executable URL schemes.
        const hasScheme = /^[a-z][a-z\d+.-]*:/i.test(raw);
        if (/^\/\//.test(raw) || hasScheme && !/^https?:\/\//i.test(raw)) return node('span', '', title + '（链接格式不受支持）');
        const link = node('a', '', title + ' ↗');
        link.href = raw;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        return link;
      }
      function sourceList(sources) {
        const ul = node('ul', 'source-list');
        for (const value of sources) {
          const source = record(value);
          const li = node('li');
          li.append(sourceLink(source));
          if (present(source.note)) li.append(node('p', '', display(source.note)));
          ul.append(li);
        }
        return ul;
      }
      function renderEliteSamples() {
        const samples = record(state.D.elite_samples);
        const root = $('elite-samples');
        root.replaceChildren();
        if (!list(samples.items).length) { root.append(empty('尚未提供本次高分玩家样本。')); return; }
        const scope = [['采集日期', samples.retrieved_at]];
        for (const [key, label] of [['mythic_plus', '大秘境'], ['raid', '神话团本']]) {
          const data = record(samples[key]);
          scope.push([label, numberText(data.logs) + ' 份日志 / ' + numberText(data.characters) + ' 名角色；' + display(data.period)]);
        }
        root.append(facts(scope), node('p', 'notice', display(samples.note)));
        const table = node('table');
        table.style.minWidth = '520px';
        table.append(node('caption', '', '频率不是收益权重，也不是全服唯一BiS；同角色可有多份日志。部分套装物品可能保留不同化生前驱属性和特效，不能只看显示ID。'));
        const head = node('tr');
        for (const title of ['槽位 / 物品', '物品ID', '高分大米', '神话团本']) {
          const th = node('th', '', title); th.scope = 'col'; head.append(th);
        }
        const thead = node('thead'); thead.append(head);
        const body = node('tbody');
        for (const raw of samples.items) {
          const entry = record(raw);
          const tr = node('tr');
          const name = node('th'); name.scope = 'row';
          name.append(itemLink(entry.id), node('p', 'small', display(entry.slot)));
          tr.append(name, node('td', 'num', display(entry.id)));
          for (const key of ['mythic_plus', 'raid']) tr.append(node('td', 'num', numberText(entry[key]) + '%'));
          body.append(tr);
        }
        table.append(thead, body);
        const scroll = node('div', 'table-scroll'); scroll.tabIndex = 0;
        scroll.setAttribute('role', 'region'); scroll.setAttribute('aria-label', '高手配装使用率表，可横向滚动');
        scroll.append(table); root.append(scroll);
        root.append(node('p', 'small', '来源：Mythicstats 当前高分日志统计；本次没有新获取的逐角色完整WCL事件或独立核验的前五名名单。历史五份导出另列于证据区。'));
      }
      function renderEvidence() {
        const meta = record(state.D.meta);
        const sources = list(state.D.sources);
        const scope = meta.scope;
        replace('wcl-scope', present(scope)
          ? scope && typeof scope === 'object' && !Array.isArray(scope) ? facts(Object.entries(scope)) : facts([['scope', scope]])
          : empty('未提供历史样本的日期、样本量与范围说明。'));
        const wclSources = sources.filter(value => /wcl|warcraftlogs|历史样本|高手样本/i.test([value?.title, value?.url, value?.note].map(display).join(' ')));
        replace('wcl-sources', wclSources.length ? sourceList(wclSources) : node('p', 'small', '没有单独标记的 WCL 样本来源；其余证据见下方来源列表。'));
        renderTextList('limitations', state.D.limitations, '本次未填写额外局限。缺少记录不代表所有模型、装备或样本均已验证。');
        replace('sources', sources.length ? sourceList(sources) : empty('尚未提供证据来源。'));
      }
      function rawFor(kind) { return kind === 'current' ? record(state.D.current).raw : record(record(state.D.profiles)[state.mode]).raw; }
      async function exportRaw(button) {
        const kind = button.dataset.export;
        const raw = rawFor(kind);
        if (typeof raw !== 'string' || !raw.trim()) { feedback('未提供该配置的 SimC 原文。'); return; }
        if (button.dataset.action === 'download') {
          const blob = new Blob([raw], { type: 'text/plain;charset=utf-8' });
          const url = URL.createObjectURL(blob);
          const link = node('a');
          const date = String(record(state.D.meta).date || 'snapshot').replace(/[^a-z\d-]/gi, '-');
          link.download = 'shaseng-' + (kind === 'current' ? 'current' : state.mode) + '-' + date + '.simc';
          link.href = url;
          document.body.append(link);
          link.click();
          link.remove();
          setTimeout(() => URL.revokeObjectURL(url), 1500);
          feedback('已发起下载：' + link.download);
          return;
        }
        try {
          if (!navigator.clipboard?.writeText) throw new Error('Clipboard API unavailable');
          await navigator.clipboard.writeText(raw);
          feedback('已复制 SimC 原文。');
        } catch {
          const area = $(kind + '-raw');
          area.closest('details').open = true;
          area.focus();
          area.select();
          let copied = false;
          try { copied = document.execCommand('copy'); } catch { /* Keep the selected text available. */ }
          if (copied) button.focus();
          feedback(copied ? '已复制 SimC 原文。' : '浏览器限制自动复制，已选中原文；可按 Ctrl+C 或使用下载。');
        }
      }
      function init() {
        let data;
        const raw = $('report-data').textContent.trim();
        const isTemplate = raw === ['__REPORT', '_DATA__'].join('');
        try {
          data = JSON.parse(raw);
          if (data === null || typeof data !== 'object' || Array.isArray(data)) throw new Error('Root must be an object');
        } catch {
          $('data-state').textContent = isTemplate
            ? '模板预览：嵌入 JSON 尚未填入。以下区域保留空态，没有示例装备或模拟结果。'
            : '嵌入数据无法解析，请检查 report-data 中的 JSON。页面没有读取外部结果或填入备用数值。';
          if (!isTemplate) $('data-state').classList.add('error');
          data = {};
        }
        state.D = data;
        state.runs = list(data.runs).filter(run => run !== null && typeof run === 'object' && !Array.isArray(run));
        const current = record(data.current);
        for (const g of list(current.gear)) if (g && g.owned !== false && validItemID(g.id)) state.owned.add(String(g.id));
        for (const profile of Object.values(record(data.profiles))) for (const g of list(record(profile).gear)) if (g?.owned === true && validItemID(g.id)) state.owned.add(String(g.id));
        state.mode = ['dungeon', 'raid'].find(mode => Object.prototype.hasOwnProperty.call(record(data.profiles), mode)) || '';
        renderMetadata();
        renderTextList('conclusions', data.conclusions, '尚未提供分析结论；等待已完成模拟与复核记录。', true);
        renderGear('current-gear', current.gear, true);
        $('current-count').textContent = list(current.gear).length + ' 槽记录';
        setRaw('current', current.raw);
        renderProfile();
        setupRunFilters();
        renderRuns();
        renderEliteSamples();
        renderRoutes();
        renderEvidence();
        if (Object.keys(data).length) $('data-state').textContent = '已载入本地数据快照。空白项显示“未提供”；暂定标记、原始配置与证据范围均按本次记录展示。';
        document.querySelectorAll('[data-profile]').forEach(button => button.addEventListener('click', () => {
          state.mode = button.dataset.profile;
          renderProfile();
        }));
        $('run-mode').addEventListener('change', () => { updateStageOptions(); renderRuns(); });
        $('run-stage').addEventListener('change', renderRuns);
        document.querySelectorAll('[data-export]').forEach(button => button.addEventListener('click', () => { void exportRaw(button); }));
        $('print-report').addEventListener('click', () => window.print());
        refreshTooltips();
      }
      init();
    })();
    window.whTooltips = { colorLinks: false, iconizeLinks: false, renameLinks: false };
  
