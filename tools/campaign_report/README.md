# Campaign report

Generate an **English**, interactive, offline HTML report from the text saves of
one World Ablaze campaign. Python 3.11+ and its standard library are sufficient.
The HTML includes its own charts, styles and data; no server, CDN, package install,
API key or LLM call is required. Large reports embed gzip-compressed data and need
a browser providing `DecompressionStream` (a clear error is shown otherwise).
Original in-game template and equipment names are preserved. Every string the generator
produces (catalog, caveats, CLI, errors) is English; there is no translation layer.

Non-technical users: `USER_GUIDE.md` next to this file is the step-by-step manual.

## Generate

From the repository root:

```powershell
python -m tools.campaign_report list
python -m tools.campaign_report build --campaign a100b67c
```

The default input directory is the current user's
`Documents/Paradox Interactive/Hearts of Iron IV/save games`.
`--campaign` accepts a unique ID prefix. When there is only one campaign, it may
be omitted. To specify other inputs:

```powershell
python -m tools.campaign_report list --saves "D:/campaigns" --recursive
python -m tools.campaign_report build --saves "D:/campaigns" --campaign <id> --workers 4
python -m tools.campaign_report build --campaign <id> --from 1939.1.1 --to 1945.12.31
```

Default outputs:

| Path | Purpose | Git |
| --- | --- | --- |
| `tools/campaign_report/output/campaign.html` | Standalone report; open directly in a browser | Ignored |
| `tools/campaign_report/output/campaign.json` | Uncompressed, reusable observations and provenance | Ignored |
| `tools/campaign_report/output/campaign_digest.md` | Agent-readable Markdown digest of the same observations (see below) | Ignored |
| `.cache/campaign_report/` | Content-addressed extraction cache | Ignored |
| `tools/campaign_report/` source files | Generator, interface and tests | Versioned |

`--output` and `--cache` override these locations. Custom locations outside the
ignored directories are **not automatically ignored**. `--refresh` forces fresh
extraction. Two worker processes are used by default; `--workers 1` uses serial
execution, up to eight workers are allowed.

To change the interface without reading the saves again:

```powershell
python -m tools.campaign_report render tools/campaign_report/output/campaign.json --output tools/campaign_report/output/campaign.html
```

## Using the report

The seven default countries are GER, ENG, USA, SOV, JAP, ITA and FRA. The country
selector also exposes the other tags serialized in the selected campaign, including
tags with no active forces. Filters apply to all six tabs. The full period is
selected initially; cards and compositions use the last observation in that window.

| Tab | Views |
| --- | --- |
| Overview | Country snapshot, changes within the window, force trends, resource shortfalls |
| Forces | Army, navy and air totals; composition by family/type; division templates |
| Industry & resources | Installed civilian/military factories and dockyards; three refinery families with hydro variants and active/inactive detail; production, trade, balances and unmet demand |
| Armor | Signed stockpiles, deployed equipment, recorded reinforcement requests and assigned factories; variants and raw production-line fields |
| Wars & casualties | Counters for wars present at each observation, opponent detail, disappearing relations |
| Country status | Displayed stability and war support (rebuilt, DERIVED) and their stored bases; army/navy/air XP; command power |

`Data` opens the exact chart observations with evidence and source paths. `CSV`
exports the displayed selection before rebasing, with units and provenance. Percent
ratios are converted to percentages; other quantities retain their extracted units.
JSON exports preserve the raw ratios. Missing values remain blank in CSV and `null`
in JSON. Rebase-to-100 is unavailable for a series whose first observed value is zero.

## Campaign and branch selection

The selector groups by `game_unique_id`, not filenames, player country or random
seed. Identical copies at the same date are deduplicated by content. Different
states at the same date are refused. Session-order reversals also require explicit
selection. These checks detect some ambiguities; they cannot prove that every
unobserved interval belongs to one continuous branch.

For a selected branch, write a manifest with paths relative to that manifest:

