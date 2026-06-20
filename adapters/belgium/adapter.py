from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st

from core.correlation import compute_correlation_result, corr_strength_label
from core.presentation import (
    METRIC_SHORT_LABELS,
    PARTY_NAME_MODES,
    build_country_finding,
    format_party_name,
    render_bar_chart,
    render_compact_dataframe,
    render_country_sidebar_footer,
    render_profile_cards,
)


BELGIUM_LIVE_YEARS = (2024,)
BELGIUM_DEFAULT_PARTY_MIN_MUNICIPALITIES = 25
BELGIUM_DEFAULT_PARTY_MIN_MEAN_SHARE = 0.5
BELGIUM_FACTOR_FILES = {
    "population": "population.csv",
    "density": "population_density.csv",
    "age65": "age65_pct.csv",
}
BELGIUM_METRIC_OPTIONS = [
    ("population", "Population", "Population (2025 reference count)"),
    ("density", "Population density", "Residents per km2"),
    ("age65", "Age 65+", "Share aged 65+ (%)"),
]


def _is_public_preview_surface() -> bool:
    return os.environ.get("WPD_PUBLIC_PREVIEW", "").strip().lower() in {"1", "true", "yes"}


def _surface_label() -> str:
    return "public Belgium preview" if _is_public_preview_surface() else "internal Belgium candidate"


def _surface_sidebar_text() -> str:
    if _is_public_preview_surface():
        return "Public Belgium preview. 2024 Chamber results are aggregated forward to a bridge-safe 2025 municipality layer."
    return "Internal Belgium candidate. 2024 Chamber results are aggregated forward to a bridge-safe 2025 municipality layer."


def _surface_intro_text() -> str:
    if _is_public_preview_surface():
        return "Belgium public-preview reading. Correlations use the 2024 Chamber vote layer and the newest available Statbel municipality factor for each metric."
    return "First internal Belgium reading. Correlations use the 2024 Chamber vote layer and the newest available Statbel municipality factor for each metric."


def _about_boundary_text() -> str:
    if _is_public_preview_surface():
        return """
Belgium is currently a public preview.

- Election layer: 2024 federal Chamber municipality results from IBZ.
- Runtime geography: bridge-safe rows aggregated forward to verified 2025 Statbel municipality targets.
- Factor layer: Statbel municipality population, population density, and age-65+ indicators.
- Hold-outs: E5 special buckets and six facility/rand vote-sum mismatch rows remain outside the runtime layer.

This is not a full Belgian politics archive, not a causal model, and not a cross-country comparison claim.
"""
    return """
Belgium is currently an internal candidate only.

- Election layer: 2024 federal Chamber municipality results from IBZ.
- Runtime geography: bridge-safe rows aggregated forward to verified 2025 Statbel municipality targets.
- Factor layer: Statbel municipality population, population density, and age-65+ indicators.
- Hold-outs: E5 special buckets and six facility/rand vote-sum mismatch rows remain outside the runtime layer.

No cross-country claim should be made from this adapter yet.
"""


def _factor_file(country_config, metric_key: str) -> Path:
    return country_config.factor_dir / BELGIUM_FACTOR_FILES[metric_key]


def is_available(country_config, runtime_context) -> bool:
    return country_config.municipal_vote_path.exists() and country_config.factor_dir.exists()


@st.cache_data
def load_bundle(country_config):
    municipal = pd.read_csv(country_config.municipal_vote_path)
    municipal["election_year"] = municipal["election_year"].astype(int)
    municipal["votes"] = pd.to_numeric(municipal["votes"], errors="coerce")
    municipal["valid_votes"] = pd.to_numeric(municipal["valid_votes"], errors="coerce")
    municipal["share"] = pd.to_numeric(municipal["share"], errors="coerce")

    national = pd.read_csv(country_config.national_vote_path) if country_config.national_vote_path else pd.DataFrame()
    if not national.empty:
        national["election_year"] = national["election_year"].astype(int)
        national["share"] = pd.to_numeric(national["share"], errors="coerce")

    factor_frames = {}
    for metric_key in country_config.supported_factors:
        path = _factor_file(country_config, metric_key)
        frame = pd.read_csv(path) if path.exists() else pd.DataFrame(columns=["municipality", "year", "value"])
        if not frame.empty:
            frame["year"] = frame["year"].astype(int)
            frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
        factor_frames[metric_key] = frame

    return {
        "municipal": municipal,
        "national": national,
        "factor_frames": factor_frames,
    }


