import pandas as pd

from funnel_utility import Utility
import plotly.express as px

util = Utility()


def main():
    #full_funnel_analysis_chart_with_counts()
    #full_funnel_analysis_chart_percent_of_the_previous()
    #full_funnel_analysis_chart_percent_of_the_top()
    #comparison_accept_pickup_cancel_duration()
    #cancellation_count_per_hour()
    #request_count_per_hour()
    #daily_ride_counts()
    ride_requests_hm_weekday_hour()
    #ride_request_per_day_of_year()
    #time_per_day_of_year()
    #pickup_location_density_map()
    #question_one_testing_area()
    #question_two_testing_area()
    #question_three_testing_area()
    #question_four_testing_area()



def question_one_testing_area():

    data = util.get_detailed_overall_funnel_analysis_dataframe()
    print(data)

    fig = px.bar(data, "Conversion From To", ["Before", "After", "Conversion Rate"], barmode="group")
    fig.show()

    download_to_signup, signup_to_ride_request, ride_request_to_transaction, transaction_to_approved_transaction = util.get_detailed_overall_funnel_analysis()

    print(f"Es gab {download_to_signup.before} Downloads und {download_to_signup.after} Sign Ups! "
          f"Das ist eine Conversion Rate von {download_to_signup.conversion_rate}!")
    print(f"Es gab {signup_to_ride_request.before} Sign Ups und {signup_to_ride_request.after} unique Ride Requests! "
          f"Das ist eine Conversion Rate von {signup_to_ride_request.conversion_rate}!")
    print(f"Es gab {ride_request_to_transaction.before} Ride Requests und {ride_request_to_transaction.after} Transactions! "
          f"Das ist eine Conversion Rate von {ride_request_to_transaction.conversion_rate}!")
    print(f"Es gab {transaction_to_approved_transaction.before} Transactions und {transaction_to_approved_transaction.after} Approved Transactions! "
          f"Das ist eine Conversion Rate von {transaction_to_approved_transaction.conversion_rate}!")
    print()

def question_two_testing_area():

    data = util.get_platform_analysis_dataframe()
    print(data)

    fig = px.bar(data, "Platform", ["Download Count", "Signed Up User Count", "Download to Sign Up Conversion Rate", "Average Money spent per Ride in $"], barmode="group")
    fig.show()

    download_count_per_platform = util.get_download_count_per_platform()
    signup_count_per_platform = util.get_signup_count_per_platform()

    print(f"Von {download_count_per_platform.ios} iOS downloads, haben sich {signup_count_per_platform.ios} Signed Up! "
          f"Das ist eine Conversion Rate von {util.get_conversion_rate(download_count_per_platform.ios, signup_count_per_platform.ios)}!")
    print(f"Von {download_count_per_platform.android} Android downloads, haben sich {signup_count_per_platform.android} Signed Up! "
          f"Das ist eine Conversion Rate von {util.get_conversion_rate(download_count_per_platform.android, signup_count_per_platform.android)}!")
    print(f"Von {download_count_per_platform.web} Web downloads, haben sich {signup_count_per_platform.web} Signed Up! "
          f"Das ist eine Conversion Rate von {util.get_conversion_rate(download_count_per_platform.web, signup_count_per_platform.web)}!")

    print()

def question_three_testing_area():

    data = util.get_age_group_analysis_dataframe()
    print(data)

    fig = px.bar(data, "Age Group", ["Sign Up Count", "Approved Ride Request Count", "Approved Rides per Signed Up User"], barmode="group")
    fig.show()

    print()

