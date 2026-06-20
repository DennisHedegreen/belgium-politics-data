# IBZ 2024 Chamber API Schema Note

Initial source probe and first normalization for Belgium candidate.

Endpoint shape used:

```text
https://api.electionresults.belgium.be/election-level?Types=Chamber&ElectionDates=2024-06-09T00:00:00.000Z&Descriptions=Municipality&Detailed=true&PageSize=1000
```

Initial observed row shape:

- `id`
- `electionId`
- `nrOfEligibleVoters`
- `nrOfValidVotes`
- `nrOfBlankVotes`
- `nisCode`
- `labels`
- `description`
- `electionType`
- `electionDate`
- `electionLists`

Initial observed `electionLists` item shape:

- `id`
- `nrOfVotes`
- `listNumber`
- `languageGroup`
- `electionLevelId`
- `partyId`
- `partyLabel`
- `hasCandidateData`

Initial findings:

- municipality-level rows are returned with `description = Municipality`
- first normalization returned `592` municipality-level rows
- `nisCode` was present and unique
- `nrOfValidVotes` is present at municipality level
- `nrOfBlankVotes` is present at municipality level
- `nrOfEligibleVoters` was `0` for municipality-level rows in the first probe
- party/list votes are nested under `electionLists`
- full municipality-party candidate output has `6,818` rows
- bridge-safe candidate output has `575` geography rows and `6,522` party rows
- `11` NIS codes ending in `998` are treated as E5 special buckets in the first audit
- `6` municipality rows have party/list vote sums larger than row valid votes and are held out of the bridge-safe output
- IBZ-only geography audit marks `581` rows as probable municipality rows and `11` rows as E5 special buckets
- official Statbel/REFNIS automated reconciliation is still pending

Normalization target:

```text
election_year,election_date,public_geography_id,municipality,party,party_id,list_number,language_group,votes,valid_votes,blank_votes,share,vote_sum_reconciles,special_bucket,bridge_safe,source_scope
```

Current outputs:

- `belgium/chamber/chamber_party_share_by_municipality.csv`
- `belgium/chamber/chamber_party_share_by_municipality_bridge_safe.csv`
- `belgium/chamber/chamber_national_vote_share.csv`
- `belgium/chamber/chamber_municipality_audit.csv`
- `belgium/geography/ibz_municipality_geography_audit.csv`
- `provenance/belgium_chamber_2024_normalization_manifest.json`

Open questions:

- why the 2024 Chamber municipality-level source returns `592` rows when the app candidate should probably start from the smaller bridge-safe subset
- whether all `nisCode` values map to current Statbel municipalities
- whether rows such as `Anvers (E5)` can be formally documented as special voting buckets from IBZ documentation
- how to handle the six faciliteit/rand municipality rows where `Dutch` and `DutchFrench` list layers make the party/list sum exceed row valid votes
