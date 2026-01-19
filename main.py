import plotly.express as px
import pandas as pd

from funnel_utility import FunnelUtility, BUSINESS_COLORS


def apply_business_layout(fig, legend_title="Segment"):
    """
    Einheitliches Styling:
    - helle Oberfläche (Business)
    - große, gut lesbare Legende
    - dezente Farben
    """
    fig.update_layout(
        template="plotly_white",
        colorway=BUSINESS_COLORS,
        font=dict(size=14),
        title=dict(font=dict(size=20)),
        legend=dict(
            title=legend_title,
            font=dict(size=13),
            bgcolor="rgba(255,255,255,0.85)",
            bordercolor="rgba(0,0,0,0.10)",
            borderwidth=1,
            orientation="v",
        ),
        margin=dict(l=70, r=40, t=80, b=70),
    )
    return fig


def save_and_open(fig, util: FunnelUtility, filename: str):
    """
    Speichert HTML und öffnet im Browser.
    """
    path = util.output_dir / filename
    fig.write_html(str(path), auto_open=True, include_plotlyjs="cdn")


def plot_funnel_overall(util: FunnelUtility, user_df: pd.DataFrame):
    counts = util.funnel_counts(user_df)
    conv = util.conversion_table(counts, col="Users")
    worst_label, worst_cr = util.worst_step(conv)

    # Funnel Counts
    fig1 = px.funnel(
        counts, y="Stage", x="Users",
        title="First-Ride Funnel (Overall) – Counts"
    )
    fig1.update_traces(texttemplate="%{x}", hovertemplate="<b>%{y}</b><br>Users: %{x}<extra></extra>")
    fig1 = apply_business_layout(fig1, legend_title="")
    save_and_open(fig1, util, "01_funnel_overall_counts.html")

    # Funnel % of previous
    pct = util.percent_of_previous(counts.rename(columns={"Users": "Overall"}), ["Overall"])
    fig2 = px.funnel(
        pct, y="Stage", x="Overall",
        title="First-Ride Funnel (Overall) – % of Previous Step"
    )
    fig2.update_traces(texttemplate="%{x:.1f}%", hovertemplate="<b>%{y}</b><br>Conversion: %{x:.2f}%<extra></extra>")
    fig2.update_xaxes(ticksuffix="%")
    fig2 = apply_business_layout(fig2, legend_title="")
    save_and_open(fig2, util, "02_funnel_overall_pct_previous.html")

    # Step Conversion Bar
    fig3 = px.bar(
        conv,
        x="From",
        y="Conversion (%)",
        title=f"Step Conversion (Overall) – Bottleneck: {worst_label} ({worst_cr:.2f}%)",
        labels={"From": "Step (From)", "Conversion (%)": "Conversion (%)"},
    )
    fig3.update_traces(hovertemplate="<b>%{x}</b><br>CR: %{y:.2f}%<extra></extra>")
    fig3 = apply_business_layout(fig3, legend_title="")
    save_and_open(fig3, util, "03_step_conversion_overall.html")


def plot_funnel_by_platform(util: FunnelUtility, user_df: pd.DataFrame):
    counts = util.funnel_counts_by_group(
        user_df, "platform_label", group_order=["iOS", "Android", "Web", "Unknown"]
    )
    value_cols = [c for c in counts.columns if c != "Stage"]

    # Counts by platform
    fig1 = px.funnel(
        counts, y="Stage", x=value_cols,
        title="First-Ride Funnel – Counts by Platform"
    )
    fig1.update_traces(texttemplate="%{x}", hovertemplate="<b>%{y}</b><br>Users: %{x}<extra></extra>")
    fig1 = apply_business_layout(fig1, legend_title="Platform")
    save_and_open(fig1, util, "04_funnel_platform_counts.html")

    # % of previous by platform
    pct = util.percent_of_previous(counts, value_cols)
    fig2 = px.funnel(
        pct, y="Stage", x=value_cols,
        title="First-Ride Funnel – % of Previous Step by Platform"
    )
    fig2.update_traces(texttemplate="%{x:.1f}%", hovertemplate="<b>%{y}</b><br>Conversion: %{x:.2f}%<extra></extra>")
    fig2.update_xaxes(ticksuffix="%")
    fig2 = apply_business_layout(fig2, legend_title="Platform")
    save_and_open(fig2, util, "05_funnel_platform_pct_previous.html")

    # Bottleneck je Plattform (kleine Zusatzanalyse als Tabelle + Plot)
    rows = []
    for p in value_cols:
        cdf = pd.DataFrame({"Stage": counts["Stage"], "Users": counts[p]})
        conv = util.conversion_table(cdf, col="Users")
        worst_label, worst_cr = util.worst_step(conv)
        rows.append({"Platform": p, "Worst step": worst_label, "Min CR (%)": worst_cr})

    bottleneck = pd.DataFrame(rows).sort_values("Min CR (%)")
    fig3 = px.bar(
        bottleneck,
        x="Platform",
        y="Min CR (%)",
        title="Bottleneck Strength by Platform (lower = worse)",
        hover_data=["Worst step"],
    )
    fig3 = apply_business_layout(fig3, legend_title="")
    save_and_open(fig3, util, "06_bottleneck_by_platform.html")


