"""Build an offline-readable equipment report from the adjacent report-data.json."""

import argparse
import html
import json
import math
import re
from pathlib import Path
from urllib.parse import urlencode, urlsplit

ROOT = Path(__file__).resolve().parent
MODELS = (("slice", "切片模型"), ("st", "单体模型"), ("aoe", "多目标模型"))


def text(value, missing="未提供"):
    return html.escape(str(value) if value is not None and value != "" else missing, quote=True)


def number(value, suffix="", signed=False, missing="未提供"):
    if value is None or value == "" or isinstance(value, float) and not math.isfinite(value):
        return missing
    if isinstance(value, (int, float)):
        return f"{value:+,.2f}{suffix}" if signed else f"{value:,.2f}".rstrip("0").rstrip(".") + suffix
    rendered = text(value)
    return rendered if not suffix or rendered.endswith(suffix) else rendered + suffix


def link(label, url, wowhead="", download=False):
    url = str(url or "")
    if not url or urlsplit(url).scheme.lower() not in ("", "https", "http") or url.startswith("//"):
        return label
    attrs = f' data-wowhead="{text(wowhead)}"' if wowhead else ""
    attrs += ' download' if download else ' target="_blank" rel="noopener noreferrer"'
    return f'<a href="{text(url)}"{attrs}>{label}</a>'


def table(headers, rows, caption):
    body = "".join(rows) or f'<tr><td colspan="{len(headers)}" class="muted">暂无资料</td></tr>'
    head = "".join(f'<th scope="col">{text(label)}</th>' for label in headers)
    return (f'<div class="table-scroll" role="region" aria-label="{text(caption)}" tabindex="0">'
            f'<table><caption>{text(caption)}</caption><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')


def row(*cells):
    return "<tr>" + "".join(f"<td>{cell}</td>" for cell in cells) + "</tr>"


def section(ident, title, body, intro=""):
    return (f'<section id="{ident}" aria-labelledby="{ident}-title"><div class="section-head">'
            f'<h2 id="{ident}-title">{title}</h2><p>{intro}</p></div>{body}</section>')


def equipment_row(item):
    bonus = item.get("bonus") or ""
    bonus = ":".join(map(str, bonus)) if isinstance(bonus, list) else re.sub(r"[/,\s]+", ":", str(bonus))
    ident, level = item.get("id", ""), item.get("level", "")
    query = urlencode({"ilvl": level, "bonus": bonus})
    tip = f"item={ident}&domain=cn&ilvl={level}&bonus={bonus}"
    icon = str(item.get("icon_data") or "")
    image = f'<img src="{text(icon)}" width="44" height="44" alt="">' if icon.startswith("data:image/") else '<span class="icon-placeholder" aria-hidden="true">装</span>'
    name = f'<span class="item-name">{image}<span>{text(item.get("name"))}</span></span>'
    main = link(name, f"https://www.wowhead.com/cn/item={ident}?{query}", tip)
    main = main.replace("<a ", '<a class="item-link" ', 1)
    gems = " · ".join(link(text(g.get("name")), f'https://www.wowhead.com/cn/item={g.get("id", "")}',
                           f'item={g.get("id", "")}&domain=cn') for g in item.get("gems", [])) or "未记录宝石"
    return (f'<tr class="gear-row"><th scope="row">{text(item.get("slot"))}</th><td>{main}</td>'
            f'<td class="level">{number(item.get("level"))}</td><td class="gems">{gems}</td>'
            f'<td><span class="source">{text(item.get("source"))}</span><p class="item-note">{text(item.get("note"), "无补充说明")}</p></td></tr>')


