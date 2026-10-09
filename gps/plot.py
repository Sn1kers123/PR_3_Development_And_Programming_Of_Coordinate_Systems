import plotly.graph_objects as go

from .config import AREA_SIZE_KM

SAT_COLORS = ["#5b2c9f", "#2ca02c", "#8c564b", "#17becf", "#7f7f7f"]
ANALYTIC_COLOR = "#e8590c"
NUMERIC_COLOR = "#1f77b4"


def _trail(fig, points, color, symbol):

    n = len(points)
    if n == 0:
        return
    fig.add_trace(go.Scatter(
        x=[p[0] for p in points], y=[p[1] for p in points], mode="markers",
        marker=dict(symbol=symbol, size=6, color=color,
                    opacity=[0.08 + 0.7 * i / n for i in range(n)]),
        showlegend=False, hoverinfo="skip",
    ))


def build_figure(sats, history, trail_len, show_trail):
    fig = go.Figure()

    # Супутники
    for i, s in enumerate(sats):
        fig.add_trace(go.Scatter(
            x=[s["x"]], y=[s["y"]], mode="markers+text", text=[str(i + 1)],
            textposition="top center", name=f"Супутник {s['id'][:6]}",
            marker=dict(symbol="triangle-up", size=11, color=SAT_COLORS[i % len(SAT_COLORS)]),
        ))

    last = history[-1] if history else {"analytic": None, "numeric": None}
    past = history[-trail_len - 1:-1] if show_trail else []

    for key, name, color, symbol, size in (
        ("analytic", "аналітичний метод", ANALYTIC_COLOR, "circle", 10),
        ("numeric", "чисельний метод (МНК)", NUMERIC_COLOR, "x", 11),
    ):
        _trail(fig, [h[key] for h in past if h[key]], color, symbol)
        p = last[key]
        fig.add_trace(go.Scatter(
            x=[p[0]] if p else [], y=[p[1]] if p else [], mode="markers", name=name,
            marker=dict(symbol=symbol, size=size, color=color, line=dict(width=2, color=color)),
        ))

    axis = dict(range=[0, AREA_SIZE_KM], showline=True, linecolor="#222",
                gridcolor="#eee", zeroline=False, constrain="domain")
    fig.update_layout(
        template="plotly_white", height=620, uirevision="keep",
        xaxis=dict(title="x, км", **axis),
        yaxis=dict(title="y, км", scaleanchor="x", scaleratio=1, **axis),
        legend=dict(orientation="h", x=0, y=-0.15),
        margin=dict(t=20, b=20),
    )
    return fig