def _latest_metric_series(metric_key: str, factor_frames: dict[str, pd.DataFrame]) -> pd.DataFrame:
    frame = factor_frames.get(metric_key, pd.DataFrame())
    if frame.empty:
        return pd.DataFrame(columns=["public_geography_id", "municipality", "metric", "metric_year", "reference_period"])
    year = int(frame["year"].max())
    current = frame[frame["year"] == year][["public_geography_id", "municipality", "value", "year", "reference_period"]].copy()
    current["public_geography_id"] = current["public_geography_id"].astype(str)
    current["metric"] = pd.to_numeric(current["value"], errors="coerce")
    current = current.rename(columns={"year": "metric_year"})
    return current[["public_geography_id", "municipality", "metric", "metric_year", "reference_period"]].dropna(subset=["metric"])


def _metric_label(metric_key: str) -> str:
    for key, _label, metric_label in BELGIUM_METRIC_OPTIONS:
        if key == metric_key:
            return metric_label
    return metric_key


def get_belgium_party_profiles(municipal_df: pd.DataFrame) -> pd.DataFrame:
    if municipal_df.empty:
        return pd.DataFrame(columns=["party", "municipality_count", "mean_share", "default_public"])
    stats = (
        municipal_df[municipal_df["share"] > 0]
        .groupby("party", as_index=False)
        .agg(
            municipality_count=("municipality", "nunique"),
            mean_share=("share", "mean"),
        )
    )
    stats["default_public"] = (
        (stats["municipality_count"] >= BELGIUM_DEFAULT_PARTY_MIN_MUNICIPALITIES)
        & (stats["mean_share"] >= BELGIUM_DEFAULT_PARTY_MIN_MEAN_SHARE)
    )
    return stats.sort_values(["default_public", "mean_share", "municipality_count"], ascending=[False, False, False]).reset_index(drop=True)


def _finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note, context_label=None):
    context = f'<div class="copy-label" style="margin-bottom:0.3rem;">{context_label}</div>' if context_label else ""
    copy_block = ""
    if copy_sentence:
        copy_label = "Use with caution:" if strength_tag.startswith("WEAK PATTERN") else "Write this as:"
        copy_block = f'<div class="copy-label">{copy_label}</div><div class="copy-box">{copy_sentence}</div>'
    return (
        f'<div class="finding {strength_cls}">'
        f'<div class="strength-tag">{strength_tag}</div>'
        f'{context}'
        f'<div class="headline">{headline}</div>'
        f'<div class="body">{concrete}</div>'
        f'{copy_block}'
        f'<div class="footnote">{note}</div>'
        '</div>'
    )


def _result_divider():
    st.markdown(
        "<div style='margin:2rem 0 0.5rem;border-top:2px solid #0d0d14;'>"
        "<span style='font-size:0.58rem;font-weight:700;letter-spacing:0.18em;text-transform:uppercase;"
        "color:#0d0d14;background:#f5f5f7;padding:0 0.6rem;position:relative;top:-0.7rem;'>RESULT</span>"
        "</div>",
        unsafe_allow_html=True,
    )


def _how_to_read():
    with st.expander("How to read this result"):
        st.markdown(
            """
**STRONG PATTERN (abs(r) >= 0.70)** - Data shows a clear municipality-level relationship.

**MODERATE PATTERN (abs(r) 0.50-0.70)** - There is a consistent tendency, but it is still not a causal claim.

**WEAK PATTERN (abs(r) 0.30-0.50)** - Useful as a lead, not as a conclusion.

**NO PATTERN (abs(r) below 0.30)** - Do not write a pattern claim.

The result is Pearson correlation across municipalities. It can show whether vote share and a factor move together, but it does not prove why.
"""
        )