def tuning_section(data):
    tuning = data.get("tuning")
    if not tuning:
        return ""
    stats = table(["属性", "当前已装备", "肩腿腰334后", "说明"],
                  [row(text(s["name"]), text(s["before"]), text(s["after"]), text(s["note"]))
                   for s in tuning["stats"]], "假设完成三件护甲升级 · 无消耗品战前属性")
    recommendations = table(["调整部位", "保留方案", "是否建议投入", "依据"],
                            [row(text(r["part"]), text(r["owned"]), text(r["decision"]), text(r["reason"]))
                             for r in tuning["recommendations"]], "满级之后的宝石、附魔与再造")
    comparisons = table(["饰品分支", "调整方案", "切片变化", "五目标变化", "单体变化"],
                        [row(text(c["branch"]), text(c["label"]),
                             *(number((c["values"].get(m) or {}).get("delta"), "%", signed=True, missing="未测")
                               for m in ("slice", "aoe", "st"))) for c in tuning["comparisons"]],
                        "调优复测 · 每个分支相对自身升级后基准")
    notes = "".join(f'<li>{text(n)}</li>' for n in tuning["limits"])
    output = section("tuning", "肩、腿、腰满级后的调优", f'<p class="lead">{text(tuning["summary"])}</p>'
                     + stats + recommendations + comparisons + f'<ul>{notes}</ul>', text(tuning["assumption"]))
    talents = tuning.get("talents")
    if talents:
        rows = [row(text(c["branch"]), text(c["label"]),
                    *(number((c["values"].get(m) or {}).get("delta"), "%", signed=True, missing="未测")
                      for m in ("slice", "aoe", "st"))) for c in talents["candidate_results"]]
        results = table(["饰品分支", "天赋方案", "切片变化", "五目标变化", "单体变化"], rows,
                        "10000次天赋复测 · 固定升级后装备，相对你当前天赋")
        joint = table(["饰品分支", "切片额外变化", "五目标额外变化", "单体额外变化"],
                      [row(text(c["branch"]), *(number((c["values"].get(m) or {}).get("tuning_delta_same_talents"),
                               "%", signed=True, missing="未测") for m in ("slice", "aoe", "st")))
                       for c in talents["joint_tuning"]], "新天赋下，再做披风／手套／宝石微调的边际收益")
        exports = ""
        for key, label in (("user_short_cd", "只换灵魂专注，保留能量爆裂"),
                           ("user_short_cd_martial", "灵魂专注＋尚武敏捷，保留你的其他功能点")):
            exports += f'<details><summary>{label} · 查看导入码</summary><pre style="overflow:auto;max-width:100%;padding:16px;background:var(--soft)"><code>{text(talents["exports"][key]["talents"])}</code></pre></details>'
        notes = "".join(f'<li>{text(n)}</li>' for n in talents["limits"])
        output += section("talents", "先试天赋，再决定是否再造", f'<p class="lead">{text(talents["summary"])}</p>'
                          + results + joint + exports + f'<ul>{notes}</ul>',
                          "灵魂专注：乾元充能恢复90→70秒、单次15秒；角杯盖子：90秒恢复、单次20秒。尚武敏捷增加近战攻击速度，能量爆裂在消耗高亮幻灭时补真气。")
    return output


