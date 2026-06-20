# Statbel be.STAT Source Audit

Internal Belgium candidate note.

This records the first official Statbel/be.STAT source probe for Belgian
municipality factors. It is not a promotion note and does not make Belgium
factor-ready.

## Official Endpoints Checked

be.STAT view index:

- `https://bestat.statbel.fgov.be/bestat/api/views`

Statbel REFNIS open-data page:

- `https://statbel.fgov.be/fr/open-data/code-refnis`
- title: `Code REFNIS`
- listed downloads: `TXT (ZIP)` and `XLSX`
- direct download URLs discovered:
  - `https://statbel.fgov.be/sites/default/files/files/opendata/REFNIS%20code/TU_COM_REFNIS.zip`
  - `https://statbel.fgov.be/sites/default/files/files/opendata/REFNIS%20code/TU_COM_REFNIS.xlsx`
- manual browser capture stored under
  `../data/politics/belgium/geography/raw/statbel-refnis/`

View metadata pattern:

- `https://bestat.statbel.fgov.be/bestat/api/views/{view_id}`

Datasource metadata pattern:

- `https://bestat.statbel.fgov.be/bestat/api/datasources/{data_source_id}`

View result export pattern discovered from the be.STAT crosstable page:

- `https://bestat.statbel.fgov.be/bestat/api/views/{view_id}/result/CSV`
- `https://bestat.statbel.fgov.be/bestat/api/views/{view_id}/result/JSON`

## Candidate Views Found

### Census 2021 aggregate indicators

View:

- `f6a7d3b2-2ce6-430b-9dcd-bc7496d69d46`
- name: `Population density`
- datasource: `e957ac31-44a2-4718-8469-10470d3c41d9`
- datasource name: `IM_SOC_GEO_IND_CENSUS_2021`

Finding:

- JSON/CSV export works.
- Standard view returns only `30` facts.
- Export is aggregated to region/province/administrative-district level, not
  municipality level.
- It is useful as a source-discovery trail, but not as a municipality factor
  input.

Follow-up on `2026-06-20`:

- the same newer Census 2021 datasource was checked through three English
  standard views:
  - `583da0e9-7cbb-4063-bdcd-1070fd1522f9` / `Total population`
  - `f6a7d3b2-2ce6-430b-9dcd-bc7496d69d46` / `Population density`
  - `5169f31c-5706-4773-b89f-7cde05d3fe83` / `Population 65 years and over`
- each standard view returned `30` facts
- exposed geography columns were `Belgium`, `Region`, `Province`, and
  `Administrative District`
- no municipality, NIS, or REFNIS code was exposed in the standard result

Decision:

- keep `IM_SOC_GEO_IND_CENSUS_2021` as a relevant source trail
- do not promote its standard views as municipality factor inputs
- next search should target a documented custom be.STAT query path or a separate
  official coded municipality file

### Legacy municipality population

View:

- `09de639d-668b-41fb-b8ec-eb82b3546407`
- name: `Gemeenten met de grootste bevolking`
- datasource: `06deb4bd-8f91-49fb-befb-cfb25108b5ae`

Finding:

- JSON export works.
- Export returns `590` municipality rows.
- Rows contain municipality labels, but no NIS/REFNIS code.
- Values and datasource age make this unsuitable for direct 2024/2025
  reconciliation.

### Legacy municipality density

View:

- `ed4bcba6-132d-4959-8161-1b5e4497b376`
- name: `Gemeenten waarvan de bevolkingsdichtheid het hoogste is`
- datasource: `06deb4bd-8f91-49fb-befb-cfb25108b5ae`

Finding:

- JSON export works.
- Export returns `590` municipality rows.
- Rows contain municipality labels, but no NIS/REFNIS code.
- Not safe as a first Belgium factor source without a separate official code
  reconciliation.

### Legacy municipality age 65+

View:

- `8c000d33-f325-4743-aafa-55275ef16f96`
- name: `Gemeenten met het hoogste aandeel vijfenzestigplussers`
- datasource: `06deb4bd-8f91-49fb-befb-cfb25108b5ae`

Finding:

- JSON export works.
- Export returns `590` municipality rows.
- Rows contain municipality labels, but no NIS/REFNIS code.
- Not safe as a first Belgium `age65` source without a separate official code
  reconciliation.

## Method Decision

Do not promote be.STAT factor files yet.

Reason:

- current IBZ election rows are 2024 and use `nisCode`
- the 2024 election geography reflects the pre-2025 municipality structure
  (`581` probable municipality rows after excluding IBZ E5 special buckets)
- Belgium's municipality structure changes on `2025-01-01` reduce the national
  municipality count to `565`, so current-year factor sources need an explicit
  merger/crosswalk method before joining to 2024 election rows
- the directly usable be.STAT municipality exports found so far expose labels
  but no stable municipality code
- the newer Census 2021 density view is not municipality-level in the standard
  export
- direct Statbel `REFNIS_2025.csv` retrieval from terminal returned a bot/captcha
  page in the earlier probe
- direct terminal retrieval of Statbel sitemap, robots, and geography pages also
  returned the same TSPD/captcha challenge, so the blocker is site-wide from the
  terminal context rather than isolated to one CSV URL
- direct terminal retrieval of the official `TU_COM_REFNIS.zip` and
  `TU_COM_REFNIS.xlsx` paths also returned captcha HTML, not valid ZIP/XLSX files
- manual browser capture of the same files succeeded on `2026-06-17`
- the captured REFNIS ZIP validates the 2024 election geography: `581/581` IBZ
  probable municipality rows match active Statbel REFNIS municipality codes on
  `2024-06-09`

Safe next path:

1. keep the captured REFNIS material in the shared source room
2. use `../geography/refnis_2024_municipality_reconciliation.csv` as the 2024
   election geography code audit
3. document the `581` to `565` municipality merger bridge before using current
   factor values
4. only then join be.STAT municipality values or fetch a newer coded source

## 2026-06-18 Follow-Up

After the 2025 merger bridge was verified, four official be.STAT municipality
views were captured under:

- `../data/politics/belgium/factors/raw/statbel-bestat-legacy-municipality-views/`

Generated audit:

- `../belgium/factors/statbel_legacy_municipality_factor_source_audit.csv`

Result:

- each tested source has `590` rows
- each has labels but no NIS/REFNIS code
- each includes one blank municipality label for a total row
- each matches only `572` active 2024 REFNIS municipality labels
- unmatched labels include pre-2019 municipality names such as `Knesselare`,
  `Kruishoutem`, `Lovendegem`, `Meeuwen-Gruitrode`, `Neerpelt`, `Nevele`,
  `Opglabbeek`, `Overpelt`, `Puurs`, `Sint-Amands`, `Waarschoot`, `Zingem`, and
  `Zomergem`

Decision:

- do not promote these be.STAT views as Belgium factor files
- keep searching for a coded/current Statbel source before app/profile exposure
