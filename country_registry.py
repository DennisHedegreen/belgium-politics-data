from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent


BASE_FACTOR_CATALOG = {'population': {'label': 'Population',
                'metric_label': 'Population (reference count)',
                'question': 'Do larger municipalities vote differently?',
                'filename': 'population.csv',
                'comparability_status': 'country_local'},
 'density': {'label': 'Population density',
             'metric_label': 'Residents per km²',
             'question': 'Does dense settlement correlate with voting '
                         'behaviour?',
             'filename': 'population_density.csv',
             'comparability_status': 'country_local'},
 'age65': {'label': 'Age 65+',
           'metric_label': 'Share aged 65+ (%)',
           'question': 'Do older municipalities vote differently?',
           'filename': 'age65_pct.csv',
           'comparability_status': 'family_mapped'}}

PARTY_METADATA = {}


@dataclass(frozen=True)
class CountryConfig:
    country_id: str
    display_name: str
    adjective: str
    language: str
    statistics_source_name: str
    default_election_type: str
    election_label: str
    public_geography_type: str
    public_geography_label: str
    public_geography_label_plural: str
    public_geography_count: int
    supported_factors: tuple[str, ...]
    supported_elections: tuple[str, ...]
    internal_ready: bool
    public_ready: bool
    municipal_vote_path: Path
    national_vote_path: Path | None
    factor_dir: Path
    party_metadata: dict[str, dict[str, str]]
    source_note: str
    secondary_source_note: str | None = None

    def factor_catalog(self) -> list[dict[str, str]]:
        return [{**BASE_FACTOR_CATALOG[key], "key": key} for key in self.supported_factors]


COUNTRY = CountryConfig(
    country_id='belgium',
    display_name='Belgium',
    adjective='Belgian',
    language='English',
    statistics_source_name='Statbel',
    default_election_type='chamber',
    election_label='Chamber election',
    public_geography_type='municipality',
    public_geography_label='municipality',
    public_geography_label_plural='municipalities',
    public_geography_count=559,
    supported_factors=('population', 'density', 'age65'),
    supported_elections=('chamber',),
    internal_ready=True,
    public_ready=True,
    municipal_vote_path=ROOT / "belgium/chamber/chamber_party_share_by_2025_municipality_bridge_safe.csv",
    national_vote_path=ROOT / "belgium/chamber/chamber_national_vote_share.csv",
    factor_dir=ROOT / "belgium/factors",
    party_metadata=PARTY_METADATA,
    source_note='IBZ 2024 Chamber bridge-safe municipality layer + Statbel municipality indicators',
    secondary_source_note='Internal only: E5 special buckets and six facility/rand vote-sum mismatch rows remain held out.',
)


def get_country_config(country_id: str) -> CountryConfig:
    if country_id != COUNTRY.country_id:
        raise KeyError(f"Unknown country_id: {country_id}")
    return COUNTRY


def list_public_countries() -> list[CountryConfig]:
    return [COUNTRY] if COUNTRY.public_ready else []


def list_internal_countries() -> list[CountryConfig]:
    return [COUNTRY] if COUNTRY.internal_ready else []


def country_data_pack_exists(config: CountryConfig) -> bool:
    if not config.municipal_vote_path.exists():
        return False
    if not config.factor_dir.exists():
        return False
    return True


def _normalize_allowed_country_ids(allowed_country_ids: Iterable[str] | None) -> list[str] | None:
    if allowed_country_ids is None:
        return None
    return [country_id.strip().lower() for country_id in allowed_country_ids if country_id.strip()]


def list_exposed_countries(
    allowed_country_ids: Iterable[str] | None = None,
    *,
    allow_internal: bool = False,
    require_data_pack: bool = True,
) -> list[CountryConfig]:
    allowed = _normalize_allowed_country_ids(allowed_country_ids)
    if allow_internal:
        if not COUNTRY.internal_ready:
            return []
    elif not COUNTRY.public_ready:
        return []
    if allowed is None:
        if require_data_pack and not country_data_pack_exists(COUNTRY):
            return []
        return [COUNTRY]
    if COUNTRY.country_id not in allowed:
        return []
    if require_data_pack and not country_data_pack_exists(COUNTRY):
        return []
    return [COUNTRY]


def list_exposed_public_countries(
    allowed_country_ids: Iterable[str] | None = None,
    require_data_pack: bool = True,
) -> list[CountryConfig]:
    return list_exposed_countries(
        allowed_country_ids,
        allow_internal=False,
        require_data_pack=require_data_pack,
    )