def question_four_testing_area():

    data = util.get_surge_pricing_analysis_dataframe()

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
    )
    fig.show()


    scatter_data_day_of_year_trend = pd.DataFrame({
        "Day of Year": data["Day of Year"],
    })
    scatter_data_day_of_year_trend = scatter_data_day_of_year_trend.value_counts().reset_index()
    scatter_data_day_of_year_trend.columns = ["Day of Year", "Ride Request Count"]
    fig1 = px.bar(
        scatter_data_day_of_year_trend,
        x="Day of Year",
        y="Ride Request Count"
    )
    fig1.show()


    weekday_order = [
        "Monday", "Tuesday", "Wednesday",
        "Thursday", "Friday", "Saturday", "Sunday"
    ]
    scatter_data_weekday_count_trend = pd.DataFrame({
        "Weekday": data["Weekday"],
    })
    scatter_data_weekday_count_trend = scatter_data_weekday_count_trend.value_counts().reset_index()
    scatter_data_weekday_count_trend.columns = ["Weekday", "Ride Request Count"]
    scatter_data_weekday_count_trend["Weekday"] = pd.Categorical(scatter_data_weekday_count_trend["Weekday"], categories=weekday_order, ordered=True)
    scatter_data_weekday_count_trend = scatter_data_weekday_count_trend.sort_values("Weekday", ascending=True)
    fig2 = px.bar(
        scatter_data_weekday_count_trend,
        x="Weekday",
        y="Ride Request Count"
    )
    fig2.show()

def full_funnel_analysis_chart_with_counts():
    data = util.get_full_funnel_analysis_dataframe()

    fig = px.funnel(data, x=["Overall", "IOS", "Android", "Web", "18-24", "25-34", "35-44", "45-54", "Unknown Age"], y="Stage", title="Funnel with Counts")
    fig.update_traces(
        texttemplate="%{x}",
        hovertemplate="<b>%{y}</b><br>"
                      "Count: %{x}"

    )
    fig.update_layout(template="plotly_white")
    fig.show()

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
        title="Conversion Rate - Percent of the previous"
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        hovertemplate="<b>%{y}</b><br>"
                      "Conversion: %{x}"

    )
    fig.update_layout(template="plotly_white")
    fig.update_xaxes(ticksuffix="%")

    fig.show()

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
        title="Conversion Rate - Percent of the top"
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        hovertemplate="<b>%{y}</b><br>"
                      "Conversion: %{x}"
    )
    fig.update_layout(template="plotly_white")
    fig.update_xaxes(ticksuffix="%")

    fig.show()

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
    fig.update_layout(template="plotly_white")
    fig.show()

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
    fig.update_layout(template="plotly_white")
    fig.update_xaxes(
        dtick="H1",
        tickformat="%H"
    )
    fig.show()

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
    fig.update_layout(template="plotly_white")
    fig.update_xaxes(
        dtick="H1",
        tickformat="%H"
    )
    fig.show()

def time_per_day_of_year():
    data = util.get_surge_pricing_analysis_dataframe()

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
    fig.update_layout(template="plotly_white")
    fig.show()

def ride_request_per_day_of_year():
    data = util.get_surge_pricing_analysis_dataframe()

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
    fig.update_layout(template="plotly_white")
    fig.show()

def daily_ride_counts():
    data = util.get_daily_ride_count_dataframe()

    fig = px.bar(data,
                  x="day",
                  y="ride_count",
                  title="Daily Ride Request Count",
                  labels={"day": "Month", "ride_count": "Ride Count"})
    fig.update_layout(template="plotly_white")
    fig.update_xaxes(
        dtick="M1",
        tickformat="%Y-%m"
    )
    fig.show()

def ride_requests_hm_weekday_hour():
    hm = util.get_ride_requests_count_per_weekday_and_hour_dataframe()
    pivot = hm.pivot(index="Weekday", columns="Hour", values="requests").fillna(0)

    fig = px.imshow(
        pivot,
        title="Ride Requests – Heatmap (Weekday × Hour)",
        labels=dict(x="Hour", y="Weekday", color="Requests"),
        aspect="auto",
    )
    fig.update_layout(template="plotly_white")
    fig.show()


def pickup_location_density_map():
    data = util.get_all_pickup_locations_dataframe()

    fig = px.density_map(
        data,
        lat="lat",
        lon="lon",
        zoom=10,
        radius=8,
    )

    fig.show()





if __name__ == "__main__":
    main()