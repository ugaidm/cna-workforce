from shiny.express import input, render, ui
from shinywidgets import render_widget
from shiny import ui as shiny_ui
from shiny import reactive

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


# =========================
# LOAD DATA
# =========================

demo_cna = pd.read_excel("CNA summary.xlsx", sheet_name="State_Summary_CNAs")
demo_hoh = pd.read_excel("CNA summary.xlsx", sheet_name="State_Summary_CNAs_as_HoH")

state_notes = pd.read_excel("state_notes.xlsx", sheet_name="Observations")
national = pd.read_excel("national_comparison.xlsx")


# =========================
# STATE ABBREVIATIONS
# =========================

state_abbr = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT",
    "Delaware": "DE", "Florida": "FL",
    "Georgia": "GA", "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL",
    "Indiana": "IN", "Iowa": "IA", "Kansas": "KS", "Kentucky": "KY",
    "Louisiana": "LA", "Maine": "ME", "Maryland": "MD",
    "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH",
    "New Jersey": "NJ", "New Mexico": "NM", "New York": "NY",
    "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA",
    "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT",
    "Virginia": "VA", "Washington": "WA", "West Virginia": "WV",
    "Wisconsin": "WI", "Wyoming": "WY"
}

demo_cna["state_abbr"] = demo_cna["state_name"].map(state_abbr)
demo_hoh["state_abbr"] = demo_hoh["state_name"].map(state_abbr)

demo_cna = demo_cna.dropna(subset=["state_abbr"])
demo_hoh = demo_hoh.dropna(subset=["state_abbr"])


# =========================
# REACTIVE STATE SELECTION
# =========================

clicked_state = reactive.value("National")


def current_demo():
    if input.selected_group() == "hoh":
        return demo_hoh
    return demo_cna


def current_state():
    return clicked_state()


def selected_national_cna_column():
    if input.selected_group() == "hoh":
        return "national_cna_hoh"
    return "national_cna"


def selected_group_label():
    if input.selected_group() == "hoh":
        return "National CNA HoH"
    return "National CNA"


def national_value(metric, column):
    return national[national["metric"] == metric][column].iloc[0]


@reactive.effect
@reactive.event(input.selected_state)
def _():
    clicked_state.set(input.selected_state())


@reactive.effect
@reactive.event(input.reset_state)
def _():
    clicked_state.set("National")


# =========================
# PAGE SETTINGS
# =========================

ui.page_opts(title="CNA Demographic Explorer", fillable=True)

ui.tags.style("""
.compact-card {
    font-size: 0.82rem;
    height: 230px !important;
    min-height: 230px !important;
    max-height: 230px !important;
}

.compact-card .card-body {
    padding: 0.45rem !important;
    overflow-y: auto !important;
}

.compact-card p {
    margin-bottom: 0.18rem !important;
}

.compact-card ul {
    padding-left: 1rem;
    margin-bottom: 0;
}

.compact-card li {
    margin-bottom: 0.25rem;
}

.stat-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0px;
}

.stat-cell {
    width: 50%;
    margin-top: 8px;
}

.card-grid-3 {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 1rem;
}

.card-grid-4 {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 1rem;
}

@media (max-width: 1000px) {
    .card-grid-3,
    .card-grid-4 {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 700px) {
    .card-grid-3,
    .card-grid-4 {
        grid-template-columns: 1fr;
    }
}
""")


# =========================
# SIDEBAR
# =========================

with ui.sidebar():

    ui.h3("Controls")

    ui.input_select(
        "selected_state",
        "Choose a state",
        choices=["National"] + sorted(demo_cna["state_name"].dropna().unique().tolist())
    )

    ui.input_select(
        "selected_group",
        "Analyze group",
        choices={
            "cna": "All CNAs",
            "hoh": "CNAs as heads of household"
        }
    )

    ui.input_action_button("reset_state", "Reset to National")

    ui.p("Tip: You can click a state on the map.")


# =========================
# MAP TITLE
# =========================

ui.div(
    ui.h2("Average CNAs by State"),
    ui.p("Demographic characteristics of Certified Nursing Assistants across U.S. states."),
    style="""
        text-align:center;
        margin-top:0px;
        margin-bottom:-10px;
        padding-bottom:0px;
    """
)


# =========================
# MAP
# =========================