```json
{
  "files": [
    "1939.6_Jun.hoi4",
    "1940.6_Jun.hoi4",
    "1941.6_Jun.hoi4"
  ]
}
```

```powershell
python -m tools.campaign_report build --manifest "D:/campaigns/branch.json"
```

A manifest cannot mix campaign identities or conflicting observations at the same
date. `--allow-ambiguous-timeline` accepts session reversals explicitly, recording
that choice in the report; it does not resolve conflicting same-date saves. Binary
saves are reported as unsupported. ZIP archives containing a text `gamestate` are
supported through the existing save reader.

## Agent digest

`build` also writes `campaign_digest.md`: the high-level view an analysis agent reads inline
instead of the HTML (about 430 lines for 132 saves and the seven majors). It carries the
evidence table of every metric, yearly-sampled trends per country, war relations with their
first/last save, composition, armor pressure and resource deficits at the last save, the ranges
without a deployed-division record, coverage notes, and the save filenames behind each row.
`wa-savegame-analysis` opens with it and descends to `savegame.py` from there.

```powershell
python -m tools.campaign_report digest tools/campaign_report/output/campaign.json
python -m tools.campaign_report digest tools/campaign_report/output/campaign.json --tags GER,ROM,HUN --every 6 --output "D:/axis_digest.md"
python -m tools.campaign_report build --campaign <id> --digest-tags USA,JAP --digest-every 3
```

At most 12 countries per digest; `--every` is the sampling step in months (1 to 24). A missing
value prints as `—`, never as zero; the digest adds no metric the JSON does not carry.

## Measurement contracts and limitations

