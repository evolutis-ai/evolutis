"""
Evolutis Live Dashboard

Public-facing Streamlit dashboard showing live paper trading performance.
Reads data from data/live/ directory (synced from private trading system).

Usage:
    streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
from pathlib import Path
from datetime import timedelta

# Page config
st.set_page_config(
    page_title="Evolutis - Live Trading",
    page_icon="chart_with_upwards_trend",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data" / "live"

# Dark theme colors
COLORS = {
    "bg": "#0D1117",
    "card": "#161B22",
    "border": "#21262D",
    "text": "#C9D1D9",
    "accent": "#58A6FF",
    "green": "#3FB950",
    "red": "#F85149",
    "gold": "#FFD54F",
    "cyan": "#06B6D4",
}

# Custom CSS for dark theme
st.markdown("""
<style>
    .stApp {
        background-color: #0D1117;
    }
    .stMetric {
        background-color: #161B22;
        border: 1px solid #21262D;
        border-radius: 8px;
        padding: 12px;
    }
    .stMetric label {
        color: #8B949E !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #C9D1D9 !important;
    }
    h1, h2, h3 {
        color: #C9D1D9 !important;
    }
    .disclaimer {
        background-color: #161B22;
        border: 1px solid #21262D;
        border-radius: 8px;
        padding: 16px;
        color: #8B949E;
        font-size: 0.85em;
        text-align: center;
        margin-top: 2em;
    }
