# Belgium Next Implementation Plan

Current state:

- candidate scaffold opened
- official IBZ XML/API source path identified
- `2024_Chamber.xml` confirmed to contain municipality-level party result rows
- IBZ API `election-level` endpoint confirmed to return municipality-level Chamber rows for `2024-06-09`
- first API normalization returned `592` municipality-level rows
- API municipality-level rows include unique `nisCode` values
- API municipality-level rows include party/list vote totals and valid/blank vote totals
- municipality-level turnout is not usable from the first API path because `nrOfEligibleVoters` returns `0`
- `fetch_belgium.py` now fetches official IBZ API JSON, stores raw snapshots under `../data/politics/belgium/elections/raw/2024-chamber/ibz-api/`, and writes normalized outputs
- full candidate output exists at `chamber/chamber_party_share_by_municipality.csv`
- bridge-safe candidate output exists at `chamber/chamber_party_share_by_municipality_bridge_safe.csv`
- official country-total national output exists at `chamber/chamber_national_vote_share.csv`
- municipality audit output exists at `chamber/chamber_municipality_audit.csv`
- IBZ geography audit output exists at `geography/ibz_municipality_geography_audit.csv`
- provenance manifest exists at `../provenance/belgium_chamber_2024_normalization_manifest.json`
- targeted Belgium fetch/output tests exist and pass
- current IBZ-only geography audit finds `581` probable municipality rows and `11` E5 special buckets
- official Statbel/REFNIS direct terminal download was blocked by captcha, but manual browser capture succeeded on `2026-06-17`
- `fetch_belgium.py` now loads the captured Statbel REFNIS ZIP and writes `geography/refnis_2024_municipality_reconciliation.csv`
- REFNIS reconciliation confirms `581/581` IBZ probable 2024 municipality rows match active Statbel REFNIS municipality codes on `2024-06-09`
- the `11` IBZ E5 special buckets do not match REFNIS municipality codes and remain excluded
- be.STAT API source audit exists at `source-schema/statbel-bestat-source-audit.md`
- be.STAT `result/JSON` and `result/CSV` exports work for discovered views
- newer Census 2021 `Population density` standard export is not municipality-level
- legacy be.STAT municipality population/density/age65 exports return `590` label-only rows with no NIS/REFNIS code and should not be promoted as factor inputs
- official Statbel `Code REFNIS` open-data page exists and exposes `TXT (ZIP)` / `XLSX` download links; direct terminal download of the actual files returns captcha HTML, but browser capture is now stored in the shared source room
- REFNIS capture/reconciliation plan and completion notes exist at `geography/refnis-reconciliation-plan.md`
- non-promotable 2025 merger bridge candidate exists at `geography/belgium_2025_merger_bridge_candidate.csv`
- Statbel `Geografische indeling` pasted-text capture from `2026-06-17` verifies the `14` target NIS codes for the 2024/2025 municipality mergers
- verified non-runtime 2025 merger bridge exists at `geography/belgium_2025_merger_bridge_verified_statbel_note.csv`
- verified 2025 bridge maps `30` pre-2025 rows to `14` target rows for a net reduction of `16`
- first bridge direction is now chosen: aggregate 2024 bridge-safe election rows forward to verified 2025 municipality targets
- bridge-safe 2025-geography election output exists at `chamber/chamber_party_share_by_2025_municipality_bridge_safe.csv`
- the 2025-geography bridge-safe output has `559` geography rows and `6,356` municipality-party rows; E5 special buckets and the six facility/rand vote-sum mismatch rows remain excluded
- the six facility/rand municipality rows now have a dedicated audit at `geography/facility_language_layer_audit.csv`; they match REFNIS but contain overlapping `Dutch` and `DutchFrench` list blocks, so they remain excluded from the first runtime geography
- `5/6` facility/rand rows have the largest language group equal to row valid votes, but `Linkebeek` does not; this blocks a simple rule like "use the largest languageGroup block"
- official be.STAT legacy municipality factor views for `population`, `population_density`, and `age65_pct` were captured and audited under `factors/statbel_legacy_municipality_factor_source_audit.csv`
- those be.STAT views are blocked as factor inputs because they are label-only, have `590` rows, match only `572` active 2024 REFNIS labels, and include pre-2019 municipality names
- Eurostat demography datasets `demo_r_pjanaggr3` and `demo_r_pjanind3` were probed as an official coded fallback, but the tested responses are national/NUTS-family data and not suitable for the Belgium municipality factor layer
- newer official be.STAT Census 2021 standard views for `population`,
  `population_density`, and `age65` were captured and audited under
  `factors/statbel_census_2021_standard_view_source_audit.csv`
- those Census 2021 standard views are blocked as factor inputs because each
  returns only `30` aggregate facts with `Belgium`, `Region`, `Province`, and
  `Administrative District` geography columns and no municipality/NIS/REFNIS
  code
- the official Statbel page `Structure de la population` exposes a stronger
  population candidate download labelled `Population par commune au 1 janvier
  (1992-2026)`; direct terminal download returned TSPD/captcha HTML instead
  of a valid XLSX file, but manual browser capture succeeded
- the captured workbook contains `Code INS`, `Lieu de Résidence`, `Hommes`,
  `Femmes`, and `Total`
- `fetch_belgium.py` now normalizes sheet `Population en 2025` into
  `factors/population.csv`
- `factors/population.csv` has `565` 2025 municipality rows and uses
  `comparability_status=country_local`
- `factors/population_2025_coverage_audit.csv` confirms that all `559`
  bridge-safe 2025 election geographies match a population row; the six extra
  population rows are the facility/rand municipalities held outside the first
  runtime election geography