| Measure | Evidence / scope |
| --- | --- |
| Mobilised share | **DERIVED** `countries/TAG/manpower/ratio` / 1e7: the recruitable fraction of the population under the conscription law and its modifiers. Scale cross-checked on one state: Ruhr 1943.6 `(total - locked) / total` = 14.8 % = GER `ratio` 1481500 / 1e7. Not a pool: it moves with laws and modifiers, never with casualties. |
| Population and available manpower | **DERIVED** sums of the state `manpower_pool` fields (`total`, `available`) over the states a country controls. `available` is the engine's free pool per state; attributing an occupied state's pool to its controller is **ASSUMED**. The country-level `manpower.ratio` is not a pool and is no longer shown as one. |
| Conscription law | **MEASURED** `countries/TAG/politics/ideas` intersected with the `mobilization_laws` idea category of the checkout (`common/ideas`, part of the cache key); shown as the law id in a change table, never as a number. Economy laws such as `over_mobilisation` are not conscription laws and are ignored. |
| Divisions and army manpower | **MEASURED** direct division records and per-country manpower contributions. **DERIVED** totals and dominant template families. Counts describe the commanded units; do not sum several countries without accounting for expeditionary forces and foreign manpower contributions. |
| Equipment stocks | **MEASURED** amounts strictly inside `production/equipments`; equipment in divisions is separate. Signed amounts are preserved. Equipment-registry presence does not itself mean ownership of a stockpile. |
| Recorded reinforcement requests | **MEASURED** `units/division/requests/reinforcement/request/need`, grouped by compatible family. These records can include material in transit; they are not certified unfulfilled shortages. |
| Armor shortfall | **DERIVED** per family: max(0, recorded reinforcement requests − signed stock). Requests may include equipment already in transit, so it is pressure, not a certified shortage; shown with stock and requests on one panel per country. |
| Daily production, training need | **ASSUMED** semantics are not sufficiently established for a verified calculation. Values stay `null` and no chart claims them. Raw `produced`, `speed`, `cost`, and factory fields remain inspectable under **Inspect recorded production lines**. No stock delta is relabelled as production. |
| Per-variant need | Not inferred from a family-level request. Variant rows retain `null` for unsupported requirements. |
| Factories and refineries | **DERIVED** sum of installed building levels over states controlled/owned by a country. This is not usable factory capacity after occupation, damage, trade and allocation. Steel and aluminium include their hydro variants. |
| Casualties | **MEASURED** bilateral war counters; **DERIVED** attribution to the corresponding country's casualties follows `losses.py`. Combat versus attrition is not established. A vanished relation terminates the observation; its last counter is not a certified final total at peace. |
| Stability and war support | **DERIVED** displayed values. The save stores only the base (`countries/TAG/stability`, `war_support`), which `add_stability` / `add_war_support` and weekly modifiers move; national spirits never touch it (**MEASURED**: a country carrying a +0.5 `stability_factor` spirit keeps its stored 0.11). The report adds, per country: the `stability_factor` / `war_support_factor` of the ideas it holds (laws, spirits, ministers defined as ideas), of the traits of its ruling leader (first `country_leader` entry of the ruling party, leader traits only) and of its appointed advisors (`characters/appointed_advisors`; trait names from the save's `character_manager`, values from `common/country_leader`), and of its enabled dynamic modifiers (stored value list, in definition order). War support then adds −0.2 when the country wages an offensive war and +0.2 when it fights a defensive one (both at once when it has both; sides from `war_relation/first_was_instigator`), the `pride_of_the_fleet_country` static modifier while the pride of the fleet is intact (the temporary sunk penalty for 30 days after `pride_of_the_fleet_date_lost`), and the stored `being_bombed_support_penalty` and `heroes_dying_war_support_penalty`. Stability adds the ruling party popularity × 0.15 × (1 + `party_popularity_stability_factor`), coastal protection ratio × 0.1, the `war_support_during_war` static modifier (−0.3) × (1 − war support) while at war, and `defensive_war_stability_factor` while in a defensive war. NCountry constants are vanilla 1.19.2 unless `05_defines.lua` overrides them (it sets the tension impact to 0). **MEASURED** against the in-game war-support tooltip of ENG, August 1941 of campaign 3a1e3a7f (every listed line reproduced: 24.78 % rebuilt, 24 % shown) and the SOV readings of the same month (stability 100 %, war support 91 %: 91.6 rebuilt). **ASSUMED**: the party popularity and coastal formulas, the defensive-war stability bonus (fits SOV, not read in a tooltip), `offensive_war_stability_factor` having no effect, the leader in office being the first `country_leader` entry, and the absence of espionage propaganda; a term that cannot be read leaves the displayed value unknown. Per-term breakdown in `countries/TAG/politics`; the stored bases stay available as `stability_base` / `war_support_base` (**MEASURED**). |
| Economy fatigue | **MEASURED** `countries/TAG/variables/economic_fatigue`, the WA variable as stored; the `economy_fatigue_N` ideas are levels derived from it in-game. |
| Convoys | **DERIVED** owned pool = sum of `countries/TAG/convoys/equipment/amount` over convoy variants; **MEASURED** free = WA telemetry `wa_tlm_nav_convoys` (its reading as free convoys is **ASSUMED**; unknown when it exceeds the pool, i.e. frozen after a capitulation); **DERIVED** in use = owned − free; **MEASURED** `convoys_destroyed` cumulative kills. Produced convoys are not reported: the `country_reports/equipment_production` counter is not consistent across saves (armor stayed at 73 while tanks were built). |
| Convoy losses | **MEASURED** top-level `sunk_convoys_history` records (month, attacker, victim, convoys). Each save keeps a rolling window of its last 24 complete months; the report stitches the selected saves month by month, the latest covering save wins, and an uncovered month stays unknown, never zero. Attacker shares are shares of the victim's losses over the covered months. **DERIVED** cumulative losses per country (`convoys.py`, build time): running sum of the stitched ledger up to each save's last complete month, unknown from the first month no save covers. |
| Factories requested, assigned, damaged | **MEASURED** per production line: `requested_factories` (what the line asks for), `active_factories` (what the engine assigned) and `damaged_factories` (assigned factories currently damaged). A line omits a field at its default 0. State buildings carry no per-factory damage, so the line-level field is the only save-side reading of damage. |
| Factories assigned to armor | **DERIVED** sum of `production/military_lines/active_factories` per family. A serialised line without the field is a queued line with no factory yet (the engine omits the field at its default 0) and counts as 0, never as unknown. |
| Composition | **DERIVED** from the definitions in the current checkout. The historical mod revision used for each save is not certified. Exact definition/template identifiers remain available. |

No missing metric is replaced by zero. Empty, present collections can sum to zero;
missing required sections remain unknown. An incomplete manpower aggregate remains
unknown instead of silently omitting divisions. Curves break at missing values and
at gaps exceeding 1.8 times the median observation interval. No interpolation or
causal AI diagnosis is generated.

The report uses multiple saves for time series. It does not currently reconstruct
missing months from WA_TLM histories. A single save produces a snapshot, with no
invented historical curve.

## Maintenance

| File | Responsibility |
| --- | --- |
| `campaign.py` | Discovery, metadata, date ordering and branch checks |
| `extract.py` | Two bounded streaming passes, classification and metric contracts |
| `cache.py` | SHA-256 keys, atomic JSON writes and importable process worker |
| `render.py` | Presentation metadata (title, localised equipment names for bare registry keys), safe HTML embedding and compression |
| `web/index.html`, `web/style.css`, `web/app.js` | Layout, chart rendering, filters, inspection and exports |
| `convoys.py` | Build-time cumulative convoy losses from the stitched per-save ledgers |
| `digest.py` | Agent-facing Markdown digest: sampling, war lifetimes, last-save sections, caps |
| `__main__.py` | `list`, `build`, `render`, `digest` commands |

Cache keys include save bytes, schema version, extraction sources, the legacy
reader modules and relevant unit/building definitions. A UI, digest or build-time
derivation change does not invalidate numeric extraction (`render.py`, `digest.py`,
`convoys.py`, `__main__.py`, `campaign.py` and `cache.py` are excluded from the key); a merge
touching `common/units`, `common/buildings` or `common/ideas` does. Save bytes are still hashed on cache hits.
The generator refuses a source save or definition set that changes during a build.
Existing scripts under `.claude/skills/wa-savegame-analysis/scripts/` are reused
without modification (`savegame.py` open/meta/date/resources/buildings/fleets, `plans.py`
templates and sub-units, `airload.py` wings, `losses.py` casualty attribution); `extract.py`
keeps its own block lexer, equipment registry, division and convoy-ledger readers. No gameplay
scripts or telemetry writers are changed.

## Validation

```powershell
python -m unittest tools.campaign_report.test_extract tools.campaign_report.test_pipeline tools.campaign_report.test_digest tools.campaign_report.test_convoys -v
node --check tools/campaign_report/web/app.js
```

Optional local campaign parity (requires the three named local saves):

```powershell
$env:WA_REPORT_REAL_SAVES = '1'
python -m unittest tools.campaign_report.test_extract.CampaignParityTests -v
Remove-Item Env:WA_REPORT_REAL_SAVES
```

Tests cover signed stocks, deployment/stock separation, missing sections, foreign
manpower contributions, duplicate fields, quoted braces, campaign mixing, branch
ambiguity, binary/ZIP formats, cache invalidation/recovery, multiprocessing on Windows,
English metadata, HTML escaping and compressed-data round trips. The parity test
compares three observations with existing readers; the stock comparison deliberately
bounds the older reader to `production`, because an unrestricted country scan includes
deployed equipment.

Browser checks should exercise all tabs, country search/selection (including the per-row
`only` button), date fields and sliders, quick ranges, raw/indexed trends, chart data dialogs,
column sorting on the tables (ascending, descending, original order), legend clicks on
multi-series charts (click hides or shows a series, Shift+click keeps only that one, `show all`
resets), the convoy-war `last month / cumulative` toggle, CSV/JSON downloads, the
`Import JSON data` button (loads another `campaign.json` from this generator for the session,
nothing leaves the browser),
variant filters and offline opening. See the delivery note in the proposal document
for the measured run and its remaining limits.
