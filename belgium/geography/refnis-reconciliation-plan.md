# Belgium REFNIS Reconciliation Plan

Internal Belgium candidate note.

Belgium cannot move from source candidate to runtime adapter until the remaining
promotion gates below are completed.

## Official Source

Statbel open-data page:

- `https://statbel.fgov.be/fr/open-data/code-refnis`
- title: `Code REFNIS`
- source description: INS codes for regions, provinces, administrative
  arrondissements, and municipalities, using 5-digit codes
- listed downloads:
  - `TXT (ZIP)`
  - `XLSX`

Direct download URLs discovered from the open-data page:

- `https://statbel.fgov.be/sites/default/files/files/opendata/REFNIS%20code/TU_COM_REFNIS.zip`
- `https://statbel.fgov.be/sites/default/files/files/opendata/REFNIS%20code/TU_COM_REFNIS.xlsx`

Terminal result:

- the page itself is readable through browser-style fetch
- direct terminal `curl` download of the ZIP/XLSX paths returns TSPD/captcha HTML,
  not a valid ZIP/XLSX file

Manual capture result:

- real `TU_COM_REFNIS.zip` and `TU_COM_REFNIS.xlsx` were captured through a
  browser on `2026-06-17`
- the ZIP contains `TU_COM_REFNIS.txt`
- `TU_COM_REFNIS.txt` contains validity-windowed REFNIS rows
- municipality-level active rows on `2024-06-09`: `581`
- IBZ probable 2024 municipality rows matching active REFNIS codes: `581`
- IBZ probable 2024 municipality rows missing from active REFNIS: `0`

## Expected Source-Room Placement

The real files are stored under the shared source room, not inside the Belgium
app room:

- `../data/politics/belgium/geography/raw/statbel-refnis/TU_COM_REFNIS.xlsx`
- or `../data/politics/belgium/geography/raw/statbel-refnis/TU_COM_REFNIS.zip`

Capture note:

- `../data/politics/belgium/geography/raw/statbel-refnis/capture-note.md`

Required capture-note fields already recorded:

- source page URL
- download URL used
- capture date
- browser/manual/API route used
- original filename
- SHA-256
- whether the file is the Statbel `Code REFNIS` open-data file

## Reconciliation Checks

Checks completed:

1. confirmed the file is a real ZIP/XLSX, not HTML
2. identified the column names for NIS/INS code and municipality labels
3. filtered to municipality-level 5-digit records
4. counted municipality records active on the 2024 election date
5. compared IBZ 2024 probable municipality rows against REFNIS codes

Generated output:

- `refnis_2024_municipality_reconciliation.csv`

Expected IBZ-side baseline:

- `592` IBZ municipality-level rows in the Chamber 2024 API output
- `11` E5 special buckets excluded from municipality reconciliation
- `581` probable pre-2025 municipality rows
- `6` non-reconciling facility/rand municipality rows are held out from the
  bridge-safe first app layer and documented in
  `facility_language_layer_audit.csv`

Known Belgium structure issue:

- IBZ election data is 2024
- Belgium has `565` municipalities from `2025-01-01`
- any current-year factor source must therefore either be backdated to the 2024
  municipal structure or joined through a documented merger bridge
- a non-promotable merger bridge candidate now exists at
  `belgium_2025_merger_bridge_candidate.csv`
- the candidate bridge maps `30` pre-2025 rows to `14` target rows, a net
  reduction of `16`
- the Statbel `Geografische indeling` 2025 merger note was captured as pasted
  browser text on `2026-06-17` and verifies the `14` target NIS codes
- the verified non-runtime bridge is written to
  `belgium_2025_merger_bridge_verified_statbel_note.csv`
- the first factor-direction decision is to bridge 2024 election rows forward to
  verified 2025 municipality targets, not to split 2025 factors backward into
  pre-merger 2024 geography
- bridge-safe forward output is written to
  `../chamber/chamber_party_share_by_2025_municipality_bridge_safe.csv`
- that output has `559` bridge-safe 2025 geography rows and still excludes E5
  special buckets plus the six facility/rand vote-sum mismatch rows
- the six facility/rand rows match REFNIS but contain overlapping `Dutch` and
  `DutchFrench` list blocks; `5/6` have `DutchFrench` equal to valid votes, but
  `Linkebeek` does not, so no simple languageGroup rule is promoted

## Promotion Gate

Belgium may only be added to `country_registry.py` after all of these are true:

- official REFNIS source captured and hashed: done
- IBZ `nisCode` rows reconcile to official pre-2025 municipality codes: done
- E5 special buckets are documented and excluded from runtime geography: done
- the six facility/rand municipality rows are explicitly excluded from runtime
  geography and covered by `facility_language_layer_audit.csv`: done
- the 2025 municipality merger bridge is documented before using current-year
  factor data: target codes verified and bridge-safe forward aggregation exists
- at least `population`, `population_density`, and `age65` have source manifests
  and coverage checks
