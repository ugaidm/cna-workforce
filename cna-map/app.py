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

demo_cna = demo_cna.copy()
demo_hoh = demo_hoh.copy()

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

ui.page_opts(title="CNA Demographic Explorer", fillable=False)

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

    ui.input_select(
        "selected_metric",
        "Shade map by",
        choices={
            "avg_age": "Average age",
            "pct_white": "Percent White",
            "pct_hs_grad_diploma_or_cred": "Percent HS diploma",
            "avg_wages": "Average wages",
            "pct_married": "Percent married",
            "pct_under_poverty": "Percent under poverty"
        },
        selected="avg_age"
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

    metric = input.selected_metric()
    df = current_demo().copy()
    state = current_state()

    metric_info = metric_settings[metric]
    metric_label = metric_info["label"]

    # Separate states with and without data for the chosen metric
    df_with_data = df[df[metric].notna()].copy()
    df_missing = df[df[metric].isna()].copy()

    fig = px.choropleth(
        df_with_data,
        locations="state_abbr",
        locationmode="USA-states",
        color=metric,
        hover_name="state_name",
        custom_data=["state_name", metric],
        scope="usa",
        color_continuous_scale=[
            [0.0, "#f4f8fe"],
            [0.5, "#76a4e1"],
            [1.0, "#042554"]
        ],
        labels={metric: metric_label},
        basemap_visible=False
    )

    # Format hover text for states with data
    if metric == "avg_wages":
        hover_template = (
            "<b>%{customdata[0]}</b><br>"
            + metric_label
            + ": $%{customdata[1]:,.0f}"
            + "<extra></extra>"
        )
    elif metric.startswith("pct_"):
        hover_template = (
            "<b>%{customdata[0]}</b><br>"
            + metric_label
            + ": %{customdata[1]:.1f}%"
            + "<extra></extra>"
        )
    else:
        hover_template = (
            "<b>%{customdata[0]}</b><br>"
            + metric_label
            + ": %{customdata[1]:.1f}"
            + "<extra></extra>"
        )

    fig.update_traces(
        hovertemplate=hover_template
    )

    # Add missing states as a gray layer
    if not df_missing.empty:
        fig.add_trace(
            go.Choropleth(
                locations=df_missing["state_abbr"],
                locationmode="USA-states",
                z=[1] * len(df_missing),
                text=df_missing["state_name"],
                customdata=df_missing[["state_name"]].to_numpy(),
                colorscale=[
                    [0, "#d9d9d9"],
                    [1, "#d9d9d9"]
                ],
                showscale=False,
                marker_line_color="white",
                marker_line_width=0.5,
                hovertemplate=(
                    "<b>%{customdata[0]}</b><br>"
                    + metric_label
                    + ": Data not available"
                    + "<extra></extra>"
                ),
                name="Data not available"
            )
        )

    # Highlight the selected state without changing the map's viewport.
    if state != "National" and state in df["state_name"].values:

        selected_abbr = df.loc[
            df["state_name"] == state,
            "state_abbr"
        ].iloc[0]

        for trace in fig.data:
            trace_locations = list(trace.locations)

            if selected_abbr in trace_locations:
                selected_index = trace_locations.index(selected_abbr)
                trace.selectedpoints = [selected_index]
                trace.selected = dict(marker=dict(opacity=1))
                trace.unselected = dict(marker=dict(opacity=0.35))

    fig.update_layout(
        autosize=True,
        height=500,
        margin=dict(l=0, r=40, t=0, b=0),
        coloraxis_colorbar=dict(
            title=metric_info["colorbar"],
            thickness=12,
            len=0.72,
            x=1.0
        ),
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            visible=False
        ),
        clickmode="event+select"
    )

    fig.update_geos(
        scope="usa",
        projection_type="albers usa",
        visible=False,
        showlakes=False,
        showframe=False,
        showcountries=False,
        showcoastlines=False
    )

    fig_widget = go.FigureWidget(fig)
    fig_widget._config = {"responsive": True, "displayModeBar": True}

    # Attach click handling to every trace
    for trace in fig_widget.data:

        def handle_click(trace, points, selector):
            if points.point_inds:
                idx = points.point_inds[0]
                state_abbreviation = trace.locations[idx]

                matching_state = df.loc[
                    df["state_abbr"] == state_abbreviation,
                    "state_name"
                ]

                if not matching_state.empty:
                    clicked_state.set(matching_state.iloc[0])

        trace.on_click(handle_click)

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
        "National Main Demos",
        [
            (f"{label} age", f"{national_value('avg_age', cna_col):.1f}"),
            ("Average person age", f"{national_value('avg_age', 'national_all'):.1f}"),
            (f"{label} wages", f"${national_value('avg_wages', cna_col):,.0f}"),
            ("Person wages", f"${national_value('avg_wages', 'national_all'):,.0f}"),
        ]
    )


def average_cna_card():
    cna_col = selected_national_cna_column()
    label = selected_group_label()

    return stat_card(
        label,
        [
            ("Average age", f"{national_value('avg_age', cna_col):.1f}"),
            ("Average wages", f"${national_value('avg_wages', cna_col):,.0f}"),
            ("Under poverty", f"{national_value('pct_under_poverty', cna_col):.1f}%"),
        ]
    )


def average_person_card():
    return stat_card(
        "Average Person",
        [
            ("Average age", f"{national_value('avg_age', 'national_all'):.1f}"),
            ("Average wages", f"${national_value('avg_wages', 'national_all'):,.0f}"),
            ("Under poverty", f"{national_value('pct_under_poverty', 'national_all'):.1f}%"),
        ]
    )


def state_basics_card(state):
    df = current_demo()
    row = df[df["state_name"] == state].iloc[0]

    return stat_card(
        f"State Basics: {state}",
        [
            ("Average age", f"{row.get('avg_age', 0):.1f}"),
            ("Percent female", f"{row.get('pct_female', 0):.1f}%"),
            ("Average wages", f"${row.get('avg_wages', 0):,.0f}"),
            (
                "Under poverty",
                "Data not available"
                if pd.isna(row.get("pct_under_poverty"))
                else f"{row.get('pct_under_poverty'):.1f}%"
            ),
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
        shiny_ui.card_header("Comparison to Natl. Avg"),
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
            national_main_demos_card(),
            average_cna_card(),
            average_person_card(),
            class_="card-grid-3"
        )

    return shiny_ui.div(
        state_basics_card(state),
        observations_card(state),
        compare_to_cna_card(state),
        compare_to_person_card(state),
        class_="card-grid-4"
    )

metric_settings = {
    "avg_age": {
        "label": "Average age",
        "hover": ".1f",
        "colorbar": "Age"
    },
    "pct_white": {
        "label": "Percent White",
        "hover": ".1f",
        "colorbar": "Percent"
    },
    "pct_hs_grad_diploma_or_cred": {
        "label": "Percent HS diploma",
        "hover": ".1f",
        "colorbar": "Percent"
    },
    "avg_wages": {
        "label": "Average wages",
        "hover": "$,.0f",
        "colorbar": "Wages"
    },
    "pct_married": {
        "label": "Percent married",
        "hover": ".1f",
        "colorbar": "Percent"
    },
    "pct_under_poverty": {
        "label": "Percent under poverty",
        "hover": ".1f",
        "colorbar": "Percent"
    }
}
