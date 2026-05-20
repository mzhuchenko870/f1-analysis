"""F1 Analytics — shared plumbing.

Helpers used across the 9 notebooks. ONLY infrastructure lives here:
loading CSVs, dropping Indy 500 entries, the chart save/show helper, default
styling, and the 9-era reference table. Analytical pandas/SQL stays inside
each notebook so the analysis is readable in isolation.

Typical setup at the top of a notebook:

    from f1_utils import (
        load_tables, remove_indy_500, show_and_save,
        apply_default_style, eras_df, year_to_era,
    )

    apply_default_style()
    tables = load_tables(['results', 'races', 'drivers', 'constructors'])
    tables = remove_indy_500(tables)
    results, races, drivers, constructors = (
        tables['results'], tables['races'], tables['drivers'], tables['constructors']
    )
"""

from __future__ import annotations

import os
from typing import Iterable

import pandas as pd


EXCEL_DIR = 'excel'
CHARTS_DIR = 'charts'


# ---------------------------------------------------------------------------
# CSV loading
# ---------------------------------------------------------------------------

def load_tables(names: Iterable[str]) -> dict[str, pd.DataFrame]:
    """Load the requested CSVs from `excel/`.

    `names` is the bare table name without the .csv suffix, e.g.
    ['results', 'races', 'drivers']. Returns a dict keyed by table name.

    Raises FileNotFoundError if any requested CSV is missing — fail loud so
    a typo in a notebook is caught immediately rather than silently merging
    against an empty DataFrame later.
    """
    out: dict[str, pd.DataFrame] = {}
    for name in names:
        path = os.path.join(EXCEL_DIR, f'{name}.csv')
        if not os.path.isfile(path):
            raise FileNotFoundError(
                f'{path} not found. Expected one of: '
                f'{sorted(f[:-4] for f in os.listdir(EXCEL_DIR) if f.endswith(".csv"))}'
            )
        out[name] = pd.read_csv(path)
    return out


# ---------------------------------------------------------------------------
# Indianapolis 500 cleanup
# ---------------------------------------------------------------------------

# Tables that can hold raceId references and therefore need filtering
_INDY_RACE_ID_TABLES = (
    'results', 'qualifying', 'driver_standings',
    'constructor_standings', 'constructor_results', 'lap_times',
    'pit_stops', 'sprint_results',
)


