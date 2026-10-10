# Equipment Research HTML

Recommend HTML for substantial multi-source studies; short weekly result
updates can remain a compact text/ledger delta. Build the agreed report from
structured character, gear and measurement data rather than transcribing DPS
numbers into independent UI constants.

## Content

- Character, snapshot date, region/patch, Hero tree, attainable ceilings and
  important excluded content; distinguish target set from owned equipment.
- Separate raid/dungeon equipment views with icons, slots, item levels,
  source, retained-effect Catalyst provenance, gems and enchants. Offer clean
  SimC download/copy for each mode.
- Measured comparisons with model, baseline, deltas, iterations, seed and
  uncertainty. Show unsupported effects and untested candidates explicitly.
- Stat snapshot context, tested stat direction, replaceable craft slots,
  embellishments and practical alternatives for near-ties.
- Actual coin balance, ordered boss/loot-spec route, fallback and stop rules.
  Show owned/excluded targets. Future content stays in a dated future branch.
- Filterable per-boss/source watchlist across relevant old/new raids,
  dungeons/Vault and crafting. Separate useful drops from a complete eligible
  remaining roll pool; unknown pool size means no exact percentage.
- Dated evidence, guides and local raw artifacts; explain matched player
  sample scope. Acquisition history and a UI favorite are different concepts.

## Wowhead and Hover Interaction

Verify the current integration against the provider when implementing it.
The pilot used `https://wow.zamimg.com/js/tooltips.js` with automatic renaming,
icon injection and coloring disabled so the report controls its own layout.
For Simplified Chinese, normal item links used `/cn/item=<id>` and tooltip
attributes used `data-wowhead="item=<id>&domain=cn&ilvl=<level>&bonus=<colon-separated-ids>"`.
Keep bonus and environment information rather than displaying only a base item.

The pilot's new items required the `ptr-2` environment: its tooltip fetch path
was `/ptr-2/tooltip/item/<id>?locale=4`, and link metadata used `domain=cn.ptr-2`.
The provider may force PTR tooltips to English; preserve actual untranslated
names rather than inventing Chinese names or promising unavailable localization.
These are observed integration details, not guarantees about future APIs.

Use one primary equipment link whose hit area spans the icon, text and row
whitespace. A stretched-link pseudo-element can expand this area without
nesting anchors. Keep gem links and favorite controls above that layer and
independently operable. Provide a subtle row hover and keyboard focus state.
Give small gem targets additional padding without resizing their icon image.

Omit native `title` from equipment links/images: it creates a second browser
popup over the Wowhead tooltip. `alt`/`aria-label` serve accessibility and are
not replacements for a tooltip. Decorative images beside named links can use
`alt=""`; name icon-only links through `aria-label`. Keep contextual titles
for unrelated unfamiliar controls only when useful.

## Delivery and Verification

Prefer a self-contained HTML file with embedded data and cached item icons
for a portable report. Describe external tooltip/network dependence and keep
name, level and source visible when it fails. Link local evidence relatively
and escape external text/embedded JSON correctly. Do not make a dated report
builder a generic scraping or simulation framework without a demonstrated need.

Verify desktop/mobile layouts, image loads, mode-specific exports and absence
of overflow/errors. Test actual Wowhead appearance over the icon, name and
whitespace; confirm equipment links have no native `title`, gems show their
own tooltip, and favorite buttons are not intercepted. Test filters and
favorite persistence separately from the real acquisition ledger. Use browser
screenshots when available; disclose if visual inspection could not be done.
For file-based delivery, give the HTML path. A temporary test server may be
needed by browser automation even when the user can open the file directly.
