import pandas as pd

from funnel_utility import Utility
import plotly.express as px

util = Utility()


def main():

    random_test()

    #question_one_testing_area()
    #question_two_testing_area()
    #question_three_testing_area()
    #question_four_testing_area()


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

    fig = px.bar(data, "Platform", ["Download Count", "Signed Up User Count", "Download to Sign Up Conversion Rate", "Average Money spent per Ride in $"], barmode="group")
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

def random_test():
    # --- Beispiel-Daten im Wide-Format ---
    data = {
        "Funnel-Stage": [
            "Downloads",
            "Sign Ups",
            "Unique User Ride Request",
            "Ride Requests",
            "Transactions",
            "Approved Transactions"
        ],
        "Overall": [100000, 60000, 30000, 25000, 18000, 15000],
        "IOS": [40000, 25000, 12000, 10000, 8000, 7000],
        "Android": [50000, 28000, 14000, 12000, 9000, 7500],
        "Web": [10000, 7000, 4000, 3000, 1000, 500],
        "18-24": [30000, 18000, 9000, 7500, 5300, 4500],
        "25-34": [40000, 24000, 12000, 10000, 7200, 6000],
        "35-44": [20000, 12000, 6000, 5000, 3600, 3000],
        "45-54": [8000, 5000, 2500, 2200, 1700, 1300],
        "Unknown": [2000, 1000, 500, 300, 200, 200],
    }
    df_wide = pd.DataFrame(data)

    # --- Long-Format ---
    value_cols = [c for c in df_wide.columns if c != "Funnel-Stage"]
    df_long = df_wide.melt(id_vars="Funnel-Stage",
                           value_vars=value_cols,
                           var_name="Category",
                           value_name="Value")

    # Stage-Order fixieren
    stage_order = [
        "Approved Transactions",
        "Transactions",
        "Ride Requests",
        "Unique User Ride Request",
        "Sign Ups",
        "Downloads"
    ]
    df_long["Funnel-Stage"] = pd.Categorical(df_long["Funnel-Stage"],
                                             categories=stage_order,
                                             ordered=True)

    # --- Prozent vom Top-of-Funnel (pro Kategorie getrennt) ---
    # Für jede Category: teile alle Stufen durch den Wert der ersten Stufe (Downloads)
    top_values = (
        df_long[df_long["Funnel-Stage"] == "Downloads"]
        .set_index("Category")["Value"]
        .to_dict()
    )

    df_long["pct_top"] = df_long.apply(
        lambda r: (r["Value"] / top_values[r["Category"]]) if top_values[r["Category"]] else 0.0,
        axis=1
    )

    # Funnel in Prozent zeichnen
    fig_top = px.funnel(
        df_long,
        x="pct_top",
        y="Funnel-Stage",
        color="Category",
        category_orders={"Funnel-Stage": stage_order},
        title="Funnel – Prozent vom Top-of-Funnel"
    )

    # Prozentformat & Hover
    fig_top.update_xaxes(tickformat=".0%")
    fig_top.update_traces(
        hovertemplate="<b>%{y}</b><br>Kategorie: %{fullData.name}"
                      "<br>Top-%: %{x:.1%}<extra></extra>"
    )

    # Optional: Legenden-/Dropdown-Logik aus dem vorherigen Beispiel weiterverwenden
    fig_top.show()



if __name__ == "__main__":
    main()