- `provenance/belgium_population_manifest.json` records the workbook source,
  coverage checks, and normalization boundary
- extra manually downloaded Statbel population-structure workbooks are archived
  under
  `../data/politics/belgium/factors/raw/statbel-structure-population-extra-downloads/`
- `Pop_density_fr.xlsx` is the strongest next factor candidate because the 2025
  sheet is coded by `Refnis` and includes population, area, and inhabitants per
  km²
- `fetch_belgium.py` now normalizes `Pop_density_fr.xlsx` sheet `2025` into
  `factors/population_density.csv`
- `factors/population_density.csv` has `565` 2025 municipality rows and uses
  `comparability_status=country_local`
- `factors/population_density_2025_coverage_audit.csv` confirms that all `559`
  bridge-safe 2025 election geographies match a population-density row
- `provenance/belgium_population_density_manifest.json` records the workbook
  source, coverage checks, and the decision not to promote provisional `2026 P`
- `pop-typeHH_FRv2.xlsx` and `popstranger-1992-fr.xlsx` are useful future
  country-local candidates, but not first-app requirements
- `pop-geboorteland_FR.xlsx` appears national-level only in first inspection
- `TF_SOC_POP_STRUCT_2026.zip` is archived under
  `../data/politics/belgium/factors/raw/statbel-social-population-structure-2026/`
  and is the promoted `age65` source because it is
  municipality-coded by `CD_REFNIS` and includes age, sex, nationality, civil
  status, and population count
- quick aggregate check of `TF_SOC_POP_STRUCT_2026.txt` gives `565`
  municipality codes, total population `11867634`, and age 65+ share `20.6692`
- `fetch_belgium.py` now normalizes `TF_SOC_POP_STRUCT_2026.zip` into
  `factors/age65_pct.csv`
- `factors/age65_pct.csv` has `565` 2026 municipality rows and uses
  `comparability_status=family_mapped`
- `factors/age65_2025_coverage_audit.csv` confirms that all `559` bridge-safe
  2025 election geographies match an age-65+ row
- `provenance/belgium_age65_manifest.json` records the source, aggregation
  method, coverage checks, and the 2026 factor versus 2025 election geography
  boundary
- manually downloaded Statbel marriage workbooks are archived under
  `../data/politics/belgium/factors/raw/statbel-marriages-downloads/`, but they
  are contextual source material, not first-layer factor candidates
- Belgium is registered as `internal_ready=True`, `public_ready=False` in
  `country_registry.py`
- `belgium_only` exposes the Belgium adapter as an internal single-country
  profile, and `world_internal` includes Belgium after Netherlands
- a minimal Belgium adapter exists at `adapters/belgium/adapter.py`
- the adapter reads the bridge-safe 2025 election layer, official national
  result file, and three Statbel factors: population, density, and age65
- Belgium factor/election joins in the adapter use `public_geography_id` /
  REFNIS code rather than municipality labels
- Belgium UI has been polished toward the Netherlands adapter pattern:
  `All parties`, result/copy boxes, ranking charts, `Compare municipalities`,
  a party-ranking `By Municipality` page, and a national-result snapshot page
- local `WPD_PROFILE=belgium_only` Streamlit smoke passed on `2026-06-21`;
  screenshot written to `/tmp/belgium-ui-smoke-wait.png`
- public-preview boundary/checklist exists at
  `belgium-public-vs-internal-boundary.md`
- public-preview README, methodology, deploy, and export-spec wording draft
  exists at `belgium-public-preview-wording.md`
- `export_public_country_repo.py` now has a Belgium public-preview spec for a
  future `belgium-politics-data` mirror
- local preview mirror export exists at `../belgium-politics-data`
- generated mirror test `python3 -m unittest tests/test_public_surface.py`
  passes from the mirror root
- local generated mirror Streamlit smoke passed on `2026-06-21` at
  `http://127.0.0.1:8502/`; Playwright screenshot written to
  `/tmp/belgium-mirror-ui-smoke-playwright.png`
- public GitHub preview mirror exists at
  `https://github.com/DennisHedegreen/belgium-politics-data`
- GitHub readback confirms the mirror is `PUBLIC`, default branch is `main`,
  and the local mirror tracks `origin/main`
- public Streamlit preview exists at
  `https://belgium-politics-data-hetgwp6yhueo4ffajjw7sd.streamlit.app/`
- live Streamlit readback passed in Playwright on `2026-06-21`; screenshot
  written to `/tmp/belgium-streamlit-live-readback.png`

Next useful passes:

1. create a preview-labelled TID door only after confirming the public wording
   still fits the TID surface
2. decide later whether one household/nationality factor belongs in the
   preview or should stay future/internal

First no-go conditions:

- municipality-level IBZ rows cannot be reconciled to a stable Statbel geography
- the `592` row count mixes true municipalities and special buckets; if Statbel reconciliation cannot defend the `575` bridge-safe layer, do not build the app picker on it
- be.STAT label-only municipality exports are joined without official REFNIS/NIS code reconciliation
- party/list availability cannot be explained clearly
- source values fail valid-vote reconciliation

Reference:

- `belgium-election-scope.md`
- `belgium-factor-board.md`
- `belgium-public-vs-internal-boundary.md`
- `belgium-public-preview-wording.md`
- `geography/refnis-reconciliation-plan.md`
- `geography/belgium-2025-merger-bridge-note.md`
- `source-schema/statbel-bestat-source-audit.md`
- `source-schema/ibz-2024-chamber-api-schema.md`
