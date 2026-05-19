"""
dashboard.py
------------
Interactive Plotly Dash dashboard for Multi-Touch Marketing Attribution Analysis.
Run: python src/dashboard.py
Open: http://127.0.0.1:8050
"""

import os
import sys
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TP_FILE = os.path.join(DATA_DIR, "marketing_touchpoints.csv")
ATTR_FILE = os.path.join(DATA_DIR, "attribution_results.csv")

# ─── Load Data ────────────────────────────────────────────────────────────────
def load_data():
    tp_df = pd.read_csv(TP_FILE, parse_dates=["timestamp"])
    attr_df = pd.read_csv(ATTR_FILE)
    return tp_df, attr_df


# ─── Color Palette ────────────────────────────────────────────────────────────
CHANNEL_COLORS = {
    "Organic Search": "#2ECC71",
    "Paid Search":    "#3498DB",
    "Social Media":   "#9B59B6",
    "Email":          "#E67E22",
    "Display Ads":    "#E74C3C",
    "Referral":       "#1ABC9C",
    "Direct":         "#F39C12",
}
MODEL_COLORS = {
    "First-Touch":  "#E74C3C",
    "Last-Touch":   "#3498DB",
    "Linear":       "#2ECC71",
    "Time-Decay":   "#F39C12",
    "Markov Chain": "#9B59B6",
}

# ─── App Init ────────────────────────────────────────────────────────────────
app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.DARKLY],
    title="TEYZIX CORE | Attribution Analytics",
)

# ─── Layout ──────────────────────────────────────────────────────────────────
def create_layout(tp_df, attr_df):
    models = attr_df["model"].unique().tolist()
    channels = tp_df["channel"].unique().tolist()

    return dbc.Container(fluid=True, children=[

        # ── Header ──
        dbc.Row(dbc.Col(html.Div([
            html.H1("TEYZIX CORE", style={"color": "#2ECC71", "fontWeight": "bold",
                                           "marginBottom": "0"}),
            html.H4("Multi-Touch Marketing Attribution Analytics Dashboard",
                    style={"color": "#aaa", "marginTop": "4px"}),
            html.Hr(style={"borderColor": "#2ECC71"}),
        ]), width=12), className="mt-3 mb-2"),

        # ── KPI Cards ──
        dbc.Row(id="kpi-row", className="mb-3"),

        # ── Controls ──
        dbc.Row([
            dbc.Col([
                html.Label("Select Attribution Models", style={"color": "#ccc"}),
                dcc.Checklist(
                    id="model-selector",
                    options=[{"label": f"  {m}", "value": m} for m in models],
                    value=models,
                    inline=True,
                    inputStyle={"marginRight": "6px", "marginLeft": "12px"},
                    labelStyle={"color": "#ddd", "marginRight": "10px"},
                )
            ], width=8),
            dbc.Col([
                html.Label("Journey Length Filter", style={"color": "#ccc"}),
                dcc.RangeSlider(
                    id="journey-slider",
                    min=1, max=6, step=1,
                    value=[1, 6],
                    marks={i: str(i) for i in range(1, 7)},
                )
            ], width=4),
        ], className="mb-4 p-3",
           style={"background": "#1a1a2e", "borderRadius": "8px"}),

        # ── Row 1: Attribution Comparison + Channel Breakdown ──
        dbc.Row([
            dbc.Col(dcc.Graph(id="attribution-comparison"), width=7),
            dbc.Col(dcc.Graph(id="channel-pie"), width=5),
        ], className="mb-3"),

        # ── Row 2: Time Series + Journey Length Distribution ──
        dbc.Row([
            dbc.Col(dcc.Graph(id="time-series"), width=8),
            dbc.Col(dcc.Graph(id="journey-dist"), width=4),
        ], className="mb-3"),

        # ── Row 3: Heatmap + Model Comparison Radar ──
        dbc.Row([
            dbc.Col(dcc.Graph(id="model-heatmap"), width=6),
            dbc.Col(dcc.Graph(id="radar-chart"), width=6),
        ], className="mb-3"),

        # ── Row 4: Sankey + Data Table ──
        dbc.Row([
            dbc.Col(dcc.Graph(id="sankey"), width=7),
            dbc.Col([
                html.H5("Attribution Results Table",
                        style={"color": "#2ECC71", "marginBottom": "8px"}),
                html.Div(id="results-table"),
            ], width=5),
        ], className="mb-3"),

        # ── Footer ──
        dbc.Row(dbc.Col(html.P(
            "TEYZIX CORE Internship | Task DA-2 | Data: category_tree.csv (provided) + "
            "SYNTHETIC touchpoint data (clearly labeled)",
            style={"color": "#555", "fontSize": "12px", "textAlign": "center"}
        ), width=12), className="mt-2 mb-3"),

    ])


# ─── Callbacks ───────────────────────────────────────────────────────────────

