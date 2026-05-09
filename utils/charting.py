import plotly.express as px
import plotly.graph_objects as go


# ---------------------------------------------------
# Color theme
# ---------------------------------------------------
COLOR_MAP = {
    "FAILED": "#E74C3C",      # Red
    "SUCCEEDED": "#2ECC71",   # Green
    "ERROR": "#F39C12",       # Orange
    "CANCELLED": "#95A5A6",   # Grey
    "TIMED_OUT": "#9B59B6"    # Purple
}


# ---------------------------------------------------
# Smart Visualization Engine
# ---------------------------------------------------
def auto_chart(df):

    if df is None or df.empty:
        return None

    cols = list(df.columns)

    # ------------------------------------------------
    # 1️⃣ KPI CARD (Single value)
    # ------------------------------------------------
    if df.shape == (1, 1):
        value = df.iloc[0, 0]

        fig = go.Figure(
            go.Indicator(
                mode="number",
                value=value,
                title={"text": cols[0]},
                number={"font": {"size": 50}}
            )
        )
        fig.update_layout(height=250)
        return fig

    # ------------------------------------------------
    # 2️⃣ Bar Chart (Category + Numeric)
    # ------------------------------------------------
    if len(cols) >= 2:

        x, y = cols[0], cols[1]

        if str(df[y].dtype).startswith(("int", "float")):

            colors = None

            if x in df.columns:
                colors = [
                    COLOR_MAP.get(str(v), "#3498DB")
                    for v in df[x]
                ]

            fig = px.bar(
                df,
                x=x,
                y=y,
                title=f"{y} by {x}"
            )

            if colors:
                fig.update_traces(marker_color=colors)

            return fig

    # ------------------------------------------------
    # 3️⃣ Line Chart (Time Series)
    # ------------------------------------------------
    for col in df.columns:
        if "time" in col.lower() or "date" in col.lower():
            other_cols = [c for c in df.columns if c != col]

            if other_cols:
                y = other_cols[0]

                fig = px.line(
                    df,
                    x=col,
                    y=y,
                    title=f"{y} over time"
                )
                return fig

    # ------------------------------------------------
    # 4️⃣ Pie Chart (Distribution)
    # ------------------------------------------------
    if len(cols) == 2:
        x, y = cols[0], cols[1]

        if str(df[y].dtype).startswith(("int", "float")):
            fig = px.pie(
                df,
                names=x,
                values=y,
                title=f"Distribution of {x}"
            )
            return fig

    return None
