# Belgium Election Scope

Current candidate election scope:

- election type: `Chamber of Representatives`
- first target year: `2024`
- election date: `2024-06-09`
- public geography target: municipality-level IBZ `nisCode`
- primary election source layer: IBZ election-results API/XML
- first output target: party vote share by municipality-level row
- turnout target: out of scope for the first pass, because the first API probe returned `nrOfEligibleVoters = 0` for municipality-level rows
- first app target: bridge-safe municipality-party layer, not the full raw municipality-level candidate

Why this scope:

- the federal Chamber election is the cleanest first Belgian national layer
- the 2024 result is current and available through official machine-readable sources
- the API gives structured municipality-level rows with `nisCode`
- one year avoids opening historical municipal reform and boundary drift too early

Known source anchors:

- IBZ election results landing page:
  - `https://electionresults.belgium.be/`
- IBZ JSON API / Swagger:
  - `https://api.electionresults.belgium.be/swagger/index.html`
- IBZ XML overview:
  - `https://resultatselection.belgium.be/fr/XmlOverview`
- 2024 Chamber XML:
  - `https://resultatselection.belgium.be/xml/2024_Chamber.xml`

Not in scope yet:

- municipal council elections
- regional parliament elections
- European Parliament elections
- historical Chamber years
- public cross-country comparison
- candidate-level analysis
- turnout as a live factor
- language-group or party-family aggregation unless a separate method note defines it
- broad Belgian politics portal behavior
- every available Statbel/be.STAT factor
- public website expansion before the narrow Chamber tool can be explained in a
  short TID/tool description

First acceptance test:

- official 2024 Chamber source can be normalized into municipality-level party vote shares
- each municipality-level row has a stable geography id
- party/list vote totals reconcile with each row's valid-vote total
- the `592` municipality-level rows are explained before they are treated as normal Belgian municipalities
- non-standard rows, special voting buckets, or abroad-style rows are either excluded with a clear note or kept in a separate diagnostic layer

Current acceptance status:

- normalized full municipality-party candidate exists
- official country-total national vote-share output exists
- municipality audit exists
- first bridge-safe output excludes `11` E5 special buckets and `6` non-reconciling facility/rand municipality rows
- IBZ-only geography audit marks `581` probable municipality rows and `11` E5 special buckets
- Statbel geography reconciliation confirms `581/581` probable 2024 municipality rows
- verified 2025 merger bridge exists
- 2025 bridge-safe geography output exists
- first be.STAT factor-source audit blocks legacy label-only municipality views
- app exposure is still blocked until coded/current factors and coverage checks exist