def register_callbacks(app, tp_df, attr_df):

    @app.callback(
        Output("kpi-row", "children"),
        Input("model-selector", "value"),
        Input("journey-slider", "value"),
    )
    def update_kpis(selected_models, journey_range):
        filtered = tp_df[
            (tp_df["journey_length"] >= journey_range[0]) &
            (tp_df["journey_length"] <= journey_range[1])
        ]
        total_users = filtered["user_id"].nunique()
        conversions = filtered[filtered["converted"] == 1]["user_id"].nunique()
        conv_rate = conversions / total_users * 100 if total_users else 0
        avg_journey = filtered["journey_length"].mean()
        top_channel = (filtered[filtered["converted"] == 1]
                       .groupby("channel")["user_id"].nunique()
                       .idxmax() if conversions else "N/A")

        kpis = [
            ("Total Users", f"{total_users:,}", "#2ECC71"),
            ("Conversions", f"{conversions:,}", "#3498DB"),
            ("Conversion Rate", f"{conv_rate:.1f}%", "#E67E22"),
            ("Avg Journey Length", f"{avg_journey:.1f}", "#9B59B6"),
            ("Top Channel", top_channel, "#E74C3C"),
        ]
        cards = []
        for label, value, color in kpis:
            cards.append(dbc.Col(dbc.Card(dbc.CardBody([
                html.H5(value, style={"color": color, "fontWeight": "bold",
                                      "fontSize": "1.6rem", "marginBottom": "2px"}),
                html.P(label, style={"color": "#aaa", "fontSize": "0.8rem",
                                     "marginBottom": "0"}),
            ]), style={"background": "#1a1a2e", "border": f"1px solid {color}",
                       "borderRadius": "8px"}), width=True))
        return cards

    @app.callback(
        Output("attribution-comparison", "figure"),
        Input("model-selector", "value"),
        Input("journey-slider", "value"),
    )
    def update_comparison(selected_models, journey_range):
        filtered_attr = attr_df[attr_df["model"].isin(selected_models)]
        fig = px.bar(
            filtered_attr,
            x="channel", y="credit", color="model",
            barmode="group",
            color_discrete_map=MODEL_COLORS,
            title="Attribution Credit by Channel & Model",
            labels={"credit": "Attribution Credit", "channel": "Channel"},
        )
        fig.update_layout(
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font_color="#ccc", legend_title="Model",
            title_font_color="#2ECC71",
        )
        fig.update_yaxes(tickformat=".0%", gridcolor="#222")
        fig.update_xaxes(gridcolor="#222")
        return fig

    @app.callback(
        Output("channel-pie", "figure"),
        Input("model-selector", "value"),
        Input("journey-slider", "value"),
    )
    def update_pie(selected_models, journey_range):
        if not selected_models:
            return go.Figure()
        # Use Linear as default for pie; if not selected use first
        model_to_use = "Linear" if "Linear" in selected_models else selected_models[0]
        data = attr_df[attr_df["model"] == model_to_use]
        fig = px.pie(
            data, values="credit", names="channel",
            title=f"Channel Share ({model_to_use})",
            color="channel", color_discrete_map=CHANNEL_COLORS,
            hole=0.4,
        )
        fig.update_layout(
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font_color="#ccc", title_font_color="#2ECC71",
        )
        return fig

    @app.callback(
        Output("time-series", "figure"),
        Input("journey-slider", "value"),
    )
    def update_time_series(journey_range):
        filtered = tp_df[
            (tp_df["journey_length"] >= journey_range[0]) &
            (tp_df["journey_length"] <= journey_range[1])
        ].copy()
        filtered["month"] = filtered["timestamp"].dt.to_period("M").astype(str)
        monthly = (filtered[filtered["converted"] == 1]
                   .groupby(["month", "channel"])["user_id"]
                   .nunique().reset_index())
        monthly.columns = ["month", "channel", "conversions"]
        fig = px.line(
            monthly, x="month", y="conversions", color="channel",
            color_discrete_map=CHANNEL_COLORS,
            title="Monthly Conversions by Channel",
            markers=True,
        )
        fig.update_layout(
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font_color="#ccc", title_font_color="#2ECC71",
        )
        fig.update_xaxes(gridcolor="#222")
        fig.update_yaxes(gridcolor="#222")
        return fig

    @app.callback(
        Output("journey-dist", "figure"),
        Input("journey-slider", "value"),
    )
    def update_journey_dist(journey_range):
        filtered = tp_df[
            (tp_df["journey_length"] >= journey_range[0]) &
            (tp_df["journey_length"] <= journey_range[1])
        ]
        dist = filtered.drop_duplicates("user_id")["journey_length"].value_counts().sort_index()
        fig = go.Figure(go.Bar(
            x=dist.index, y=dist.values,
            marker_color="#2ECC71",
        ))
        fig.update_layout(
            title="Journey Length Distribution",
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font_color="#ccc", title_font_color="#2ECC71",
            xaxis_title="Touchpoints", yaxis_title="Users",
        )
        fig.update_xaxes(gridcolor="#222")
        fig.update_yaxes(gridcolor="#222")
        return fig

    @app.callback(
        Output("model-heatmap", "figure"),
        Input("model-selector", "value"),
    )
    def update_heatmap(selected_models):
        pivot = attr_df[attr_df["model"].isin(selected_models)].pivot_table(
            index="channel", columns="model", values="credit", fill_value=0
        )
        fig = go.Figure(go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="Viridis",
            text=np.round(pivot.values * 100, 1),
            texttemplate="%{text}%",
            showscale=True,
        ))
        fig.update_layout(
            title="Attribution Heatmap: Channel × Model",
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font_color="#ccc", title_font_color="#2ECC71",
        )
        return fig

    @app.callback(
        Output("radar-chart", "figure"),
        Input("model-selector", "value"),
    )
    def update_radar(selected_models):
        channels_list = attr_df["channel"].unique().tolist()
        fig = go.Figure()
        for model in selected_models:
            model_data = attr_df[attr_df["model"] == model].set_index("channel")
            values = [model_data.loc[c, "credit"] if c in model_data.index else 0
                      for c in channels_list]
            values.append(values[0])  # close the loop
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=channels_list + [channels_list[0]],
                fill="toself",
                name=model,
                line_color=MODEL_COLORS.get(model, "#fff"),
                opacity=0.7,
            ))
        fig.update_layout(
            title="Model Comparison Radar Chart",
            polar=dict(
                bgcolor="#1a1a2e",
                radialaxis=dict(visible=True, range=[0, 0.3],
                                gridcolor="#333", color="#aaa"),
                angularaxis=dict(color="#aaa"),
            ),
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font_color="#ccc", title_font_color="#2ECC71",
            legend=dict(bgcolor="#1a1a2e"),
        )
        return fig

    @app.callback(
        Output("sankey", "figure"),
        Input("journey-slider", "value"),
    )
    def update_sankey(journey_range):
        filtered = tp_df[
            (tp_df["journey_length"] >= journey_range[0]) &
            (tp_df["journey_length"] <= journey_range[1]) &
            (tp_df["touchpoint_order"] <= 3)
        ]
        channels = filtered["channel"].unique().tolist()
        channel_idx = {c: i for i, c in enumerate(channels)}

        sources, targets, values = [], [], []
        for (src, tgt), cnt in (
            filtered.groupby(["channel", "channel"])  # placeholder loop
            .size().reset_index().rename(columns={0: "count"})
            .set_index(["channel", "channel"])["count"].items()
        ):
            pass

        # Build actual transitions
        transitions = {}
        for uid, journey in filtered.groupby("user_id"):
            journey = journey.sort_values("touchpoint_order")
            chs = journey["channel"].tolist()
            for i in range(len(chs) - 1):
                key = (chs[i], chs[i + 1])
                transitions[key] = transitions.get(key, 0) + 1

        node_labels = channels
        for (src, tgt), cnt in transitions.items():
            if src in channel_idx and tgt in channel_idx:
                sources.append(channel_idx[src])
                targets.append(channel_idx[tgt])
                values.append(cnt)

        node_colors = [CHANNEL_COLORS.get(c, "#aaa") for c in node_labels]

        fig = go.Figure(go.Sankey(
            node=dict(label=node_labels, color=node_colors, pad=15, thickness=20),
            link=dict(source=sources, target=targets, value=values,
                      color="rgba(100,100,200,0.3)"),
        ))
        fig.update_layout(
            title="Channel Transition Flow (Sankey)",
            plot_bgcolor="#0d1117", paper_bgcolor="#0d1117",
            font_color="#ccc", title_font_color="#2ECC71",
        )
        return fig

    @app.callback(
        Output("results-table", "children"),
        Input("model-selector", "value"),
    )
    def update_table(selected_models):
        data = attr_df[attr_df["model"].isin(selected_models)].copy()
        data["credit"] = (data["credit"] * 100).round(2).astype(str) + "%"
        return dash_table.DataTable(
            data=data[["model", "channel", "credit"]].to_dict("records"),
            columns=[{"name": c.title(), "id": c}
                     for c in ["model", "channel", "credit"]],
            style_table={"overflowY": "auto", "maxHeight": "380px"},
            style_header={"backgroundColor": "#1a1a2e", "color": "#2ECC71",
                           "fontWeight": "bold"},
            style_cell={"backgroundColor": "#0d1117", "color": "#ccc",
                        "border": "1px solid #222", "fontSize": "12px"},
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": "#111827"}
            ],
            page_size=20,
            sort_action="native",
            filter_action="native",
        )


# ─── Main ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[Dashboard] Loading data...")
    tp_df, attr_df = load_data()
    print(f"  → Touchpoints: {len(tp_df)} | Attribution results: {len(attr_df)}")
    app.layout = create_layout(tp_df, attr_df)
    register_callbacks(app, tp_df, attr_df)
    print("[Dashboard] Starting server at http://127.0.0.1:8050")
    app.run(debug=False, host="127.0.0.1", port=8050)
