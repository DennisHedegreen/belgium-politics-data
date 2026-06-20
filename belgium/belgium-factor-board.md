# Belgium Factor Board

Internal planning note for first Belgian factor passes.

This is not a public launch list and not a cross-country comparability claim.

Website-fit rule:

- prefer a small defended factor set over a broad impressive catalog
- do not add factors simply because be.STAT has a view
- the first public-compatible Belgium surface should be explainable as a narrow
  2024 Chamber municipality pattern reader
- if a factor needs long caveats to avoid misleading users, it stays internal or
  source-only

## First Candidate Batch

### `population`

Why:

- core denominator and coverage sanity check
- likely available from Statbel open data at municipality level
- needed before per-capita or density-derived metrics are trusted

First requirement:

- match Statbel municipality geography to IBZ `nisCode`
- document source date and whether the reference point is January 1

### `population_density`

Why:

- first structural settlement signal
- likely useful in Belgium because regional/urban patterns are central
- easier to explain than a blunt urban/rural class

First requirement:

- confirm whether Statbel publishes municipality area / density directly or whether it must be derived
- keep unit and denominator explicit

### `age65`

Why:

- clean demographic structure signal
- already part of the wider factor family in the engine
- usually easier to defend than labour-market or migration semantics

First requirement:

- source age-by-municipality rows from Statbel
- sum a documented 65+ age band and divide by total population

### `income`

Why:

- useful structural complement if municipality coverage is good
- likely available through Statbel taxable-income or administrative-income data

First requirement:

- identify whether the available measure is household income, taxable income, or another administrative definition
- avoid pretending it matches Denmark, Sweden, Norway, or Netherlands income definitions

## Investigate Later

### `education`

Useful but likely more sensitive to census/source-period semantics. Do not include until coverage and definition are clear.

### `housing`

Potentially strong, but Belgium may require careful source separation between building stock, ownership, and household structure.

### `cars`

Potentially useful as a settlement/mobility proxy. Check whether registration location creates distortion.

## Blocked For Now

### `turnout`

The first municipality-level API probe returned `nrOfEligibleVoters = 0`, so turnout should not be promoted from that API path.

### `immigration_share`

Politically and semantically sensitive. Leave out of the first Belgian candidate.

### `crime`

Not needed for a first source-first Belgium proof and likely requires a separate public wording pass.

## Working Order

1. reconcile IBZ `nisCode` with Statbel municipality geography
2. confirm whether the `575` bridge-safe election geography can be defended as the first app layer
3. keep the 2025 forward bridge limited to the bridge-safe layer
4. find a coded/current source for `population`
5. add `population_density` only if source coverage is equally defensible
6. add `age65` only if the age-band denominator is explicit
7. only then decide whether `income` is safe enough for the first picker

Runtime geography note:

- the first factor coverage target is the `559` bridge-safe 2025-geography
  election layer
- the six facility/rand rows are documented in
  `geography/facility_language_layer_audit.csv` and remain out of runtime until
  a Belgium-specific language-layer method is sourced

Blocked source note:

- official be.STAT legacy municipality views for `population`,
  `population_density`, and `age65_pct` were captured on `2026-06-18`
- they are blocked as factor inputs because they are label-only, include `590`
  rows, match only `572` active 2024 REFNIS labels, and include pre-2019
  municipality names
