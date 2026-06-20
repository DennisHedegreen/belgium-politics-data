# Belgium 2025 Merger Bridge Candidate

Internal discovery note.

This is not a production runtime bridge and must not be used for factor joins or
runtime exposure yet.

## What Exists

Candidate file:

- `belgium_2025_merger_bridge_candidate.csv`

Verified Statbel-note file:

- `belgium_2025_merger_bridge_verified_statbel_note.csv`

The verified Statbel-note file maps:

- `30` pre-2025 municipality rows
- into `14` post-merger target rows
- for a net reduction of `16`

That matches the known national movement from `581` municipalities after the
2019 mergers to `565` municipalities from early 2025.

## Source Basis

Old/source municipality codes:

- official Statbel REFNIS capture in
  `../data/politics/belgium/geography/raw/statbel-refnis/TU_COM_REFNIS.zip`
- active municipality-level records from the captured REFNIS file

Merger grouping and target NIS codes:

- Statbel `Geografische indeling` pasted-text capture, stored under
  `../data/politics/belgium/geography/raw/statbel-refnis-2025/`
- captured section: `NIS-codes van de nieuwe gemeenten door fusies van
  02/12/2024 en 01/01/2025`

Target NIS-code status:

- verified against the Statbel text capture
- used only for a bridge-safe forward aggregation output so far
- still not a full production runtime bridge until facility/rand handling and
  factor coverage checks are decided

## Why It Is Still Blocked

The captured Statbel REFNIS file is a 2019-era open-data file with validity
windows, and it correctly reconciles the 2024 election geography. It does not
contain 2025 merger rows.

The first analytical direction is now chosen:

- keep the original 2024 election output unchanged
- aggregate the 2024 bridge-safe election rows forward to verified 2025
  municipality targets
- do not try to split 2025 factor values backward into pre-merger 2024
  municipalities

Generated output:

- `../chamber/chamber_party_share_by_2025_municipality_bridge_safe.csv`

This output has:

- `559` bridge-safe 2025 geography rows
- `6,356` municipality-party rows
- `14` merged target municipalities
- E5 special buckets still excluded
- six facility/rand vote-sum mismatch rows still excluded

Before this bridge can be used for factors:

1. document how the six facility/rand municipality vote-sum mismatch rows are
   handled in runtime geography
2. add factor coverage checks after the first coded factor source is harvested
3. keep the app/profile boundary closed until those checks exist

## Current Method Boundary

Use these files only as:

- a verified 2025 target-code bridge source
- a planning artifact for factor harvest sequencing
- a basis for future validation tests
- a bridge-safe forward aggregation candidate for matching coded 2025 factor
  sources

Do not use it as:

- a final factor join key without coverage checks
- an app/runtime geography layer
- a public-method claim
