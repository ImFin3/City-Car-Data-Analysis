import pandas as pd
import plotly.express as px
from funnel_utility import Utility


util = Utility()

# Alle Plots werden in einem automatisch erstelltem Ordner "output_html" abgespeichert, dort können sie einzeln geöffnet werden ohne das Programm nochmal durchlaufen zu lassen
# Um den Browser nicht direkt vollzuspammen auto_open_all_plots auf False setzen
auto_open_all_plots = True

def main():
    print("Hello World!")
    overall_funnel_analysis_chart_with_counts()
    overall_funnel_analysis_chart_percent_of_the_previous()
    full_funnel_analysis_chart_with_counts()
    full_funnel_analysis_chart_percent_of_the_previous()
    full_funnel_analysis_chart_percent_of_the_top()
    comparison_accept_pickup_cancel_duration()
    cancellation_count_per_hour()
    request_count_per_hour()
    cancellation_rate_per_platform()
    average_review_rating_per_platform()
    cancellation_rate_per_age_group()
    average_review_rating_per_age_group()
    average_income_per_age_group()
    signups_per_age_group()
    daily_ride_counts()
    ride_requests_hm_weekday_hour()
    ride_request_per_day_of_year()
    time_per_day_of_year()
    pickup_location_density_map()

def overall_funnel_analysis_chart_with_counts():
    data = util.get_overall_funnel_analysis_dataframe()

    fig = px.funnel(data, x="Overall", y="Stage", title="Overall Funnel - Counts")
    fig.update_traces(
        texttemplate="%{x}",
        hovertemplate="<b>%{y}</b><br>"
                      "Count: %{x}"

    )
    fig = util.apply_constant_plot_layout(fig, )
    util.save_and_open(fig, "overall_funnel_analysis_chart_with_counts.html", auto_open_all_plots)

def overall_funnel_analysis_chart_percent_of_the_previous():
    percentage_data = util.get_overall_funnel_analysis_dataframe()

    percentage_data["Overall"] = percentage_data["Overall"].astype(float)

    shifted_data = percentage_data["Overall"].shift(1)
    for index in percentage_data.index:
        percentage_data.loc[index, "Overall"] = percentage_data["Overall"][index] / shifted_data[index] * 100
    percentage_data.loc[percentage_data.index[0], "Overall"] = 100

    fig = px.funnel(
        percentage_data,
        x="Overall",
        y="Stage",
        title="Overall Conversion Rate - Percent of the previous"
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        hovertemplate="<b>%{y}</b><br>"
                      "Conversion: %{x}"

    )
    fig.update_xaxes(ticksuffix="%")

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "overall_funnel_analysis_chart_percent_of_the_previous.html", auto_open_all_plots)

def full_funnel_analysis_chart_with_counts():
    data = util.get_full_funnel_analysis_dataframe()

    fig = px.funnel(data, x=["Overall", "IOS", "Android", "Web", "18-24", "25-34", "35-44", "45-54", "Unknown Age"], y="Stage", title="Unique User Funnel - Counts")
    fig.update_traces(
        texttemplate="%{x}",
        hovertemplate="<b>%{y}</b><br>"
                      "Count: %{x}"

    )
    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "full_funnel_analysis_chart_with_counts.html", auto_open_all_plots)

def full_funnel_analysis_chart_percent_of_the_previous():
    percentage_data = util.get_full_funnel_analysis_dataframe()

    value_columns = [
        "Overall", "IOS", "Android", "Web",
        "18-24", "25-34", "35-44", "45-54", "Unknown Age"
    ]

    percentage_data[value_columns] = percentage_data[value_columns].astype(float)

    for col in value_columns:
        shifted_data = percentage_data[col].shift(1)
        for index in percentage_data.index:
            percentage_data.loc[index, col] = percentage_data[col][index] / shifted_data[index] * 100
    percentage_data.loc[percentage_data.index[0], value_columns] = 100

    fig = px.funnel(
        percentage_data,
        x=value_columns,
        y="Stage",
        title="Unique User Conversion Rate - Percent of the previous"
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        hovertemplate="<b>%{y}</b><br>"
                      "Conversion: %{x}"

    )
    fig.update_xaxes(ticksuffix="%")

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "full_funnel_analysis_chart_percent_of_the_previous.html", auto_open_all_plots)

