# Deploy

Belgium public preview deploy checklist.

## Local smoke

```bash
pip install -r requirements.txt
streamlit run app.py
```

Check:

- `Explore`
- `Compare municipalities`
- `By Municipality`
- `National result`
- `About & sources`

## Live Streamlit Preview

- Live app: [belgium-politics-data Streamlit app](https://belgium-politics-data-hetgwp6yhueo4ffajjw7sd.streamlit.app/)

## Streamlit Community Cloud settings

Current Streamlit Community Cloud settings:

- Repository: `DennisHedegreen/belgium-politics-data`
- Branch: `main`
- Main file path: `app.py`
- Python version: `3.12`
- Secrets: none
- Suggested app URL: `belgian-politics-data` if available; otherwise leave blank and use the generated URL

Deploy privacy:

- The GitHub repo is public.
- The Streamlit app may be public for this preview.
- Keep TID/site links out until a separate public-launch decision exists.

## Public preview shape

- App title: `Belgian Politics Data`
- Country exposure: `Belgium` only
- No public country selector
- No TID door or public homepage updates in this phase
- Public preview only until an explicit TID-readiness decision exists

## Before pushing live

- confirm the belgium data pack exists and loads cleanly
- confirm the README and methodology still say `public preview`
- confirm boundary notes still match the Belgium preview boundary
- confirm no TID-door language slipped into the repo
