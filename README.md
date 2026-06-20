# Belgian Politics Data

Belgian Politics Data compares Belgian Chamber election vote shares with municipality-level structural factors. It is built for finding reporting leads and visible patterns, not for proving why people vote as they do.

This repo is a public preview, not a full public launch.

## Public Preview

- GitHub repo: [DennisHedegreen/belgium-politics-data](https://github.com/DennisHedegreen/belgium-politics-data)
- Visibility: `public`
- Live app: [belgium-politics-data Streamlit app](https://belgium-politics-data-hetgwp6yhueo4ffajjw7sd.streamlit.app/)
- Public status: `preview`; TID door is preview-only, not a full country launch

## Declared Scope

- Country: Belgium
- Election type: Chamber
- Unit of analysis: municipality
- Municipality election year: `2024`
- National result year: `2024`
- Preview geography: `bridge-safe 2025 Statbel municipality target`
- Preview runtime geographies: `559`
- Factors: Population, Population density, Age 65+

This repo is the Belgium-only public preview extracted from the internal World-politics-data engine. It keeps the Belgian app shell, Belgium data pack, source notes, and scope docs without pretending that the country surface has already become a full public launch.

## What You Can Do

- Compare party vote share with one or more municipality-level factors.
- Read whether the relationship is positive, negative, weak, moderate, or strong.
- Inspect high and low municipalities before turning a pattern into a claim.
- Use the result as a lead for reporting, not as the final story.

## What Not To Infer

- Correlation is not causation.
- Municipality-level patterns do not describe individual voters.
- A strong result does not prove why people voted as they did.
- A weak or missing result does not prove that a factor is irrelevant.
- The app is not a prediction model, campaign tool, or causal engine.

## How To Read Results

Positive correlation means higher party vote share tends to appear in municipalities where the selected factor is higher. Negative correlation means higher party vote share tends to appear where the selected factor is lower. The result is ranked by absolute correlation strength, so `-0.62` is treated as stronger than `0.31`.

Example: if a party has `r = 0.58` with population density, a responsible reading is: "The party tended to have higher vote shares in denser municipalities in this election year." It is not: "Density made voters choose this party."

## Quick Case

A journalist could start with a strong party-factor result, open the high and low municipality tables, and ask a concrete reporting question: is this a real geographic pattern, a party-history pattern, or just a one-year artifact? The app gives the lead. The reporting still has to do the verification.

See [METHODOLOGY.md](METHODOLOGY.md) before using results in public claims.

## Boundary

- Not a full public/TID launch
- Not a cross-country Belgium claim
- Not a second source of truth beside `World-politics-data`
- Not a full Belgian election archive
- Not a live turnout-factor release

Intentionally missing:

- Full public-launch wording until Belgium is explicitly declared beyond preview
- Public homepage, public country-switch, or cross-country exposure
- `Turnout` as a live factor because the first municipality API path has no usable voter denominator
- E5 special buckets and six facility/rand rows from the first runtime layer
- Older or non-Chamber Belgian elections

## Preview Sources

- Election source: `IBZ 2024 Chamber bridge-safe municipality layer + Statbel municipality indicators`
- Secondary source: `Internal only: E5 special buckets and six facility/rand vote-sum mismatch rows remain held out.`
- Statistics source: `Statbel`
- Provenance notes: [provenance/](provenance/)

## Repo Structure

```text
app.py               Single-country public-preview wrapper
engine_app.py        Shared app shell extracted from the internal engine
correlation_utils.py Compatibility import for correlation helpers
core/                Runtime, presentation, correlation, and failure-state helpers
country_registry.py  Belgium-only public-preview registry
belgium/             Country data pack and scope notes
provenance/          Preview-safe manifests
tests/               Country-surface and logic contract tests
```

## Source Of Truth

This repo is a public preview surface. The shared internal source tree still exists separately and remains the source of truth for shell changes and future extraction work. Public claims should cite this repo cautiously and should not treat the preview as a final TID release.

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```