@render_widget
def map():

    metric = "avg_age"
    df = current_demo()
    state = current_state()

    fig = px.choropleth(
        df,
        locations="state_abbr",
        locationmode="USA-states",
        color=metric,
        hover_name="state_name",
        scope="usa",
        color_continuous_scale=[
            [0.0, "#f4f8fe"],
            [0.5, "#76a4e1"],
            [1.0, "#042554"]
        ],
        basemap_visible=False
    )

    if state == "National":
        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><extra></extra>"
        )
    else:
        selected_points = df.index[df["state_name"] == state].tolist()

        fig.update_traces(
            hovertemplate="<b>%{hovertext}</b><extra></extra>",
            selectedpoints=selected_points,
            selected=dict(marker=dict(opacity=1)),
            unselected=dict(marker=dict(opacity=0.35))
        )

    fig.update_geos(
        showlakes=False,
        showframe=False,
        showcountries=False,
        showcoastlines=False
    )

    fig.update_layout(
        autosize=True,
        height=520,
        margin=dict(l=0, r=0, t=5, b=0),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            projection_scale=0.85,
            center=dict(lat=37.8, lon=-96)
        ),
        clickmode="event+select"
    )

    fig_widget = go.FigureWidget(fig)

    def handle_click(trace, points, selector):
        if points.point_inds:
            idx = points.point_inds[0]
            clicked_state.set(df.iloc[idx]["state_name"])

    fig_widget.data[0].on_click(handle_click)

    return fig_widget


# =========================
# CARD HELPERS
# =========================

def stat_card(title, stats):
    cells = []

    for label, value in stats:
        cells.append(
            shiny_ui.div(
                shiny_ui.strong(label),
                shiny_ui.br(),
                value,
                class_="stat-cell"
            )
        )

    return shiny_ui.card(
        shiny_ui.card_header(title),
        shiny_ui.div(*cells, class_="stat-grid"),
        class_="compact-card"
    )


def national_main_demos_card():
    cna_col = selected_national_cna_column()
    label = selected_group_label()

    return stat_card(
        "National Main Demographics",
        [
            (f"{label} age", f"{national_value('avg_age', cna_col):.1f}"),
            ("US Resident age", f"{national_value('avg_age', 'national_all'):.1f}"),
            (f"{label} wages", f"${national_value('avg_wages', cna_col):,.0f}"),
            ("US Resident wages", f"${national_value('avg_wages', 'national_all'):,.0f}"),
        ]
    )


def average_cna_card():
    cna_col = selected_national_cna_column()
    label = selected_group_label()

    return stat_card(
        label,
        [
            ("Age", f"{national_value('avg_age', cna_col):.1f}"),
            ("Wages", f"${national_value('avg_wages', cna_col):,.0f}"),
            ("Under poverty", f"{national_value('pct_under_poverty', cna_col):.1f}%"),
        ]
    )


def average_person_card():
    return stat_card(
        "US Resident",
        [
            ("Age", f"{national_value('avg_age', 'national_all'):.1f}"),
            ("Wages", f"${national_value('avg_wages', 'national_all'):,.0f}"),
            ("Under poverty", f"{national_value('pct_under_poverty', 'national_all'):.1f}%"),
        ]
    )


def state_basics_card(state):
    df = current_demo()
    row = df[df["state_name"] == state].iloc[0]

    return stat_card(
        f"State Basics: {state}",
        [
            ("Age", f"{row.get('avg_age', 0):.1f}"),
            ("Percent female", f"{row.get('pct_female', 0):.1f}%"),
            ("Wages", f"${row.get('avg_wages', 0):,.0f}"),
            ("Under poverty", f"{row.get('pct_under_poverty', 0):.1f}%"),
        ]
    )


def observations_card(state):
    group = input.selected_group()

    state_obs = state_notes[state_notes["state_name"] == state]

    if group == "cna":
        state_obs = state_obs[state_obs["group"].isin(["CNA", "All CNAs"])]
    elif group == "hoh":
        state_obs = state_obs[state_obs["group"].isin(["HoH", "CNAs as heads of household"])]

    if len(state_obs) == 0:
        return shiny_ui.card(
            shiny_ui.card_header("Observations"),
            shiny_ui.p("No special observations available."),
            class_="compact-card"
        )

    grouped_sections = []

    for category, group_df in state_obs.groupby("category"):

        items = []

        for _, row in group_df.iterrows():
            obs_text = row.get("observation", "")

            if pd.notna(obs_text) and str(obs_text).strip() != "":
                items.append(shiny_ui.tags.li(str(obs_text)))

        if len(items) > 0:
            grouped_sections.append(
                shiny_ui.tags.div(
                    shiny_ui.tags.strong(str(category)),
                    shiny_ui.tags.ul(*items),
                    style="margin-bottom: 0.6rem;"
                )
            )

    if len(grouped_sections) == 0:
        grouped_sections.append(shiny_ui.p("No special observations available."))

    return shiny_ui.card(
        shiny_ui.card_header("Observations"),
        shiny_ui.div(
            *grouped_sections,
            style="""
                max-height: 170px;
                overflow-y: auto;
                padding-right: 6px;
            """
        ),
        class_="compact-card"
    )