def _format_party(party, country_config, party_name_mode, *, compact=False, prose=False):
    return format_party_name(
        party,
        metadata=country_config.party_metadata,
        mode=party_name_mode,
        compact=compact,
        prose=prose,
    )


def _preferred_index(options: list[str], preferred: str, fallback: int = 0) -> int:
    if preferred in options:
        return options.index(preferred)
    if not options:
        return 0
    return min(fallback, len(options) - 1)


def _party_options(municipal_df: pd.DataFrame, year: int) -> list[str]:
    year_frame = municipal_df[municipal_df["election_year"] == year].copy()
    if year_frame.empty:
        return []
    profiles = get_belgium_party_profiles(year_frame)
    return profiles["party"].tolist()


def compute_belgium_correlation(municipal_year: pd.DataFrame, factor_frames: dict[str, pd.DataFrame], *, party: str, metric_key: str) -> dict:
    votes = municipal_year[municipal_year["party"] == party][["public_geography_id", "municipality", "share"]].copy()
    votes["public_geography_id"] = votes["public_geography_id"].astype(str)
    metric_series = _latest_metric_series(metric_key, factor_frames)
    merged = votes.merge(metric_series, on="public_geography_id", how="inner", suffixes=("", "_factor"))
    return compute_correlation_result(
        merged,
        factor=_metric_label(metric_key),
        party=party,
        year=int(municipal_year["election_year"].iloc[0]) if not municipal_year.empty else 2024,
        mode="explore-belgium",
    )


