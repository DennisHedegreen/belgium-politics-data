# Belgium Factor Source Audit

Internal candidate note.

This records the first post-REFNIS factor-source pass for Belgium.

## Source Tested

Official be.STAT municipality views were captured under:

- `../data/politics/belgium/factors/raw/statbel-bestat-legacy-municipality-views/`

Generated audit:

- `statbel_legacy_municipality_factor_source_audit.csv`

Candidate factors tested:

- `population`
- `population_density`
- `age65_pct`

## Finding

The captured be.STAT municipality exports are not safe factor inputs.

Each tested export:

- has `590` rows
- has municipality labels, but no NIS/REFNIS code
- includes one blank municipality label for a total/national row
- matches only `572` labels against the active 2024 REFNIS municipality label
  set
- includes old pre-2019 municipality names, showing the source geography is not
  aligned with either the 2024 election geography or the 2025 bridge-safe target
  geography

Concrete unmatched examples:

- `Knesselare`
- `Kruishoutem`
- `Lovendegem`
- `Meeuwen-Gruitrode`
- `Neerpelt`
- `Nevele`
- `Opglabbeek`
- `Overpelt`
- `Puurs`
- `Sint-Amands`
- `Waarschoot`
- `Zingem`
- `Zomergem`

## Decision

Do not write Belgium factor files from these be.STAT views.

They are useful as source-discovery evidence, but not as app/factor inputs.

Belgium still needs one of these before factor promotion:

1. a coded Statbel/be.STAT source with NIS/REFNIS municipality codes and current
   geography
2. an official downloadable factor file with REFNIS/NIS codes
3. a separate documented official code bridge for any label-only source, plus
   coverage checks against the `559` bridge-safe 2025-geography election layer

## Eurostat Probe

Eurostat was tested as an alternative official source path on `2026-06-18`.

Captured source evidence:

- `../data/politics/belgium/factors/raw/eurostat-demography-probe/`

Tested datasets:

- `demo_r_pjanaggr3`
- `demo_r_pjanind3`

Finding:

- the tested responses are official and coded, but only at national/NUTS-family
  geography for this probe
- `geo=BE` returns Belgium total, not municipalities
- the relevant datasets are labelled NUTS 3, not LAU/REFNIS municipality
  geography

Decision:

- do not use Eurostat NUTS data for the first Belgium municipality factor layer
- this would make the tool broader and less precise instead of fitting the
  website-fit boundary

## Current Safe Belgium Data Surface

Belgium currently has:

- official IBZ 2024 Chamber election rows
- 2024 REFNIS reconciliation
- verified 2025 municipality merger bridge
- bridge-safe 2025-geography election layer
- official coded Statbel 2025 municipality population factor

Belgium does not yet have:

- additional promoted factor files beyond population
- runtime app adapter
- profile exposure

## Statbel Census 2021 Standard Views Probe

Captured on `2026-06-20`.

Official be.STAT datasource:

- datasource id: `e957ac31-44a2-4718-8469-10470d3c41d9`
- datasource name: `IM_SOC_GEO_IND_CENSUS_2021`
- description: `Indicators on population, households and housing, according to the place of residence, based on the CENSUSES 2011 and 2021`

Captured raw files:

- `../data/politics/belgium/factors/raw/statbel-bestat-census-2021-standard-views/total-population.json`
- `../data/politics/belgium/factors/raw/statbel-bestat-census-2021-standard-views/population-density.json`
- `../data/politics/belgium/factors/raw/statbel-bestat-census-2021-standard-views/population-65-plus.json`

Generated audit:

- `statbel_census_2021_standard_view_source_audit.csv`

Finding:

- the datasource is official and relevant
- the tested standard views return `30` facts each
- the exposed geography columns are `Belgium`, `Region`, `Province`, and
  `Administrative District`
- no municipality, NIS, or REFNIS code is exposed in these standard results

Decision:

- do not promote the standard Census 2021 be.STAT views as Belgium municipality
  factor inputs
- keep searching for either a documented custom be.STAT query path or another
  official coded municipality file

## Statbel Population By Municipality Download Probe

Identified on `2026-06-20`.

Official Statbel page:

- `https://statbel.fgov.be/fr/themes/population/structure-de-la-population`

Official download label:

- `Population par commune au 1 janvier (1992-2026)`

Direct URL attempted:

- `https://statbel.fgov.be/sites/default/files/files/documents/bevolking/5.1%20Structuur%20van%20de%20bevolking/Population_par_commune.xlsx`

Generated audit:

- `statbel_population_by_municipality_download_audit.csv`

