import pandas as pd

from funnel_utility import Utility
import plotly.express as px

util = Utility()


def main():

    question_julian_testing_area()
    question_one_testing_area()
    question_two_testing_area()
    question_three_testing_area()
    question_four_testing_area()

def question_julian_testing_area():

    #cancelationRatePerAge
    age_group_cancellations = util.get_cancellation_rate_per_age_group()
    fig = px.pie(
        names=age_group_cancellations.index,
        values=age_group_cancellations.values,
        title="Cancellation Rate per Age Group"
    )
    fig.show()

    ios_rate, android_rate, web_rate = util.get_cancellation_rate_per_platform()
    fig = px.pie(
        names=["iOS", "Android", "Web"],
        values=[ios_rate, android_rate, web_rate],
        title="Cancellation Rate per Platform"
    )
    fig.show()

    #averageReview
    age_group_ratings = util.get_average_review_rating_per_age_group()
    fig = px.bar(
        x=age_group_ratings.index,  # Altersgruppen als x-Achse
        y=age_group_ratings.values,  # Durchschnittliches Rating als y-Achse
        labels={'y': 'Average Rating', 'x': 'Age Group'},
        title="Average Review Rating per Age Group",
        text_auto=True,
        barmode='stack'  # Gestapeltes Balkendiagramm
    )
    fig.show()


    ios_rating, android_rating, web_rating = util.get_average_review_rating_per_platform()
    fig = px.bar(
        x=["iOS", "Android", "Web"],
        y=[ios_rating, android_rating, web_rating],
        labels={'y': 'Average Rating', 'x': 'Platform'},
        title="Average Review Rating per Platform",
        text_auto=True
    )
    fig.show()

    #avrageIncome
    age_18_24, age_25_34, age_35_44, age_45_54, age_unknown = util.get_average_income_per_age_group()
    fig = px.bar(
        x=["18-24", "25-34", "35-44", "45-54", "Unknown"],
        y=[age_18_24, age_25_34, age_35_44, age_45_54, age_unknown],
        labels={"x": "Age Group", "y": "Average Income (USD)"},
        title="Average Income per Age Group",
        text_auto=True
    )
    fig.show()

    #signups per agegroup
    age_18_24, age_25_34, age_35_44, age_45_54, age_unknown = util.get_signed_up_user_count_per_age_group()
    fig = px.pie(
        names=["Unknown", "18-24", "25-34", "35-44", "45-54"],
        values=[age_unknown, age_18_24, age_25_34, age_35_44, age_45_54],
        title="Signed Up User Count per Age Group"
    )
    fig.show()


def question_one_testing_area():

    data = util.get_funnel_analysis_dataframe()
    print(data)

    fig = px.bar(data, "Conversion From To", ["Before", "After", "Conversion Rate"], barmode="group")
    fig.show()

    download_to_signup, signup_to_ride_request, ride_request_to_transaction, transaction_to_approved_transaction = util.full_funnel_analysis()

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

    fig = px.bar(data, "Platform", ["Download Count", "Signed Up User Count", "Download to Sign Up Conversion Rate", "Median Money spent per Ride in $"], barmode="group")
    fig.show()

    download_count_per_platform = util.get_total_user_downloads_per_platform()
    signup_count_per_platform = util.get_total_user_signups_per_platform()

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
    #scatter_data_day_of_year_trend = scatter_data_day_of_year_trend.sort_values("Day of Year", ascending=True)
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


if __name__ == "__main__":
    main()