def full_funnel_analysis_chart_percent_of_the_top():
    percentage_data = util.get_full_funnel_analysis_dataframe()

    value_columns = [
        "Overall", "IOS", "Android", "Web",
        "18-24", "25-34", "35-44", "45-54", "Unknown Age"
    ]

    percentage_data[value_columns] = percentage_data[value_columns].astype(float)

    for col in value_columns:
        top_value = percentage_data[col][0]

        for index in percentage_data.index:
            if top_value == 0:
                percentage_data.loc[index, col] = 0
            else:
                percentage_data.loc[index, col] = (
                        percentage_data.loc[index, col] / top_value * 100
                )

    fig = px.funnel(
        percentage_data,
        x=value_columns,
        y="Stage",
        title="Unique User Conversion Rate - Percent of the top"
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        hovertemplate="<b>%{y}</b><br>"
                      "Conversion: %{x}"
    )
    fig.update_xaxes(ticksuffix="%")

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "full_funnel_analysis_chart_percent_of_the_top.html", auto_open_all_plots)

def comparison_accept_pickup_cancel_duration():
    data = util.get_accept_cancel_pickup_duration_dataframe()

    fig = px.box(data,
                 y=["time_till_accept_min", "time_till_pickup_min", "time_till_cancel_min"],
                 labels={
                     "variable": "Category",
                     "value": "Duration in minutes"
                 },
                 title="Comparison Accept, Pickup, Cancel Duration",
                 color="variable")

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "comparison_accept_pickup_cancel_duration.html", auto_open_all_plots)

def cancellation_count_per_hour():
    data = util.get_cancel_count_per_hour_dataframe()

    fig = px.line(data,
                  x="hour",
                  y="cancel_count",
                  title="Cancellation - Distribution over the Day (per Hour)",
                  labels={
                      "hour": "Hour",
                      "cancel_count": "Cancellations"
                  })
    fig.update_xaxes(
        dtick="H1",
        tickformat="%H"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "cancellation_count_per_hour.html", auto_open_all_plots)

def request_count_per_hour():
    data = util.get_request_count_per_hour_dataframe()

    fig = px.line(data,
                  x="hour",
                  y="request_count",
                  title="Ride Requests - Distribution over the Day (per Hour)",
                  labels={
                      "hour": "Hour",
                      "request_count": "Ride Requests"
                  })
    fig.update_xaxes(
        dtick="H1",
        tickformat="%H"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "request_count_per_hour.html", auto_open_all_plots)

def time_per_day_of_year():
    data = util.get_ride_requests_ts_split_dataframe()

    scatter_data_yearly_time_trend = pd.DataFrame({
        "Day of Year": data["Day of Year"],
        "Time": data["Time"],
        "Hour": data["Hour"]
    })
    scatter_data_yearly_time_trend = scatter_data_yearly_time_trend.sort_values("Time", ascending=True)
    fig = px.scatter(
        scatter_data_yearly_time_trend,
        x="Day of Year",
        y="Time",
        title="Ride Request Time per Day of Year"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "time_per_day_of_year.html", auto_open_all_plots)

def ride_request_per_day_of_year():
    data = util.get_ride_requests_ts_split_dataframe()

    day_of_year_trend = pd.DataFrame({
        "Day of Year": data["Day of Year"],
    })
    day_of_year_trend = day_of_year_trend.value_counts().reset_index()
    day_of_year_trend.columns = ["Day of Year", "Ride Request Count"]
    fig = px.bar(
        day_of_year_trend,
        x="Day of Year",
        y="Ride Request Count",
        title="Ride Request Count per Day of Year"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "ride_request_per_day_of_year.html", auto_open_all_plots)