Initial finding:

- this is the strongest `population` source candidate found so far because the
  official Statbel page describes it as population by municipality
- direct terminal download returned a TSPD/captcha HTML challenge, not a valid
  XLSX workbook

Manual capture result:

- user downloaded the workbook through a browser to `Downloads`
- the workbook was copied to
  `../data/politics/belgium/factors/raw/statbel-population-by-municipality/Population_par_commune.xlsx`
- sha256:
  `ba1bba1577929f0e1eced196331adebe9e6f2febd9b0713e439685d165e20b09`
- workbook is a valid XLSX
- sheet `Population en 2025` contains `Code INS`, `Lieu de Résidence`,
  `Hommes`, `Femmes`, and `Total`
- all `565` selected Statbel 2025 municipality codes are present
- all `559` bridge-safe 2025 election geographies match a population row

Decision:

- promote `population` as the first internal Belgium factor candidate
- write normalized output to `factors/population.csv`
- write coverage audit to `factors/population_2025_coverage_audit.csv`
- keep the terminal-blocked HTML response as source-capture evidence, but it no
  longer blocks the factor because the real workbook has been manually captured

## Statbel Extra Population-Structure Downloads

Captured on `2026-06-20` from user Downloads.

Raw source room:

- `../data/politics/belgium/factors/raw/statbel-structure-population-extra-downloads/`

Archived files:

- `Pop_density_fr.xlsx`
- `pop-typeHH_FRv2.xlsx`
- `pop-geboorteland_FR.xlsx`
- `popstranger-1992-fr.xlsx`

Finding:

- `Pop_density_fr.xlsx` is now promoted as a `population_density` factor. It is a valid
  XLSX workbook, has annual sheets from `2019` through `2026 P`, and the `2025`
  sheet is coded by `Refnis` with `Population`, `Superficie en km²`, and
  `Habitants / km²`.
- normalized output has `565` selected Statbel 2025 municipality-code rows
- coverage audit confirms all `559` bridge-safe 2025 election geographies match
  a population-density row
- the six extra rows are the same facility/rand municipalities held outside the
  first runtime election layer
- the provisional `2026 P` sheet is not promoted because Statbel notes that
  2026 surface-area values were not yet published and the sheet reuses 2025
  area values
- `pop-typeHH_FRv2.xlsx` is coded by `CODE NIS` and may support a future
  household-structure factor, including one-person households.
- `popstranger-1992-fr.xlsx` is coded by `CODE INS` and may support a future
  nationality/foreign-population factor, but needs careful extraction because
  rows are split by sex and total.
- `pop-geboorteland_FR.xlsx` appears national-level only in first inspection,
  so it is not a municipality factor candidate for the first Belgium layer.

Decision:

- archive these files for future use
- promote `Pop_density_fr.xlsx` sheet `2025` as `factors/population_density.csv`
- write coverage audit to `factors/population_density_2025_coverage_audit.csv`
- keep the household and nationality workbooks as future country-local
  candidates, not first-app requirements

## Statbel Social Population Structure 2026

Captured on `2026-06-20` from user Downloads.

Raw source room:

- `../data/politics/belgium/factors/raw/statbel-social-population-structure-2026/`

Archived file:

- `TF_SOC_POP_STRUCT_2026.zip`

Finding:

- the archive contains a `104151550` byte pipe-delimited text file
- the file is municipality-coded by `CD_REFNIS`
- it includes municipality names, administrative district, province, region,
  sex, nationality group, civil status, age, and population count
- quick aggregate check gives `467615` raw rows, `565` municipality codes, and
  total population `11867634`
- age 65+ can be derived as `2452949`, or `20.6692%` of the checked total
- Belgian/non-Belgian nationality can also be derived from `CD_NATLTY`
- normalized `age65` output has `565` 2026 municipality rows
- coverage audit confirms all `559` bridge-safe 2025 election geographies match
  an age-65+ row
- the factor keeps the `2026-01-01` reference period visible because it is used
  against the 2025 bridge-safe election geography as a structural context
  factor

Decision:

- promote `age65` as `factors/age65_pct.csv`
- write coverage audit to `factors/age65_2025_coverage_audit.csv`
- keep nationality/civil-status derivatives as future candidates, not
  first-layer requirements

## Statbel Marriage Downloads

Captured on `2026-06-20` from user Downloads.

Raw source room:

- `../data/politics/belgium/factors/raw/statbel-marriages-downloads/`

Decision:

- archive as contextual Belgium Statbel source material
- do not treat these as first-layer Belgium politics-data factor candidates