def plot_funnel_by_age(util: FunnelUtility, user_df: pd.DataFrame):
    # Optional feste Reihenfolge (wenn vorhanden)
    age_order = ["18-24", "25-34", "35-44", "45-54", "Unknown"]

    counts = util.funnel_counts_by_group(user_df, "age_range", group_order=age_order)
    value_cols = [c for c in counts.columns if c != "Stage"]

    fig1 = px.funnel(
        counts, y="Stage", x=value_cols,
        title="First-Ride Funnel – Counts by Age Group"
    )
    fig1.update_traces(texttemplate="%{x}", hovertemplate="<b>%{y}</b><br>Users: %{x}<extra></extra>")
    fig1 = apply_business_layout(fig1, legend_title="Age Group")
    save_and_open(fig1, util, "07_funnel_age_counts.html")

    pct = util.percent_of_previous(counts, value_cols)
    fig2 = px.funnel(
        pct, y="Stage", x=value_cols,
        title="First-Ride Funnel – % of Previous Step by Age Group"
    )
    fig2.update_traces(texttemplate="%{x:.1f}%", hovertemplate="<b>%{y}</b><br>Conversion: %{x:.2f}%<extra></extra>")
    fig2.update_xaxes(ticksuffix="%")
    fig2 = apply_business_layout(fig2, legend_title="Age Group")
    save_and_open(fig2, util, "08_funnel_age_pct_previous.html")


def plot_surge(util: FunnelUtility):
    by_hour = util.requests_per_hour()

    fig1 = px.line(
        by_hour,
        x="hour", y="requests",
        title="Ride Requests – Distribution over the Day (per Hour)",
        labels={"hour": "Hour of Day", "requests": "Ride Requests"},
    )
    fig1.update_xaxes(dtick=1)
    fig1 = apply_business_layout(fig1, legend_title="")
    save_and_open(fig1, util, "09_requests_per_hour.html")

    # Heatmap weekday x hour
    hm = util.requests_weekday_hour()
    pivot = hm.pivot(index="weekday", columns="hour", values="requests").fillna(0)

    fig2 = px.imshow(
        pivot,
        title="Ride Requests – Heatmap (Weekday × Hour)",
        labels=dict(x="Hour", y="Weekday", color="Requests"),
        aspect="auto",
    )
    fig2 = apply_business_layout(fig2, legend_title="")
    save_and_open(fig2, util, "10_requests_heatmap_weekday_hour.html")


def main():
    # Wenn eure CSVs in Resources/ liegen -> so lassen
    # Wenn sie im gleichen Ordner liegen -> data_dir="."
    util = FunnelUtility(data_dir="Resources", output_dir="output_html")

    # 1) User-Level Tabelle für den First-Ride-Funnel
    user_df = util.build_first_ride_user_df()

    # 2) Funnel plots + Analyse
    plot_funnel_overall(util, user_df)
    plot_funnel_by_platform(util, user_df)
    plot_funnel_by_age(util, user_df)

    # 3) Nachfrage / Surge-Analyse
    plot_surge(util)

    print("Fertig! HTML-Plots liegen in 'output_html/' und wurden im Browser geöffnet.")


if __name__ == "__main__":
    main()