def daily_ride_counts():
    data = util.get_daily_ride_count_dataframe()

    fig = px.bar(data,
                  x="day",
                  y="ride_count",
                  title="Daily Ride Request Count",
                  labels={"day": "Month", "ride_count": "Ride Count"})
    fig.update_xaxes(
        dtick="M1",
        tickformat="%Y-%m"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "daily_ride_counts.html", auto_open_all_plots)

def ride_requests_hm_weekday_hour():
    hm = util.get_ride_requests_count_per_weekday_and_hour_dataframe()
    pivot = hm.pivot(index="Weekday", columns="Hour", values="requests").fillna(0)

    fig = px.imshow(
        pivot,
        title="Ride Requests – Heatmap (Weekday × Hour)",
        labels=dict(x="Hour", y="Weekday", color="Requests"),
        aspect="auto",
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "ride_requests_hm_weekday_hour.html", auto_open_all_plots)

def pickup_location_density_map():
    data = util.get_all_pickup_locations_dataframe()

    fig = px.density_map(
        data,
        lat="lat",
        lon="lon",
        zoom=10,
        radius=8,
        title="Pickup Location Density Map"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "pickup_location_density_map.html", auto_open_all_plots)

def cancellation_rate_per_age_group():
    age_group_cancellations = util.get_cancellation_rate_per_age_group()
    fig = px.pie(
        names=age_group_cancellations.index,
        values=age_group_cancellations.values,
        title="Cancellation Rate per Age Group"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "cancellation_rate_per_age_group.html", auto_open_all_plots)

def cancellation_rate_per_platform():
    ios_rate, android_rate, web_rate = util.get_cancellation_rate_per_platform()
    fig = px.pie(
        names=["iOS", "Android", "Web"],
        values=[ios_rate, android_rate, web_rate],
        title="Cancellation Rate per Platform"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "cancellation_rate_per_platform.html", auto_open_all_plots)

def average_review_rating_per_age_group():
    age_group_ratings = util.get_average_review_rating_per_age_group()
    fig = px.bar(
        x=age_group_ratings.index,
        y=age_group_ratings.values,
        labels={'y': 'Average Rating', 'x': 'Age Group'},
        title="Average Review Rating per Age Group",
        text_auto=True,
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "average_review_rating_per_age_group.html", auto_open_all_plots)

def average_review_rating_per_platform():
    ios_rating, android_rating, web_rating = util.get_average_review_rating_per_platform()
    fig = px.bar(
        x=["iOS", "Android", "Web"],
        y=[ios_rating, android_rating, web_rating],
        labels={'y': 'Average Rating', 'x': 'Platform'},
        title="Average Review Rating per Platform",
        text_auto=True
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "average_review_rating_per_platform.html", auto_open_all_plots)

def average_income_per_age_group():
    age_18_24, age_25_34, age_35_44, age_45_54, age_unknown = util.get_average_income_per_age_group()
    fig = px.bar(
        x=["18-24", "25-34", "35-44", "45-54", "Unknown"],
        y=[age_18_24, age_25_34, age_35_44, age_45_54, age_unknown],
        labels={"x": "Age Group", "y": "Average Income (USD)"},
        title="Average Income per Age Group",
        text_auto=True
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "average_income_per_age_group.html", auto_open_all_plots)

def signups_per_age_group():
    count = util.get_signup_count_per_age_group()
    fig = px.pie(
        names=["Unknown", "18-24", "25-34", "35-44", "45-54"],
        values=[count.age_18_to_24, count.age_25_to_34, count.age_35_to_44, count.age_45_to_54, count.unknown],
        title="Signed Up User Count per Age Group"
    )

    fig = util.apply_constant_plot_layout(fig)
    util.save_and_open(fig, "signups_per_age_group.html", auto_open_all_plots)


if __name__ == "__main__":
    main()