</style>
""", unsafe_allow_html=True)


def load_data():
    """Load paper trading data from data/live/ directory."""
    data = {}

    portfolio_file = DATA_DIR / "portfolio_history.csv"
    if portfolio_file.exists():
        try:
            df = pd.read_csv(portfolio_file)
            if len(df) > 0 and "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            data["portfolio"] = df
        except Exception:
            data["portfolio"] = pd.DataFrame()
    else:
        data["portfolio"] = pd.DataFrame()

    trades_file = DATA_DIR / "trades.csv"
    if trades_file.exists():
        try:
            df = pd.read_csv(trades_file)
            if len(df) > 0 and "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
            data["trades"] = df
        except Exception:
            data["trades"] = pd.DataFrame()
    else:
        data["trades"] = pd.DataFrame()

    summary_file = DATA_DIR / "summary.json"
    if summary_file.exists():
        try:
            with open(summary_file) as f:
                data["summary"] = json.load(f)
        except Exception:
            data["summary"] = None
    else:
        data["summary"] = None

    return data


def render_header(data):
    """Render dashboard header with key metrics."""
    st.markdown("# Evolutis - Live Paper Trading")

    summary = data.get("summary")
    portfolio = data.get("portfolio", pd.DataFrame())

    if len(portfolio) == 0 and not summary:
        st.info("No live trading data available yet. Check back soon.")
        return False

    # Get latest values
    if len(portfolio) > 0:
        latest = portfolio.iloc[-1]
        portfolio_value = latest.get("portfolio_value", 0)
        buyhold_value = latest.get("buyhold_value", 0)
        total_trades = int(latest.get("total_trades", 0))
        winning_trades = int(latest.get("winning_trades", 0))
        losing_trades = int(latest.get("losing_trades", 0))
    elif summary:
        portfolio_value = summary.get("final_portfolio_value", 0)
        buyhold_value = summary.get("final_buyhold_value", 0)
        total_trades = summary.get("total_trades", 0)
        winning_trades = summary.get("winning_trades", 0)
        losing_trades = summary.get("losing_trades", 0)
    else:
        return False

    initial_capital = summary.get("initial_capital", 10000) if summary else 10000
    total_return = ((portfolio_value / initial_capital) - 1) * 100 if initial_capital > 0 else 0
    buyhold_return = ((buyhold_value / initial_capital) - 1) * 100 if initial_capital > 0 else 0
    alpha = total_return - buyhold_return
    win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0

    # Session info
    if summary:
        start = summary.get("start_time", "")
        duration = summary.get("duration_seconds", 0)
        steps = summary.get("total_steps", 0)
        st.caption(f"Session started: {start[:19] if start else 'N/A'}  |  Steps: {steps}  |  Duration: {timedelta(seconds=int(duration))}")

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Portfolio Value", f"${portfolio_value:,.2f}", f"{total_return:+.2f}%")
    with col2:
        st.metric("Buy & Hold", f"${buyhold_value:,.2f}", f"{buyhold_return:+.2f}%")
    with col3:
        st.metric("Alpha", f"{alpha:+.2f}%", "vs Buy & Hold")
    with col4:
        st.metric("Win Rate", f"{win_rate:.1f}%", f"{winning_trades}W / {losing_trades}L")
    with col5:
        st.metric("Total Trades", f"{total_trades}", f"{len(data.get('trades', []))} logged")

    return True


def render_portfolio_chart(data):
    """Render portfolio performance chart."""
    portfolio = data.get("portfolio", pd.DataFrame())
    if len(portfolio) == 0:
        return

    st.markdown("### Portfolio Performance")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=portfolio["timestamp"],
        y=portfolio["portfolio_value"],
        name="Evolutis Agent",
        line=dict(color=COLORS["cyan"], width=2),
        fill="tozeroy",
        fillcolor="rgba(6, 182, 212, 0.08)"
    ))

    if "buyhold_value" in portfolio.columns:
        fig.add_trace(go.Scatter(
            x=portfolio["timestamp"],
            y=portfolio["buyhold_value"],
            name="Buy & Hold",
            line=dict(color=COLORS["gold"], width=2, dash="dash")
        ))

    summary = data.get("summary")
    initial = summary.get("initial_capital", 10000) if summary else 10000
    fig.add_hline(y=initial, line_dash="dot", line_color="#8B949E",
                  annotation_text=f"Initial (${initial:,.0f})")

    fig.update_layout(
        plot_bgcolor=COLORS["bg"],
        paper_bgcolor=COLORS["bg"],
        font_color=COLORS["text"],
        xaxis_title="Time",
        yaxis_title="Value (USDT)",
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=450,
        margin=dict(l=60, r=20, t=40, b=60),
        xaxis=dict(gridcolor=COLORS["border"]),
        yaxis=dict(gridcolor=COLORS["border"]),
    )

    st.plotly_chart(fig, use_container_width=True)


def render_returns_chart(data):
    """Render returns and outperformance charts."""
    portfolio = data.get("portfolio", pd.DataFrame())
    summary = data.get("summary")
    if len(portfolio) == 0:
        return

    initial = summary.get("initial_capital", 10000) if summary else 10000
    df = portfolio.copy()
    df["return_pct"] = ((df["portfolio_value"] / initial) - 1) * 100
    df["bh_return_pct"] = ((df["buyhold_value"] / initial) - 1) * 100 if "buyhold_value" in df.columns else 0
    df["alpha_pct"] = df["return_pct"] - df["bh_return_pct"]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Returns (%)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["return_pct"],
                                 name="Agent", line=dict(color=COLORS["green"], width=2)))
        fig.add_trace(go.Scatter(x=df["timestamp"], y=df["bh_return_pct"],
                                 name="Buy & Hold", line=dict(color=COLORS["gold"], width=2, dash="dash")))
        fig.add_hline(y=0, line_dash="dot", line_color="#8B949E")
        fig.update_layout(
            plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"], font_color=COLORS["text"],
            height=300, margin=dict(l=40, r=20, t=10, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            xaxis=dict(gridcolor=COLORS["border"]), yaxis=dict(gridcolor=COLORS["border"]),
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("### Alpha vs Buy & Hold (%)")
        fig = go.Figure()
        colors = [COLORS["green"] if x >= 0 else COLORS["red"] for x in df["alpha_pct"]]
        fig.add_trace(go.Bar(x=df["timestamp"], y=df["alpha_pct"], marker_color=colors))
        fig.add_hline(y=0, line_dash="dot", line_color="#8B949E")
        fig.update_layout(
            plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"], font_color=COLORS["text"],
            height=300, margin=dict(l=40, r=20, t=10, b=40),
            xaxis=dict(gridcolor=COLORS["border"]), yaxis=dict(gridcolor=COLORS["border"]),
        )
        st.plotly_chart(fig, use_container_width=True)


def render_trades(data):
    """Render recent trades and distribution."""
    trades = data.get("trades", pd.DataFrame())
    if len(trades) == 0:
        return

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### Recent Trades")
        recent = trades.tail(20).sort_values("timestamp", ascending=False)
        display_cols = ["timestamp", "symbol", "side", "quantity", "price", "value_usd", "fee"]
        available = [c for c in display_cols if c in recent.columns]
        st.dataframe(recent[available], use_container_width=True, height=400)

    with col2:
        st.markdown("### Trade Distribution")

        if "symbol" in trades.columns:
            counts = trades["symbol"].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=counts.index, values=counts.values,
                hole=0.4, textinfo="label+percent",
                marker=dict(colors=["#2196F3", "#FF5722", "#4CAF50", "#9C27B0",
                                     "#FF9800", "#00BCD4", "#E91E63", "#795548", "#607D8B"])
            )])
            fig.update_layout(
                plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"], font_color=COLORS["text"],
                height=200, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)

        if "side" in trades.columns:
            sides = trades["side"].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=sides.index, values=sides.values,
                hole=0.4, textinfo="label+percent",
                marker=dict(colors=[COLORS["green"], COLORS["red"]])
            )])
            fig.update_layout(
                plot_bgcolor=COLORS["bg"], paper_bgcolor=COLORS["bg"], font_color=COLORS["text"],
                height=200, margin=dict(l=0, r=0, t=0, b=0), showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True)


def main():
    data = load_data()

    has_data = render_header(data)
    if not has_data:
        return

    st.markdown("---")
    render_portfolio_chart(data)
    render_returns_chart(data)
    st.markdown("---")
    render_trades(data)

    # Footer
    st.markdown(
        '<div class="disclaimer">'
        'This dashboard shows simulated paper trading results. '
        'Past performance does not guarantee future results. '
        'Not financial advice. For research and educational purposes only.'
        '</div>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()