def render(data):
    meta = data.get("meta", {})
    stats = "".join(f'<article class="stat-card"><h3>{text(s.get("name"))}</h3><strong>{number(s.get("percent"), "%")}</strong>'
                    f'<p class="muted">属性等级 {number(s.get("rating"))}</p><p>{text(s.get("comparison"))}</p>'
                    f'<p class="stat-advice">{text(s.get("advice"))}</p></article>' for s in data.get("stats", []))
    equipment = table(["部位", "装备", "装等", "宝石", "来源与化生说明"],
                      [equipment_row(i) for i in data.get("equipment", [])], "当前装备清单")
    branches = "".join(f'<article class="branch"><p class="eyebrow">{text(b.get("outcome"))}</p>'
                       f'<h3>{text(b.get("preferred"))}</h3><p>{text(b.get("reason"))}</p>'
                       f'<p class="branch-comparison">{text(b.get("comparison"))}</p></article>' for b in data.get("branches", []))
    panels, buttons = [], []
    model_info = {m["id"]: m for m in data.get("models", [])}
    for key, fallback in MODELS:
        model = model_info.get(key, {})
        label = text(model.get("label"), fallback)
        buttons.append(f'<button type="button" data-model="{key}" aria-controls="model-{key}" aria-pressed="false">{label}</button>')
        results = []
        for comparison in data.get("comparisons", []):
            value = (comparison.get("values", {}).get(key) or {})
            measured = value.get("dps") not in (None, "")
            delta = value.get("delta") if measured else None
            tone = "positive" if isinstance(delta, (int, float)) and delta > 0 else "negative" if isinstance(delta, (int, float)) and delta < 0 else ""
            results.append(row(text(comparison.get("label")), number(value.get("dps"), missing="未测"),
                               number(value.get("ci") if measured else None, missing="未测"),
                               f'<span class="{tone}">{number(delta, "%", signed=True, missing="未测")}</span>'))
        panels.append(f'<section id="model-{key}" class="model-panel" aria-labelledby="label-{key}">'
                      f'<h3 id="label-{key}">{label}</h3><p class="muted">{text(model.get("detail"), "模型说明尚未提供")}</p>'
                      + table(["配置方案", "每秒伤害", "置信区间／误差", "相对变化"], results, f"{label} · 配置对照") + '</section>')
    actions = "".join(f'<li><h3>{text(a.get("title"))}</h3><p>{text(a.get("body"))}</p></li>' for a in data.get("actions", []))
    elite = table(["角色", "评分", "装等", "暴击", "急速", "精通", "全能"],
                  [row(link(text(e.get("name")), e.get("url")), number(e.get("score")), number(e.get("level")),
                       *(number(e.get(stat), "%") for stat in ("crit", "haste", "mastery", "vers"))) for e in data.get("elite", [])], "高分样本参考")
    usage = table(["样本项目", "使用情况", "口径说明"],
                  [row(text(u.get("name")), text(u.get("value")), text(u.get("note"))) for u in data.get("usage", [])], "样本使用情况")
    consumables = table(["项目", "当前记录", "建议"], [row(link(text(c.get("name")), c.get("url")), text(c.get("current")),
                        text(c.get("recommendation"))) for c in data.get("consumables", [])], "消耗品与补齐建议")
    limits = "".join(f'<li>{text(limit)}</li>' for limit in data.get("limits", []))
    sources = "".join(f'<li>{link(text(s.get("title")), s.get("url"))}</li>' for s in data.get("sources", []))
    downloads = "".join(f'<li>{link(text(d.get("title")), d.get("path"), download=True)}</li>' for d in data.get("downloads", []))
    nav = (("overview", "结论"), ("stats", "属性"),
           *((("tuning", "满级调优"),) if data.get("tuning") else ()),
           *((("talents", "天赋对照"),) if data.get("tuning", {}).get("talents") else ()),
           ("equipment", "装备"), ("branches", "R币与兑换"),
           ("comparisons", "模型对照"), ("actions", "行动顺序"), ("samples", "样本"), ("consumables", "消耗品"), ("evidence", "来源"))
    navigation = "".join(f'<a href="#{ident}">{label}</a>' for ident, label in nav)
    facts = "".join(f'<div><dt>{label}</dt><dd>{text(meta.get(key))}</dd></div>' for key, label in
                    (("date", "研究日期"), ("patch", "游戏版本"), ("content", "研究场景"), ("engine", "模拟引擎")))
    payload = json.dumps(data, ensure_ascii=False, allow_nan=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e")
    body = section("stats", "属性现状", f'<div class="stat-grid">{stats or "暂无属性资料"}</div>', "结合当前记录与样本口径阅读建议，不把样本均值当作硬性阈值。")
    body += tuning_section(data)
    body += section("equipment", "当前装备", equipment, "整行可打开物品，宝石可独立查看。当前属性、来源及化生前驱以本表记录为准；悬浮提示中的数据库默认属性不能替代当前属性。")
    body += section("branches", "R币与兑换分支", f'<div class="branch-grid">{branches or "暂无分支资料"}</div>', text(meta.get("budget_note")))
    body += section("comparisons", "模型与配置对照", '<div class="model-switch" role="group" aria-label="选择战斗模型" hidden>' + "".join(buttons) + '</div>' + "".join(panels), "仅在同一模型与相同测试口径内比较；缺失结果标记为“未测”，不按零收益处理。")
    body += section("actions", "行动顺序", f'<ol class="action-list">{actions or "<li>暂无行动建议</li>"}</ol>')
    body += section("samples", "高分样本与使用情况", elite + usage, "参考样本用于理解配置取向，具体环境与适用边界见口径说明。")
    body += section("consumables", "消耗品与补齐", consumables)
    body += section("evidence", "研究边界与资料来源", f'<div class="evidence-grid"><article><h3>适用边界</h3><ul>{limits or "<li>暂无边界说明</li>"}</ul></article>'
                    f'<article><h3>参考来源</h3><ul>{sources or "<li>暂无来源记录</li>"}</ul><h3>本地资料下载</h3><ul>{downloads or "<li>暂无下载资料</li>"}</ul></article></div>')
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light"><title>{text(meta.get("character"))} · 装备研究报告</title>
<style>
:root{{--paper:#f5f3ed;--card:#fffefa;--ink:#202e36;--muted:#5d6d74;--line:#d9ded9;--accent:#176b61;--soft:#eaf2ed;--warm:#a34330}}
*{{box-sizing:border-box}}html{{scroll-behavior:smooth;scroll-padding-top:6rem}}body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.75 "Segoe UI","Microsoft YaHei",sans-serif}}
a{{color:var(--accent);text-underline-offset:4px;overflow-wrap:anywhere}}a:hover{{text-decoration-thickness:2px}}button{{font:inherit;cursor:pointer}}[hidden]{{display:none!important}}
:focus-visible{{outline:3px solid var(--warm);outline-offset:4px}}.skip{{position:fixed;top:-100px;left:1rem;z-index:10;background:var(--card);padding:.5rem 1rem}}.skip:focus{{top:1rem}}
.wrap{{width:min(1280px,calc(100% - 64px));margin:auto;min-width:0}}.masthead{{background:#203a3d;color:#f9f8ef;padding:58px 0 44px}}
.eyebrow{{font-size:.8rem;font-weight:700;letter-spacing:.12em;margin:0 0 .6rem}}.masthead .eyebrow{{color:#bad6c6}}h1,h2,h3,p{{margin-top:0}}h1{{font-size:clamp(1.9rem,4vw,3.2rem);line-height:1.3;letter-spacing:-.03em;margin-bottom:1.5rem}}
h2{{font-size:1.55rem;line-height:1.4;margin-bottom:.5rem}}h3{{font-size:1.05rem;line-height:1.5;margin-bottom:.65rem}}p{{margin-bottom:.7rem;overflow-wrap:anywhere}}.lead{{font-size:1.12rem;white-space:pre-line;margin:0;max-width:100ch}}
.conclusion{{border-left:3px solid #a9cf9b;padding:0 0 0 24px}}.conclusion h2{{font-size:.9rem;color:#bad6c6}}.facts{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px;margin:28px 0 18px}}
.facts dt{{color:#c5d4d0;font-size:.8rem}}.facts dd{{margin:4px 0 0;overflow-wrap:anywhere;font-size:.93rem}}.budget{{border-top:1px solid #56706c;padding-top:16px;margin:0;color:#dfebdf;font-size:.9rem;white-space:pre-line}}
nav{{position:sticky;top:0;z-index:5;background:rgba(255,254,250,.97);border-bottom:1px solid var(--line)}}.nav-links{{display:flex;gap:26px;overflow-x:auto;padding:15px 2px;white-space:nowrap}}nav a{{text-decoration:none;font-size:.9rem;font-weight:600;flex-shrink:0}}
main{{padding-bottom:48px}}main>section{{padding-top:44px;min-width:0}}.section-head{{margin-bottom:20px;max-width:100ch}}.section-head p,.muted{{color:var(--muted);font-size:.9rem}}.section-head p:empty{{display:none}}
.stat-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,230px),1fr));gap:16px}}.stat-card,.branch,.evidence-grid>article{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:24px;min-width:0}}
.stat-card h3{{color:var(--muted);font-weight:500}}.stat-card strong{{font-size:2rem;line-height:1.3;font-variant-numeric:tabular-nums}}.stat-card .muted{{margin:6px 0 18px}}.stat-advice{{border-top:1px solid var(--line);padding-top:12px;color:var(--accent)}}
.table-scroll{{max-width:100%;overflow:auto;background:var(--card);border:1px solid var(--line);border-radius:12px;margin-bottom:18px}}table{{width:100%;border-collapse:collapse;min-width:720px;text-align:left;font-size:.93rem}}
caption{{text-align:left;padding:14px 20px;font-size:.82rem;font-weight:600;color:var(--muted);border-bottom:1px solid var(--line)}}th,td{{padding:15px 20px;border-bottom:1px solid var(--line);vertical-align:top;overflow-wrap:anywhere}}thead th{{background:#edf0ea;color:var(--muted);font-size:.8rem;font-weight:600;white-space:nowrap}}tbody tr:last-child>*{{border-bottom:0}}tbody tr:hover{{background:#f0f5ee}}
.gear-row{{position:relative}}.gear-row>th{{width:90px;font-size:.85rem;white-space:nowrap;font-weight:500}}.gear-row>td:nth-child(2){{min-width:235px}}.gear-row>td:last-child{{min-width:290px}}.item-link{{text-decoration:none;font-weight:600}}
.item-link::after{{content:"";position:absolute;inset:0;z-index:1}}.item-link:focus-visible{{outline:none}}.item-link:focus-visible::after{{outline:3px solid var(--warm);outline-offset:-3px;border-radius:4px}}.item-name{{display:flex;align-items:center;gap:12px;line-height:1.5}}
.item-name img,.icon-placeholder{{flex-shrink:0;width:44px;height:44px;border-radius:8px;background:var(--soft);object-fit:cover}}.icon-placeholder{{display:grid;place-items:center;font-size:.8rem;color:var(--muted)}}.gems{{min-width:160px;font-size:.82rem}}.gems a{{position:relative;z-index:2}}
.level{{font-weight:700;font-variant-numeric:tabular-nums}}.source{{font-size:.86rem}}.item-note{{color:var(--muted);font-size:.82rem;line-height:1.65;margin:.4rem 0 0;white-space:pre-line}}
.branch-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:16px}}.branch .eyebrow{{color:var(--accent);letter-spacing:0}}.branch h3{{font-size:1.2rem}}.branch-comparison{{font-size:.88rem;background:var(--soft);padding:12px;border-radius:6px;margin:16px 0 0;white-space:pre-line}}
.model-switch{{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:20px}}.model-switch button{{border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--ink);padding:9px 18px}}.model-switch button[aria-pressed=true]{{background:var(--accent);border-color:var(--accent);color:white}}
.model-panel{{margin-top:20px}}.model-panel table{{min-width:640px;font-variant-numeric:tabular-nums}}.model-panel td:first-child{{width:48%}}.positive{{color:#12644d;font-weight:700}}.negative{{color:#a34330;font-weight:700}}
.action-list{{list-style:none;counter-reset:actions;padding:0;margin:0;display:grid;gap:12px}}.action-list li{{counter-increment:actions;position:relative;padding:20px 24px 20px 68px;background:var(--card);border:1px solid var(--line);border-radius:10px}}.action-list li::before{{content:counter(actions,decimal-leading-zero);position:absolute;left:24px;top:20px;color:var(--accent);font-weight:700}}.action-list p{{margin:0;white-space:pre-line}}
.evidence-grid{{display:grid;grid-template-columns:1fr 1fr;gap:20px}}ul{{padding-left:1.3rem;margin:0 0 18px}}li{{margin-bottom:.65rem;overflow-wrap:anywhere}}footer{{border-top:1px solid var(--line);padding:24px 0 32px;color:var(--muted);font-size:.82rem}}
@media(max-width:700px){{.wrap{{width:calc(100% - 32px)}}.masthead{{padding:32px 0}}.facts{{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}}.conclusion{{padding-left:16px}}.lead{{font-size:1rem}}.nav-links{{gap:22px}}main>section{{padding-top:32px}}.evidence-grid{{grid-template-columns:1fr}}.stat-card,.branch,.evidence-grid>article{{padding:20px}}th,td{{padding:13px 16px}}}}
@media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}@media print{{nav,.skip,.model-switch{{display:none!important}}.masthead{{background:white;color:black;padding:20px 0}}.masthead .eyebrow,.facts dt,.budget,.conclusion h2{{color:#333}}.wrap{{width:100%}}.model-panel[hidden]{{display:block!important}}.table-scroll{{overflow:visible}}table{{min-width:0}}.item-link::after{{display:none}}}}
</style></head><body><a class="skip" href="#main">跳到报告正文</a>
<header id="overview" class="masthead"><div class="wrap"><p class="eyebrow">角色装备研究 · 决策备忘</p><h1>{text(meta.get("character"))} · 装备研究</h1>
<div class="conclusion"><h2>本次结论</h2><p class="lead">{text(data.get("lead"), "结论尚未提供")}</p></div>
<dl class="facts">{facts}</dl><p class="budget">资源与预算 · {text(meta.get("budget_note"))}</p></div></header>
<nav aria-label="报告章节"><div class="wrap"><div class="nav-links">{navigation}</div></div></nav>
<main id="main" class="wrap">{body}</main><footer><div class="wrap">本报告可离线阅读；联网后物品链接可提供悬浮提示。原始研究数据已内嵌，下载资料按本地相对路径打开。</div></footer>
<script id="report-data" type="application/json">{payload}</script>
<script>
const switcher = document.querySelector('.model-switch');
const buttons = [...switcher.querySelectorAll('button')];
function selectModel(id) {{
  buttons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.model === id)));
  document.querySelectorAll('.model-panel').forEach(panel => {{ panel.hidden = panel.id !== 'model-' + id; }});
}}
switcher.hidden = false;
buttons.forEach(button => button.addEventListener('click', () => selectModel(button.dataset.model)));
selectModel('slice');
window.whTooltips = {{colorLinks:false, iconizeLinks:false, renameLinks:false}};
</script><script async src="https://wow.zamimg.com/js/tooltips.js"></script></body></html>'''


def main():
    parser = argparse.ArgumentParser(description="根据研究数据生成独立装备报告；默认读取脚本同目录的数据。")
    parser.add_argument("--data", type=Path, default=ROOT / "report-data.json", help="研究数据 JSON 路径")
    parser.add_argument("--output", type=Path, default=ROOT / "report.html", help="生成的 HTML 路径")
    args = parser.parse_args()
    if not args.data.is_file():
        parser.exit(1, f"数据文件尚未就绪：{args.data}；生成器准备就绪，写入后重新运行即可。\n")
    try:
        data = json.loads(args.data.read_text(encoding="utf-8-sig"))
        document = render(data)
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        parser.exit(1, f"数据格式错误，未写入报告：{error}\n")
    args.output.write_text(document, encoding="utf-8")
    print(f"已生成报告：{args.output}")


if __name__ == "__main__":
    main()