def remove_indy_500(tables: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Drop the 11 Indianapolis 500 races (1950–1960) from a tables dict.

    Why: the Indy 500 was nominally part of the F1 World Championship from
    1950 to 1960 but was a separate American oval race. Most "drivers" in
    those rows never raced any other F1 round, so leaving them in pollutes
    per-driver statistics. Strip once at the source.

    Requires `tables` to contain at least 'races'. Filters every other table
    in `tables` that has a raceId column.

    Returns a new dict (the inputs are not mutated).
    """
    if 'races' not in tables:
        raise KeyError(
            "remove_indy_500 needs 'races' in the tables dict to identify "
            "Indy raceIds. Add 'races' to load_tables() and retry."
        )

    races = tables['races']
    indy_race_ids = races.loc[
        races['name'].str.contains('Indianapolis', case=False, na=False),
        'raceId',
    ]

    out: dict[str, pd.DataFrame] = {}
    for name, df in tables.items():
        if name == 'races':
            out[name] = races[~races['raceId'].isin(indy_race_ids)].copy()
        elif 'raceId' in df.columns and name in _INDY_RACE_ID_TABLES:
            out[name] = df[~df['raceId'].isin(indy_race_ids)].copy()
        else:
            out[name] = df

    return out


# ---------------------------------------------------------------------------
# Chart save + display
# ---------------------------------------------------------------------------

def show_and_save(filename: str, dpi: int = 150) -> None:
    """Save the current matplotlib figure to charts/ AND display it inline.

    Naming convention: '<section>.<question>_<slug>.png'
        e.g. '1.3a_pole_positions.png', '7.4_most_popular_circuits.png'
    See QuestionsF1.txt for the section/question numbering.

    Always savefig BEFORE show — show() can clear the figure on some backends.
    """
    import matplotlib.pyplot as plt
    os.makedirs(CHARTS_DIR, exist_ok=True)
    plt.savefig(os.path.join(CHARTS_DIR, filename), dpi=dpi, bbox_inches='tight')
    plt.show()


# ---------------------------------------------------------------------------
# Default seaborn / matplotlib styling
# ---------------------------------------------------------------------------

def apply_default_style() -> None:
    """Apply the project-wide chart style. Idempotent — safe to call repeatedly."""
    import seaborn as sns
    sns.set_theme(style='whitegrid')


# ---------------------------------------------------------------------------
# F1 era reference table
# ---------------------------------------------------------------------------
# The canonical 9-era split used across the project. Eras are defined by major
# technical regulation changes (engine formulas, refuelling, downforce regs).
# Boundaries are inclusive on both ends.

# Mirrors the canonical definition in `Statistics for each Era.ipynb`.
# Columns + boundaries must stay in sync with that notebook.
_eras = [
    # (era_id, name_ru,                                                    name_en,                                year_start, year_end, engine,                                  dominant,                          key_feature)
    (1, 'Пред-аэродинамическая / Переднемоторная эра',                     'Pre-aerodynamic / Front-engine',       1950, 1958, 'Front-engine, NA 1.5L s/c or 4.5L NA', 'Alfa Romeo, Mercedes, Ferrari',    'No wings, no aero — driver skill on narrow tyres; Fangio wins 5 titles'),
    (2, 'Заднемоторная революция',                                         'Rear-engine revolution',               1959, 1967, 'NA 1.5–3.0L (rear-mounted)',           'Cooper, Lotus, BRM',               'Cooper proves the rear-engine layout; Jim Clark / Lotus dominance'),
    (3, 'Эра крыльев и аэродинамики',                                      'Wings & aerodynamics',                 1968, 1982, 'NA 3.0L (Cosworth DFV era)',           'Lotus, Ferrari, McLaren',          'First wings (1968), ground effect (Lotus 78/79), DFV available to all'),
    (4, 'Турбоэра',                                                         'Turbo era',                            1983, 1988, '1.5L turbo (up to ~1300 hp qual.)',    'McLaren-Honda, Williams-Honda',    'Renault pioneers turbos; Honda/Porsche dominate; Senna vs Prost'),
    (5, 'Золотая эра активной подвески / Бестурбоэра',                     'Active suspension / post-turbo',       1989, 1993, 'NA 3.5L V8/V10/V12',                   'Williams, McLaren',                'Active suspension, traction control, ABS; Williams FW14B'),
    (6, 'Запрет электроники / Пред-V10-эра',                               'Driver-aid ban / pre-V10 dominance',   1994, 1999, 'NA 3.0L (mixed V8/V10/V12)',           'Williams, Ferrari, McLaren',       'Active aids banned after Senna death; Schumacher 1st titles; V10 becomes standard'),
    (7, 'Эра V10 / Доминация Ferrari и Шумахера',                          'V10 era',                              2000, 2005, 'NA 3.0L V10 (~19 000 rpm)',            'Ferrari',                          'Schumacher + Ferrari win 5 straight titles'),
    (8, 'Эра V8 / Запрет электроники',                                     'V8 / Limited electronics',             2006, 2013, 'NA 2.4L V8',                           'Red Bull (late), Brawn, Ferrari',  'V8s replace V10s; KERS introduced 2009; Vettel 4 titles 2010-13'),
    (9, 'Гибридная эра V6 Turbo',                                          'Hybrid V6 Turbo',                      2014, 2025, '1.6L V6 turbo hybrid (MGU-K + MGU-H)', 'Mercedes, Red Bull',               'Mercedes 8 constructor titles; Hamilton 6 / Verstappen 4 titles'),
]

eras_df = pd.DataFrame(
    _eras,
    columns=['era_id', 'name_ru', 'name_en',
             'year_start', 'year_end',
             'engine', 'dominant', 'key_feature'],
)

# Contiguous + non-overlapping boundary check
assert (eras_df['year_start'].iloc[1:].values
        == eras_df['year_end'].iloc[:-1].values + 1).all(), 'Era boundaries are not contiguous!'


def year_to_era(year: int | float, table: pd.DataFrame = eras_df) -> int | None:
    """Map a year to its era_id (1–9). Returns None for years outside the table."""
    if pd.isna(year):
        return None
    year = int(year)
    match = table[(table['year_start'] <= year) & (year <= table['year_end'])]
    if match.empty:
        return None
    return int(match['era_id'].iloc[0])
