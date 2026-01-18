import pandas as pd

from funnel_utility import Utility
import plotly.express as px

util = Utility()


def main():

    full_funnel_analysis_chart_with_counts()
    full_funnel_analysis_chart_percent_of_the_previous()
    full_funnel_analysis_chart_percent_of_the_top()
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
    print(data)

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

if __name__ == "__main__":
    main()