def render(country_config, selected_country_label, runtime_context):
    bundle = load_bundle(country_config)
    municipal = bundle["municipal"]
    national = bundle["national"]
    factor_frames = bundle["factor_frames"]

    with st.sidebar:
        st.markdown('<div class="hr-wordmark">HEDEGREEN RESEARCH<span class="dot"> *</span></div>', unsafe_allow_html=True)
        st.markdown("**Belgian Politics Data**")
        st.markdown(
            "<p style='font-size:0.75rem;color:#6a6a7a;line-height:1.6;margin-top:0.3rem;'>"
            f"{_surface_sidebar_text()}"
            "</p>",
            unsafe_allow_html=True,
        )
        st.divider()
        party_name_mode = st.selectbox("Party names", PARTY_NAME_MODES, index=1, key="belgium_party_name_mode")
        st.divider()
        page = st.radio(
            "nav",
            ["Explore", "Compare municipalities", "By Municipality", "National result", "About & sources"],
            label_visibility="collapsed",
            key="belgium_page",
        )
        st.divider()
        render_country_sidebar_footer(country_config)

    if page == "Explore":
        if "belgium_all_parties" not in st.session_state:
            st.session_state["belgium_all_parties"] = True
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            "Belgian Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("Is there a pattern?")
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:2rem;'>"
            f"{_surface_intro_text()}"
            "</p>",
            unsafe_allow_html=True,
        )

        st.markdown('<div class="step-label">Step 1 — Which election year?</div>', unsafe_allow_html=True)
        year = st.selectbox(
            "year",
            options=sorted(BELGIUM_LIVE_YEARS, reverse=True),
            index=0,
            key="belgium_year",
            label_visibility="collapsed",
        )
        municipal_year = municipal[municipal["election_year"] == year].copy()

        available_metric_items = [
            (key, label, metric_label)
            for key, label, metric_label in BELGIUM_METRIC_OPTIONS
            if not _latest_metric_series(key, factor_frames).empty
        ]
        metric_labels = [label for _, label, _ in available_metric_items]
        if "belgium_cx_factors" not in st.session_state:
            st.session_state["belgium_cx_factors"] = metric_labels[:1]
        current_factors = [label for label in st.session_state.get("belgium_cx_factors", []) if label in metric_labels]
        if not current_factors and metric_labels:
            current_factors = metric_labels[:1]
        st.session_state["belgium_cx_factors"] = current_factors

        st.markdown('<div class="step-label" style="margin-top:1rem;">Step 2 — What factors are available?</div>', unsafe_allow_html=True)
        selected_metric_labels = st.pills(
            "belgium-factors",
            metric_labels,
            key="belgium_cx_factors",
            selection_mode="multi",
            label_visibility="collapsed",
        )
        if not selected_metric_labels:
            st.markdown(
                "<p style='font-size:0.74rem;color:#8888a0;margin-bottom:0;'>"
                "No factor is currently selected. Municipality-level pattern analysis requires at least one factor."
                "</p>",
                unsafe_allow_html=True,
            )

        party_profiles = get_belgium_party_profiles(municipal_year)
        all_party_options = party_profiles["party"].tolist()
        default_party_options = party_profiles.loc[party_profiles["default_public"], "party"].tolist()
        st.markdown('<div class="step-label" style="margin-top:1rem;">Step 3 — Pick parties</div>', unsafe_allow_html=True)
        include_low_coverage = st.checkbox(
            "Show smaller parties too",
            key="belgium_include_low_coverage",
            help="Default Belgium view keeps only parties with at least 25 municipalities and at least 0.5% mean municipality vote share.",
        )
        party_options = all_party_options if include_low_coverage else default_party_options
        if "belgium_parties" not in st.session_state:
            st.session_state["belgium_parties"] = party_options[:5]
        current_selected = [party for party in st.session_state.get("belgium_parties", []) if party in party_options]
        if not current_selected:
            current_selected = party_options[:] if st.session_state.get("belgium_all_parties") else party_options[:1]
        st.session_state["belgium_parties"] = current_selected
        select_all = st.checkbox("All parties", key="belgium_all_parties")
        if select_all:
            selected_parties = party_options
            st.session_state["belgium_parties"] = party_options
        else:
            selected_parties = st.pills(
                "belgium-parties",
                party_options,
                key="belgium_parties",
                selection_mode="multi",
                format_func=lambda party: format_party_name(party, metadata=country_config.party_metadata, mode=party_name_mode, compact=True),
                label_visibility="collapsed",
            )
            if not selected_parties:
                st.markdown(
                    "<p style='font-size:0.74rem;color:#8888a0;margin-top:0.45rem;margin-bottom:0;'>"
                    "No party is currently selected. Municipality-level pattern analysis requires at least one party selection."
                    "</p>",
                    unsafe_allow_html=True,
                )
        st.markdown(
            "<p style='font-size:0.72rem;color:#8888a0;margin-top:0.35rem;margin-bottom:0;'>"
            "Default party view filters out micro-parties and very small lists.</p>",
            unsafe_allow_html=True,
        )

        if not selected_metric_labels or not selected_parties:
            st.markdown(
                '<div class="finding weak">'
                '<div class="strength-tag">SELECTION INCOMPLETE</div>'
                '<div class="headline">This analysis cannot run yet.</div>'
                '<div class="body">Belgium municipality-level correlation requires at least one factor and at least one party selection.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            return

        factor_label_to_key = {label: key for key, label, _ in available_metric_items}
        results = []
        for party in selected_parties:
            for metric_label in selected_metric_labels:
                metric_key = factor_label_to_key[metric_label]
                computed = compute_belgium_correlation(municipal_year, factor_frames, party=party, metric_key=metric_key)
                results.append(
                    {
                        "party": party,
                        "factor": metric_label,
                        "metric_key": metric_key,
                        "label": _metric_label(metric_key),
                        "r": computed["r"],
                        "merged": computed["merged"],
                        "valid": computed["valid"],
                        "strength": corr_strength_label(computed["r"]),
                    }
                )

        valid_results = [row for row in results if row["valid"]]
        if not valid_results:
            st.markdown(
                '<div class="finding weak">'
                '<div class="strength-tag">NO VALID RESULT</div>'
                '<div class="headline">No valid Belgium result is available.</div>'
                '<div class="body">The current selection did not produce a reliable municipality-level correlation value.</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            return

        _result_divider()

        if len(selected_parties) == 1 and len(selected_metric_labels) == 1:
            row = valid_results[0]
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_country_finding(
                row["r"],
                row["factor"],
                row["label"],
                row["party"],
                year,
                row["merged"],
                party_name_mode,
                country_config,
            )
            st.markdown(_finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
            _how_to_read()

            metric_short = METRIC_SHORT_LABELS.get(row["factor"], row["label"])
            ranked = row["merged"].sort_values("metric").rename(
                columns={
                    "municipality": "Municipality",
                    "metric": metric_short,
                    "share": "Vote share",
                }
            )
            tab_low, tab_high = st.tabs([f"Lowest {metric_short}", f"Highest {metric_short}"])
            with tab_low:
                render_compact_dataframe(ranked.head(10)[["Municipality", metric_short, "Vote share"]])
            with tab_high:
                render_compact_dataframe(ranked.tail(10).sort_values(metric_short, ascending=False)[["Municipality", metric_short, "Vote share"]])

        elif len(selected_parties) == 1 and len(selected_metric_labels) > 1:
            ranked = sorted(valid_results, key=lambda row: abs(float(row["r"])), reverse=True)
            summary = pd.DataFrame(
                [
                    {
                        "Factor": row["factor"],
                        "Label": row["factor"],
                        "r": row["r"],
                        "Strength": row["strength"],
                    }
                    for row in ranked
                ]
            )
            st.markdown(
                "<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>"
                "Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>",
                unsafe_allow_html=True,
            )
            render_bar_chart(summary, "Label", "r", tooltip_label="Factor", full_label_col="Factor")
            meaningful = [row for row in ranked if abs(float(row["r"])) >= 0.30] or ranked[:1]
            no_pattern = [row for row in ranked if abs(float(row["r"])) < 0.30]
            for row in meaningful:
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_country_finding(
                    row["r"], row["factor"], row["label"], row["party"], year, row["merged"], party_name_mode, country_config
                )
                st.markdown(_finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
            if no_pattern:
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>No pattern found for: {', '.join(row['factor'] for row in no_pattern)} (abs(r) below 0.30).</p>",
                    unsafe_allow_html=True,
                )
            _how_to_read()
            with st.expander("See full ranking table"):
                render_compact_dataframe(summary[["Factor", "r", "Strength"]])

        elif len(selected_parties) > 1 and len(selected_metric_labels) == 1:
            ranked = sorted(valid_results, key=lambda row: abs(float(row["r"])), reverse=True)
            summary = pd.DataFrame(
                [
                    {
                        "Party": _format_party(row["party"], country_config, party_name_mode, compact=True),
                        "Party_full": _format_party(row["party"], country_config, party_name_mode),
                        "r": row["r"],
                        "Strength": row["strength"],
                    }
                    for row in ranked
                ]
            )
            st.markdown(
                "<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.3rem;'>"
                "Results are ranked by correlation strength (absolute value). Positive = more votes where factor is higher. Negative = more votes where factor is lower.</p>",
                unsafe_allow_html=True,
            )
            render_bar_chart(summary, "Party", "r", tooltip_label="Party", full_label_col="Party_full")
            meaningful = [row for row in ranked if abs(float(row["r"])) >= 0.30] or ranked[:1]
            no_pattern = [row for row in ranked if abs(float(row["r"])) < 0.30]
            for row in meaningful:
                strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_country_finding(
                    row["r"], row["factor"], row["label"], row["party"], year, row["merged"], party_name_mode, country_config
                )
                st.markdown(_finding_html(strength_cls, strength_tag, headline, concrete, copy_sentence, note), unsafe_allow_html=True)
            if no_pattern:
                st.markdown(
                    f"<p style='font-size:0.75rem;color:#aaaabc;margin-top:0.5rem;'>No pattern found for: {', '.join(_format_party(row['party'], country_config, party_name_mode, compact=True) for row in no_pattern)} (abs(r) below 0.30).</p>",
                    unsafe_allow_html=True,
                )
            _how_to_read()
            with st.expander("See full ranking table"):
                render_compact_dataframe(summary[["Party_full", "r", "Strength"]], rename_map={"Party_full": "Party"})

        else:
            top = max(valid_results, key=lambda item: abs(float(item["r"])))
            strength_cls, strength_tag, headline, concrete, copy_sentence, note = build_country_finding(
                top["r"],
                top["factor"],
                top["label"],
                top["party"],
                year,
                top["merged"],
                party_name_mode,
                country_config,
            )
            st.markdown(
                "<p style='font-size:0.75rem;color:#aaaabc;margin-bottom:0.5rem;'>"
                "Showing highest correlation across selected factors and parties. Use the full correlation table to inspect all results.</p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                _finding_html(
                    strength_cls,
                    strength_tag,
                    headline,
                    concrete,
                    copy_sentence,
                    note,
                    context_label=f"Strongest signal: {_format_party(top['party'], country_config, party_name_mode, compact=True)} x {top['factor']}",
                ),
                unsafe_allow_html=True,
            )
            _how_to_read()
            with st.expander("See full correlation table"):
                flat_df = pd.DataFrame(
                    [
                        {
                            "Party": _format_party(row["party"], country_config, party_name_mode),
                            "Factor": row["factor"],
                            "r": row["r"],
                            "Strength": row["strength"],
                            "Rows": len(row["merged"]),
                        }
                        for row in valid_results
                    ]
                ).assign(abs_r=lambda frame: frame["r"].abs()).sort_values("abs_r", ascending=False).drop(columns="abs_r")
                render_compact_dataframe(flat_df)
        return

    if page == "Compare municipalities":
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            "Belgian Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("Compare two municipalities")
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>"
            "Pick two municipalities and compare their 2024 Chamber vote profile and current Statbel factor layer.</p>",
            unsafe_allow_html=True,
        )
        compare_year = st.selectbox("Election year", sorted(BELGIUM_LIVE_YEARS, reverse=True), index=0, key="belgium_compare_year")
        compare_votes = municipal[municipal["election_year"] == compare_year].copy()
        municipalities_for_year = sorted(compare_votes["municipality"].dropna().unique().tolist())
        col1, col2 = st.columns(2)
        with col1:
            mun_a = st.selectbox(
                "Municipality A",
                municipalities_for_year,
                index=_preferred_index(municipalities_for_year, "Bruxelles"),
                key="belgium_compare_a",
            )
        with col2:
            mun_b = st.selectbox(
                "Municipality B",
                municipalities_for_year,
                index=_preferred_index(municipalities_for_year, "Anvers", fallback=1),
                key="belgium_compare_b",
            )
        if mun_a == mun_b:
            st.warning("Select two different municipalities.")
            return

        st.markdown("## Voting patterns")
        votes_a = compare_votes[compare_votes["municipality"] == mun_a].set_index("party")["share"]
        votes_b = compare_votes[compare_votes["municipality"] == mun_b].set_index("party")["share"]
        common = votes_a.index.intersection(votes_b.index)
        if len(common):
            gap_series = (votes_a[common] - votes_b[common]).sort_values(key=lambda series: series.abs(), ascending=False)
            top_parties = gap_series.head(8).index.tolist()
            gap_chart_df = pd.DataFrame(
                {
                    "Party": [_format_party(party, country_config, party_name_mode, compact=True) for party in top_parties],
                    "Party_full": [_format_party(party, country_config, party_name_mode) for party in top_parties],
                    "Gap": [float(gap_series[party]) for party in top_parties],
                }
            )
            st.markdown(
                f"<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.5rem;'>"
                f"Percentage point gap in vote share: <strong>{mun_a}</strong> minus <strong>{mun_b}</strong>. "
                f"Positive bar = {mun_a} votes more for that party. Negative = {mun_b} does.</p>",
                unsafe_allow_html=True,
            )
            render_bar_chart(gap_chart_df, "Party", "Gap", tooltip_label="Party", full_label_col="Party_full")
            biggest_party = gap_series.index[0]
            biggest_gap = float(gap_series.iloc[0])
            direction = mun_a if biggest_gap > 0 else mun_b
            st.markdown(
                f'<div class="finding moderate">'
                f'<div class="headline">Biggest difference: {_format_party(biggest_party, country_config, party_name_mode, prose=True)}</div>'
                f'<div class="body"><strong>{direction}</strong> is currently <strong>{abs(biggest_gap):.1f} percentage points</strong> higher on this party in the Belgium {compare_year} bridge-safe municipality layer.</div>'
                f'<div class="footnote">Chamber {compare_year} · {_surface_label()} · {country_config.source_note}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            with st.expander("See full vote snapshot for both municipalities"):
                display_parties = gap_series.index.tolist()
                tab_a, tab_b = st.tabs([mun_a, mun_b])
                with tab_a:
                    votes_a_display = votes_a[display_parties].round(2).reset_index()
                    votes_a_display["party"] = votes_a_display["party"].apply(lambda value: _format_party(value, country_config, party_name_mode))
                    render_compact_dataframe(votes_a_display.rename(columns={"party": "Party", "share": "Vote %"}))
                with tab_b:
                    votes_b_display = votes_b[display_parties].round(2).reset_index()
                    votes_b_display["party"] = votes_b_display["party"].apply(lambda value: _format_party(value, country_config, party_name_mode))
                    render_compact_dataframe(votes_b_display.rename(columns={"party": "Party", "share": "Vote %"}))

        st.markdown("## Current factor profile")
        st.markdown(
            "<p style='font-size:0.82rem;color:#6a6a7a;margin-bottom:0.8rem;'>"
            "Factor profile uses the newest available Statbel municipality factor for each metric. Source periods are visible in About & sources.</p>",
            unsafe_allow_html=True,
        )
        geo_lookup = compare_votes.drop_duplicates("municipality").set_index("municipality")["public_geography_id"].astype(str)
        geo_a = geo_lookup.get(mun_a)
        geo_b = geo_lookup.get(mun_b)
        cards = []
        for metric_key, label, _metric_text in BELGIUM_METRIC_OPTIONS:
            metric_series = _latest_metric_series(metric_key, factor_frames)
            left_value = metric_series.loc[metric_series["public_geography_id"] == str(geo_a), "metric"]
            right_value = metric_series.loc[metric_series["public_geography_id"] == str(geo_b), "metric"]
            reference = metric_series["reference_period"].dropna().iloc[0] if "reference_period" in metric_series.columns and not metric_series["reference_period"].dropna().empty else ""
            cards.append(
                {
                    "Metric": label,
                    mun_a: f"{left_value.iloc[0]:.2f}" if not left_value.empty else "-",
                    mun_b: f"{right_value.iloc[0]:.2f}" if not right_value.empty else "-",
                    "Year": str(compare_year),
                    "Reference": reference,
                }
            )
        render_profile_cards(cards, mun_a, mun_b)
        return

    if page == "By Municipality":
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            "Belgian Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("By Municipality")
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>"
            "Pick a party and see where that party was strongest and weakest across the bridge-safe Belgium municipality layer.</p>",
            unsafe_allow_html=True,
        )
        col1, col2 = st.columns(2)
        with col1:
            year = st.selectbox("Election year", options=sorted(BELGIUM_LIVE_YEARS, reverse=True), index=0, key="belgium_municipality_year")
        with col2:
            party_options = _party_options(municipal, year)
            party = st.selectbox(
                "Party",
                party_options,
                format_func=lambda value: _format_party(value, country_config, party_name_mode),
                key="belgium_single_party",
            )
        municipal_year = municipal[municipal["election_year"] == year].copy()
        filtered = municipal_year[municipal_year["party"] == party].sort_values("share", ascending=False)
        if filtered.empty:
            st.warning("No municipality rows are available for this selection.")
            return
        top = filtered.iloc[0]
        bottom = filtered.iloc[-1]
        avg = filtered["share"].mean()
        party_label = _format_party(party, country_config, party_name_mode, prose=True)
        st.markdown(
            f"<p style='font-size:0.86rem;color:#3a3a4a;margin-bottom:0.35rem;'>"
            f"In <strong>{year}</strong>, <strong>{party_label}</strong> had its highest bridge-safe municipality share in "
            f"<strong>{top['municipality']}</strong> ({top['share']:.1f}%) and its lowest in "
            f"<strong>{bottom['municipality']}</strong> ({bottom['share']:.1f}%). "
            f"The unweighted municipality average was <strong>{avg:.1f}%</strong>.</p>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<p style='font-size:0.74rem;color:#8888a0;margin-bottom:0.8rem;'>"
            "The table is sorted by local vote share. `Vote %` is the party's share of valid votes in that municipality, not the national result.</p>",
            unsafe_allow_html=True,
        )
        display = filtered[["municipality", "votes", "valid_votes", "share"]].rename(
            columns={
                "municipality": "Municipality",
                "votes": "Votes",
                "valid_votes": "Valid votes",
                "share": "Vote %",
            }
        )
        render_compact_dataframe(display)
        with st.expander("Show full municipality ranking chart"):
            render_bar_chart(
                filtered.assign(municipality_label=filtered["municipality"]),
                "municipality_label",
                "share",
                tooltip_label="Municipality",
                full_label_col="municipality",
            )
        return

    if page == "National result":
        st.markdown(
            "<p style='font-size:0.65rem;font-weight:500;letter-spacing:0.12em;text-transform:uppercase;color:#aaaabc;margin-bottom:0.2rem;'>"
            "Belgian Politics Data</p>",
            unsafe_allow_html=True,
        )
        st.title("National result")
        if national.empty:
            st.warning("No national result file is available.")
            return
        st.markdown(
            "<p style='font-size:0.95rem;color:#5a5a6a;margin-bottom:1.5rem;'>"
            "Official Belgium country-total Chamber result for 2024. This is not a trend view yet; it is the national snapshot beside the municipality layer.</p>",
            unsafe_allow_html=True,
        )
        parties_nat = national.sort_values("share", ascending=False)["party"].tolist()
        default_nat = parties_nat[:10]
        selected = st.multiselect(
            "Parties",
            parties_nat,
            default=default_nat,
            format_func=lambda party: _format_party(party, country_config, party_name_mode, compact=True),
            key="belgium_national_parties",
        )
        if selected:
            chart_df = national[national["party"].isin(selected)].copy().sort_values("share", ascending=True)
            chart_df["party_label"] = chart_df["party"].apply(lambda party: _format_party(party, country_config, party_name_mode, compact=True))
            render_bar_chart(chart_df, "party_label", "share", tooltip_label="Party", full_label_col="party")
            render_compact_dataframe(
                chart_df.sort_values("share", ascending=False)[["party", "votes", "valid_votes", "share", "seats"]].rename(
                    columns={
                        "party": "Party",
                        "votes": "Votes",
                        "valid_votes": "Valid votes",
                        "share": "Vote %",
                        "seats": "Seats",
                    }
                )
            )
        st.markdown(
            "<p style='font-size:0.72rem;color:#8888a0;margin-top:0.8rem;'>"
            "Source: official IBZ country-total Chamber row for 2024-06-09. The Explore page uses bridge-safe municipality rows, so the source scope is related but not identical.</p>",
            unsafe_allow_html=True,
        )
        return

    st.title("About & sources")
    st.markdown(_about_boundary_text())
    factor_summary = []
    for metric_key, label, metric_label in BELGIUM_METRIC_OPTIONS:
        frame = factor_frames.get(metric_key, pd.DataFrame())
        if frame.empty:
            continue
        factor_summary.append(
            {
                "Factor": label,
                "Metric": metric_label,
                "Rows": len(frame),
                "Years": ", ".join(str(year) for year in sorted(frame["year"].dropna().unique())),
                "Status": frame["comparability_status"].dropna().iloc[0] if "comparability_status" in frame.columns and not frame["comparability_status"].dropna().empty else "country_local",
            }
        )
    render_compact_dataframe(pd.DataFrame(factor_summary))
