# Belgium Public Vs Internal Boundary

Belgium is moving toward a possible public-preview mirror, but it is not live yet.

The correct next public shape is **public preview**, not full public launch.

## Public Now

Nothing.

- no public Belgium app
- no Belgium mirror repo
- no Belgium Streamlit Community Cloud app
- no Belgium TID door
- no public homepage link
- no shared public country-switch exposure
- no cross-country Belgium claim

## Internal Now

- internal country room: `belgium/`
- internal rebuild script: `fetch_belgium.py`
- dispatcher entry: `fetch_country.py belgium`
- internal adapter: `adapters/belgium/adapter.py`
- internal profile: `belgium_only`
- internal multi-country profile: `world_internal`
- internal registry entry with `internal_ready=True`, `public_ready=False`
- bridge-safe 2024 Chamber municipality layer aggregated to verified 2025 Statbel municipality targets
- official 2024 Chamber national result snapshot
- three internal Statbel factors:
  - `population`
  - `population_density`
  - `age65`

## Preview Candidate Shape

If promoted, Belgium should first become:

- public GitHub preview mirror: `belgium-politics-data`
- public-preview Streamlit app
- preview-labelled TID door only after live readback passes
- no shared public country selector
- no public homepage feature until a separate full-launch decision
- no cross-country claim

The preview mirror may contain normalized public-source outputs, app shell, source notes, methodology, and provenance files. It must not include raw download rooms or private working material.

## Still Not Full Launch

Even after a public-preview mirror exists, Belgium should still not be treated as full public launch until:

- public wording is reviewed after live Cloud deployment
- the TID door is explicitly labelled preview-only
- the public homepage decision is separate
- cross-country comparability is explicitly refused or separately defended
- the facility/rand holdout story is short enough to explain publicly

## Public-Preview Readiness Checklist

Belgium can get a GitHub/Streamlit public-preview mirror only after all of this is true:

- [x] internal election layer exists
- [x] internal national result snapshot exists
- [x] internal factor layer has at least three usable factors
- [x] all live factors cover all `559` bridge-safe runtime geographies
- [x] adapter joins election/factor rows by `public_geography_id` / REFNIS code, not labels
- [x] local `belgium_only` Streamlit smoke passes
- [x] UI has normal country-app views: `Explore`, `Compare municipalities`, `By Municipality`, `National result`, `About & sources`
- [x] full engine test suite passes
- [x] public-preview README wording is drafted
- [x] public-preview deploy notes are drafted
- [x] public-preview methodology/source wording is drafted
- [x] `export_public_country_repo.py` has a Belgium preview spec
- [x] exported mirror is tested locally from the generated repo root
- [ ] GitHub repo is created only after the local mirror test passes
- [ ] Streamlit Community Cloud is connected only after GitHub readback passes
- [ ] TID preview door is created only after live Streamlit readback passes

## Hard No-Go Conditions

Do not publish a Belgium mirror if any of these are true:

- the public README implies full launch instead of preview
- the public surface hides the `559` bridge-safe runtime geography limit
- the public surface implies all `565` current municipalities are in the election runtime layer
- the public surface hides the `11` E5 special bucket holdout
- the public surface hides the six facility/rand held-out rows
- the public surface presents population, density, or age65 as causal explanations
- the public surface claims cross-country comparability
- any mirror export includes raw source rooms or private working files

## Rule

Belgium may move toward GitHub and Streamlit only as a **public preview**. The local preview mirror now exists and passes local readback, but GitHub, Streamlit Community Cloud, and any TID preview door remain separate next decisions.