def compare_to_cna_card(state):
    df = current_demo()
    row = df[df["state_name"] == state].iloc[0]
    cna_col = selected_national_cna_column()
    label = selected_group_label()

    bullets = []

    state_age = row.get("avg_age", None)
    nat_age = national_value("avg_age", cna_col)

    if pd.notna(state_age):
        diff = state_age - nat_age
        if diff > 0:
            bullets.append(f"{diff:.1f} years older than the {label} average")
        else:
            bullets.append(f"{abs(diff):.1f} years younger than the {label} average")

    state_wage = row.get("avg_wages", None)
    nat_wage = national_value("avg_wages", cna_col)

    if pd.notna(state_wage):
        diff = state_wage - nat_wage
        if diff > 0:
            bullets.append(f"${abs(diff):,.0f} higher wages than the {label} average")
        else:
            bullets.append(f"${abs(diff):,.0f} lower wages than the {label} average")

    state_poverty = row.get("pct_under_poverty", None)
    nat_poverty = national_value("pct_under_poverty", cna_col)

    if pd.notna(state_poverty):
        diff = state_poverty - nat_poverty
        if diff > 0:
            bullets.append(f"{abs(diff):.1f}% higher poverty rate than {label}")
        else:
            bullets.append(f"{abs(diff):.1f}% lower poverty rate than {label}")

    return shiny_ui.card(
        shiny_ui.card_header(f"Comparison to {label}"),
        shiny_ui.tags.ul(*[shiny_ui.tags.li(b) for b in bullets]),
        class_="compact-card"
    )


def compare_to_person_card(state):
    df = current_demo()
    row = df[df["state_name"] == state].iloc[0]

    bullets = []

    state_age = row.get("avg_age", None)
    nat_age = national_value("avg_age", "national_all")

    if pd.notna(state_age):
        diff = state_age - nat_age
        if diff > 0:
            bullets.append(f"{diff:.1f} years older than the national workforce average")
        else:
            bullets.append(f"{abs(diff):.1f} years younger than the national workforce average")

    state_wage = row.get("avg_wages", None)
    nat_wage = national_value("avg_wages", "national_all")

    if pd.notna(state_wage):
        diff = state_wage - nat_wage
        if diff > 0:
            bullets.append(f"${abs(diff):,.0f} higher wages than the national workforce average")
        else:
            bullets.append(f"${abs(diff):,.0f} lower wages than the national workforce average")

    state_poverty = row.get("pct_under_poverty", None)
    nat_poverty = national_value("pct_under_poverty", "national_all")

    if pd.notna(state_poverty):
        diff = state_poverty - nat_poverty
        if diff > 0:
            bullets.append(f"{abs(diff):.1f}% higher poverty rate than the national workforce")
        else:
            bullets.append(f"{abs(diff):.1f}% lower poverty rate than the national workforce")

    return shiny_ui.card(
        shiny_ui.card_header("Comparison to US Resident"),
        shiny_ui.tags.ul(*[shiny_ui.tags.li(b) for b in bullets]),
        class_="compact-card"
    )


# =========================
# DYNAMIC CARD LAYOUT
# =========================

@render.ui
def dashboard_cards():

    state = current_state()

    if state == "National":
        return shiny_ui.div(
            shiny_ui.div(
                average_cna_card(),
                style="width:350px;"
            ),
            shiny_ui.div(
                average_person_card(),
                style="width:350px;"
            ),
            style="""
                display:flex;
                justify-content:center;
                gap:2rem;
                margin-top:1rem;
            """
        )
        
        return shiny_ui.div(
            state_basics_card(state),
            observations_card(state),
            compare_to_cna_card(state),
            compare_to_person_card(state),
            class_="card-grid-4"
        )
