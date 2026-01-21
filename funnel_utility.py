import pandas as pd
from pathlib import Path
from dataclasses import dataclass

class Utility:

    @dataclass
    class UserPerPlatform:
        ios: int
        android: int
        web: int

    @dataclass
    class AgeGroupDistribution:
        age_18_to_24: int
        age_25_to_34: int
        age_35_to_44: int
        age_45_to_54: int
        unknown: int


    def __init__(self):
        # get Data from CSV
        self.downloads_df = pd.read_csv("Resources/app_downloads.csv")
        self.reviews_df = pd.read_csv("Resources/reviews.csv")
        self.ride_requests_df = pd.read_csv("Resources/ride_requests.csv")
        self.signups_df = pd.read_csv("Resources/signups.csv")
        self.transactions_df = pd.read_csv("Resources/transactions.csv")

        # Conserve Computing power for later Functions -> better merge only once
        self.downloads_x_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        self.downloads_x_rides_merged = pd.merge(self.downloads_x_signups_merged, self.ride_requests_df, on="user_id", how="inner")
        self.downloads_x_transactions_merged =  pd.merge(self.downloads_x_rides_merged, self.transactions_df, on="ride_id", how="inner")


    #region Funnel Analysis
    def get_overall_funnel_analysis_dataframe(self) -> pd.DataFrame:

        df = pd.DataFrame({
            "Stage": ["Downloads", "Sign ups", "Ride requests created", "Ride Requests accepted",
                      "Pickups happened", "Dropoffs happened", "Transactions created", "Transactions approved"],
            "Overall": [self.get_download_count(), self.get_signup_count(), self.get_ride_requests_count(), self.get_ride_request_accepted_count(),
                      self.get_ride_request_pickup_count(), self.get_ride_request_dropoff_count(), self.get_transaction_count(), self.get_approved_transactions_count()]
        })

        return df

    def get_full_funnel_analysis_dataframe(self) -> pd.DataFrame:
        platforms = self.get_platform_funnel_counts()
        age_groups = self.get_age_group_funnel_counts()

        df = pd.DataFrame({
            "Stage": ["Downloads", "Sign ups", "First ride request created", "First request accepted",
                      "First pickup happened", "First dropoff happened", "First transaction created", "First Payment approved"],
            "Overall": [self.get_download_count(), self.get_signup_count(), self.get_first_ride_request_count(), self.get_first_ride_request_accepted_count(),
                        self.get_first_ride_request_pickup_count(), self.get_first_ride_request_dropoff_count(), self.get_first_transaction_count(), self.get_first_approved_transaction_count()],
            "IOS": [p.ios for p in platforms],
            "Android": [p.android for p in platforms],
            "Web": [p.web for p in platforms],
            "18-24": [a.age_18_to_24 for a in age_groups],
            "25-34": [a.age_25_to_34 for a in age_groups],
            "35-44": [a.age_35_to_44 for a in age_groups],
            "45-54": [a.age_45_to_54 for a in age_groups],
            "Unknown Age": [a.unknown for a in age_groups]
        })

        return df

    def get_accept_cancel_pickup_duration_dataframe(self) -> pd.DataFrame:
        time_cols = [
            "request_ts",
            "accept_ts",
            "pickup_ts",
            "cancel_ts"
        ]

        df = pd.DataFrame()

        for col in time_cols:
            df[col] = pd.to_datetime(self.ride_requests_df[col], errors='coerce')

        df["time_till_accept"] = df["accept_ts"] - df["request_ts"]
        df["time_till_pickup"] = df["pickup_ts"] - df["request_ts"]
        df["time_till_cancel"] = df["cancel_ts"] - df["request_ts"]

        df["time_till_accept_min"] = df["time_till_accept"].dt.total_seconds() / 60
        df["time_till_pickup_min"] = df["time_till_pickup"].dt.total_seconds() / 60
        df["time_till_cancel_min"] = df["time_till_cancel"].dt.total_seconds() / 60

        return df

    def get_cancel_count_per_hour_dataframe(self) -> pd.DataFrame:
        df = self.ride_requests_df
        df["cancel_ts"] = pd.to_datetime(df["cancel_ts"], errors='coerce')

        df["hour"] = df["cancel_ts"].dt.hour

        cancel_per_hour = (
            df.groupby("hour")
            .size()
            .reindex(range(24), fill_value=0)
            .reset_index(name="cancel_count")
        )

        return cancel_per_hour

    def get_request_count_per_hour_dataframe(self) -> pd.DataFrame:
        df = self.ride_requests_df
        df["request_ts"] = pd.to_datetime(df["request_ts"], errors='coerce')

        df["hour"] = df["request_ts"].dt.hour

        request_per_hour = (
            df.groupby("hour")
            .size()
            .reindex(range(24), fill_value=0)
            .reset_index(name="request_count")
        )

        return request_per_hour

    #endregion

    #region Platform Analysis

    def get_platform_funnel_counts(self) -> tuple[UserPerPlatform, UserPerPlatform, UserPerPlatform, UserPerPlatform, UserPerPlatform, UserPerPlatform, UserPerPlatform, UserPerPlatform]:
        downloads = self.get_download_count_per_platform()
        signups = self.get_signup_count_per_platform()
        first_ride_requests = self.get_first_ride_request_count_per_platform()
        first_request_accepted = self.get_first_request_accepted_count_per_platform()
        first_pickup_happened = self.get_first_request_pickup_count_per_platform()
        first_dropoff_accepted = self.get_first_request_dropoff_count_per_platform()
        first_transactions = self.get_first_transaction_count_per_platform()
        first_approved_transactions = self.get_first_approved_transaction_count_per_platform()

        return downloads, signups, first_ride_requests, first_request_accepted, first_pickup_happened, first_dropoff_accepted, first_transactions, first_approved_transactions

    def get_download_count_per_platform(self) -> UserPerPlatform:
        ios = int(self.downloads_df[self.downloads_df["platform"] == "ios"]["app_download_key"].count())
        android = int(self.downloads_df[self.downloads_df["platform"] == "android"]["app_download_key"].count())
        web = int(self.downloads_df[self.downloads_df["platform"] == "web"]["app_download_key"].count())

        return self.UserPerPlatform(ios, android, web)

    def get_signup_count_per_platform(self) -> UserPerPlatform:
        merged = self.downloads_x_signups_merged

        ios = int(merged[merged["platform"] == "ios"]["app_download_key"].count())
        android = int(merged[merged["platform"] == "android"]["app_download_key"].count())
        web = int(merged[merged["platform"] == "web"]["app_download_key"].count())

        return self.UserPerPlatform(ios, android, web)

    def get_first_ride_request_count_per_platform(self) -> UserPerPlatform:
        merged = self.downloads_x_rides_merged

        ios = merged[merged["platform"] == "ios"]["user_id"].nunique()
        android = merged[merged["platform"] == "android"]["user_id"].nunique()
        web = merged[merged["platform"] == "web"]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)

    def get_first_request_accepted_count_per_platform(self) -> UserPerPlatform:
        merged = self.downloads_x_rides_merged

        ios = merged[(merged["platform"] == "ios") & (merged["accept_ts"].notna())]["user_id"].nunique()
        android = merged[(merged["platform"] == "android") & (merged["accept_ts"].notna())]["user_id"].nunique()
        web = merged[(merged["platform"] == "web") & (merged["accept_ts"].notna())]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)

    def get_first_request_pickup_count_per_platform(self) -> UserPerPlatform:
        merged = self.downloads_x_rides_merged

        ios = merged[(merged["platform"] == "ios") & (merged["pickup_ts"].notna())]["user_id"].nunique()
        android = merged[(merged["platform"] == "android") & (merged["pickup_ts"].notna())]["user_id"].nunique()
        web = merged[(merged["platform"] == "web") & (merged["pickup_ts"].notna())]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)

    def get_first_request_dropoff_count_per_platform(self) -> UserPerPlatform:
        merged = self.downloads_x_rides_merged

        ios = merged[(merged["platform"] == "ios") & (merged["pickup_ts"].notna())]["user_id"].nunique()
        android = merged[(merged["platform"] == "android") & (merged["pickup_ts"].notna())]["user_id"].nunique()
        web = merged[(merged["platform"] == "web") & (merged["pickup_ts"].notna())]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)

    def get_first_transaction_count_per_platform(self) -> UserPerPlatform:
        merged = self.downloads_x_transactions_merged

        ios = merged[merged["platform"] == "ios"]["user_id"].nunique()
        android = merged[merged["platform"] == "android"]["user_id"].nunique()
        web = merged[merged["platform"] == "web"]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)
        
    def get_first_approved_transaction_count_per_platform(self) -> UserPerPlatform:
        merged = self.downloads_x_transactions_merged

        ios = merged[(merged["platform"] == "ios") & (merged["charge_status"] == "Approved")]["user_id"].nunique()
        android = merged[(merged["platform"] == "android") & (merged["charge_status"] == "Approved")]["user_id"].nunique()
        web = merged[(merged["platform"] == "web") & (merged["charge_status"] == "Approved")]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)

    def get_cancellation_rate_per_platform(self):
        merged = self.downloads_x_rides_merged
        platforms = ["ios", "android", "web"]
        cancellation_rates = {}
        for platform in platforms:
            platform_df = merged[merged["platform"] == platform]
            total_requests = len(platform_df)
            canceled_requests = len(platform_df[platform_df["cancel_ts"].notnull()])
            if total_requests > 0:
                cancellation_rate = canceled_requests / total_requests
            else:
                cancellation_rate = 0
            cancellation_rates[platform] = cancellation_rate
        return cancellation_rates["ios"], cancellation_rates["android"], cancellation_rates["web"]

    def get_average_review_rating_per_platform(self):
        merged_reviews = pd.merge(self.reviews_df, self.signups_df, on='user_id')
        merged_reviews = pd.merge(merged_reviews, self.downloads_df, left_on='session_id', right_on='app_download_key')
        average_ratings = merged_reviews.groupby('platform')['rating'].mean().to_dict()
        ios_rating = average_ratings.get('ios', 0)
        android_rating = average_ratings.get('android', 0)
        web_rating = average_ratings.get('web', 0)
        return ios_rating, android_rating, web_rating


    #endregion

    #region Age Group Analysis
    def get_age_group_funnel_counts(self) -> tuple[AgeGroupDistribution, AgeGroupDistribution, AgeGroupDistribution, AgeGroupDistribution, AgeGroupDistribution, AgeGroupDistribution, AgeGroupDistribution, AgeGroupDistribution]:
        d_c = self.get_download_count_per_age_group()
        s_c = self.get_signup_count_per_age_group()
        f_rr_c = self.get_first_ride_request_count_per_age_group()
        f_ra_c = self.get_first_request_accepted_count_per_age_group()
        f_p_c = self.get_first_request_pickup_count_per_age_group()
        f_d_c = self.get_first_request_dropoff_count_per_age_group()
        f_t_c = self.get_first_transaction_count_per_age_group()
        f_at_c = self.get_first_approved_transaction_count_per_age_group()

        return d_c, s_c, f_rr_c, f_ra_c, f_p_c, f_d_c, f_t_c, f_at_c

    def get_download_count_per_age_group(self) -> AgeGroupDistribution:
        merged = self.downloads_x_signups_merged

        distribution = self.AgeGroupDistribution(
            age_18_to_24=int(merged[merged["age_range"] == "18-24"]["user_id"].count()),
            age_25_to_34=int(merged[merged["age_range"] == "25-34"]["user_id"].count()),
            age_35_to_44=int(merged[merged["age_range"] == "35-44"]["user_id"].count()),
            age_45_to_54=int(merged[merged["age_range"] == "45-54"]["user_id"].count()),
            unknown=int(merged[merged["age_range"] == "Unknown"]["user_id"].count())
        )

        return distribution


    def get_signup_count_per_age_group(self) -> AgeGroupDistribution:

        age_distribution = self.AgeGroupDistribution(
            age_18_to_24 = int(self.signups_df[self.signups_df["age_range"] == "18-24"]["user_id"].count()),
            age_25_to_34 = int(self.signups_df[self.signups_df["age_range"] == "25-34"]["user_id"].count()),
            age_35_to_44 = int(self.signups_df[self.signups_df["age_range"] == "35-44"]["user_id"].count()),
            age_45_to_54 = int(self.signups_df[self.signups_df["age_range"] == "45-54"]["user_id"].count()),
            unknown = int(self.signups_df[self.signups_df["age_range"] == "Unknown"]["user_id"].count())
        )
        return age_distribution

    def get_first_ride_request_count_per_age_group(self) -> AgeGroupDistribution:
        merged = self.downloads_x_rides_merged

        distribution = self.AgeGroupDistribution(
            age_18_to_24=merged[merged["age_range"] == "18-24"]["user_id"].nunique(),
            age_25_to_34=merged[merged["age_range"] == "25-34"]["user_id"].nunique(),
            age_35_to_44=merged[merged["age_range"] == "35-44"]["user_id"].nunique(),
            age_45_to_54=merged[merged["age_range"] == "45-54"]["user_id"].nunique(),
            unknown=merged[merged["age_range"] == "Unknown"]["user_id"].nunique()
        )

        return distribution

    def get_first_request_accepted_count_per_age_group(self) -> AgeGroupDistribution:
        merged = self.downloads_x_rides_merged

        distribution = self.AgeGroupDistribution(
            age_18_to_24=merged[(merged["age_range"] == "18-24") & (merged["accept_ts"].notna())]["user_id"].nunique(),
            age_25_to_34=merged[(merged["age_range"] == "25-34") & (merged["accept_ts"].notna())]["user_id"].nunique(),
            age_35_to_44=merged[(merged["age_range"] == "35-44") & (merged["accept_ts"].notna())]["user_id"].nunique(),
            age_45_to_54=merged[(merged["age_range"] == "45-54") & (merged["accept_ts"].notna())]["user_id"].nunique(),
            unknown=merged[(merged["age_range"] == "Unknown") & (merged["accept_ts"].notna())]["user_id"].nunique()
        )

        return distribution

    def get_first_request_pickup_count_per_age_group(self) -> AgeGroupDistribution:
        merged = self.downloads_x_rides_merged

        distribution = self.AgeGroupDistribution(
            age_18_to_24=merged[(merged["age_range"] == "18-24") & (merged["pickup_ts"].notna())]["user_id"].nunique(),
            age_25_to_34=merged[(merged["age_range"] == "25-34") & (merged["pickup_ts"].notna())]["user_id"].nunique(),
            age_35_to_44=merged[(merged["age_range"] == "35-44") & (merged["pickup_ts"].notna())]["user_id"].nunique(),
            age_45_to_54=merged[(merged["age_range"] == "45-54") & (merged["pickup_ts"].notna())]["user_id"].nunique(),
            unknown=merged[(merged["age_range"] == "Unknown") & (merged["pickup_ts"].notna())]["user_id"].nunique()
        )

        return distribution

    def get_first_request_dropoff_count_per_age_group(self) -> AgeGroupDistribution:
        merged = self.downloads_x_rides_merged

        distribution = self.AgeGroupDistribution(
            age_18_to_24=merged[(merged["age_range"] == "18-24") & (merged["dropoff_ts"].notna())]["user_id"].nunique(),
            age_25_to_34=merged[(merged["age_range"] == "25-34") & (merged["dropoff_ts"].notna())]["user_id"].nunique(),
            age_35_to_44=merged[(merged["age_range"] == "35-44") & (merged["dropoff_ts"].notna())]["user_id"].nunique(),
            age_45_to_54=merged[(merged["age_range"] == "45-54") & (merged["dropoff_ts"].notna())]["user_id"].nunique(),
            unknown=merged[(merged["age_range"] == "Unknown") & (merged["dropoff_ts"].notna())]["user_id"].nunique()
        )

        return distribution

    def get_first_transaction_count_per_age_group(self) -> AgeGroupDistribution:
        merged = self.downloads_x_transactions_merged

        distribution = self.AgeGroupDistribution(
            age_18_to_24=merged[merged["age_range"] == "18-24"]["user_id"].nunique(),
            age_25_to_34=merged[merged["age_range"] == "25-34"]["user_id"].nunique(),
            age_35_to_44=merged[merged["age_range"] == "35-44"]["user_id"].nunique(),
            age_45_to_54=merged[merged["age_range"] == "45-54"]["user_id"].nunique(),
            unknown=merged[merged["age_range"] == "Unknown"]["user_id"].nunique()
        )

        return distribution

    def get_first_approved_transaction_count_per_age_group(self) -> AgeGroupDistribution:
        merged = self.downloads_x_transactions_merged

        distribution = self.AgeGroupDistribution(
            age_18_to_24=merged[(merged["age_range"] == "18-24") & (merged["charge_status"] == "Approved")]["user_id"].nunique(),
            age_25_to_34=merged[(merged["age_range"] == "25-34") & (merged["charge_status"] == "Approved")]["user_id"].nunique(),
            age_35_to_44=merged[(merged["age_range"] == "35-44") & (merged["charge_status"] == "Approved")]["user_id"].nunique(),
            age_45_to_54=merged[(merged["age_range"] == "45-54") & (merged["charge_status"] == "Approved")]["user_id"].nunique(),
            unknown=merged[(merged["age_range"] == "Unknown") & (merged["charge_status"] == "Approved")]["user_id"].nunique()
        )

        return distribution

    def get_cancellation_rate_per_age_group(self):
        merged_df = pd.merge(self.ride_requests_df, self.signups_df, on='user_id')
        merged_df['canceled'] = merged_df['cancel_ts'].notnull()
        cancellation_rate_per_age_group = merged_df.groupby('age_range')['canceled'].mean()
        return cancellation_rate_per_age_group

    def get_average_review_rating_per_age_group(self):
        merged_reviews = pd.merge(self.reviews_df, self.signups_df, on='user_id')
        average_ratings_per_age_group = merged_reviews.groupby('age_range')['rating'].mean()
        return average_ratings_per_age_group

    def get_average_income_per_age_group(self):
        approved_tx = self.transactions_df[self.transactions_df["charge_status"] == "Approved"]
        tx_with_user = pd.merge(
            approved_tx,
            self.ride_requests_df[["ride_id", "user_id"]],
            on="ride_id",
            how="inner"
        )
        full = pd.merge(
            tx_with_user,
            self.signups_df[["user_id", "age_range"]],
            on="user_id",
            how="inner"
        )
        avg_income = full.groupby("age_range")["purchase_amount_usd"].mean().to_dict()
        return (
            avg_income.get("18-24", 0.0),
            avg_income.get("25-34", 0.0),
            avg_income.get("35-44", 0.0),
            avg_income.get("45-54", 0.0),
            avg_income.get("Unknown", 0.0),
        )

    def get_signed_up_user_count_per_age_group(self):
        counts = self.signups_df["age_range"].value_counts(dropna=False).to_dict()
        return (
            int(counts.get("18-24", 0)),
            int(counts.get("25-34", 0)),
            int(counts.get("35-44", 0)),
            int(counts.get("45-54", 0)),
            int(counts.get("Unknown", 0)),
        )

    #endregion

    #region Surge Pricing Analysis
    def get_ride_requests_ts_split_dataframe(self) -> pd.DataFrame:
        time_and_date = self.get_all_ride_request_time_date_ts()

        df = pd.DataFrame({
            "Date": time_and_date["Date"],
            "Time": time_and_date["Time"].dt.time,
            "Day of Year": time_and_date["Date"].dt.dayofyear,
            "Hour": time_and_date["Time"].dt.hour,
            "Weekday": time_and_date["Date"].dt.day_name()
        })

        return df

    def get_all_ride_request_time_date_ts(self) -> pd.DataFrame:
        df = pd.DataFrame()
        #get all requests not null
        df["request_ts"] = self.ride_requests_df[self.ride_requests_df["request_ts"] != pd.notnull]["request_ts"]
        #convert date string to date type
        df["request_ts"] = pd.to_datetime(df["request_ts"], format="%Y-%m-%d %H:%M:%S")
        #split time and date
        ready_df = pd.DataFrame({
            "Date": df["request_ts"].dt.date,
            "Time": df["request_ts"].dt.time
        })

        #reconvert to pandas.Timestamp
        ready_df["Date"] = pd.to_datetime(ready_df["Date"], format="%Y-%m-%d")
        ready_df["Time"] = pd.to_datetime(ready_df["Time"], format="%H:%M:%S")

        return ready_df

    def get_all_pickup_locations_dataframe(self) -> pd.DataFrame:
        df = self.ride_requests_df
        df = df[
            df["pickup_location"].notna() &
            (df["pickup_location"] != "<unset>")
            ]

        #robust splitten (beliebig viele Whitespaces)
        coords = df["pickup_location"].str.split(r"\s+", expand=True)

        #nur die ersten zwei Spalten nehmen
        coords.columns = ["lat", "lon"]

        # 4. sicher in numerisch umwandeln
        coords = coords.apply(pd.to_numeric, errors="coerce")

        return coords

    def get_daily_ride_count_dataframe(self) -> pd.DataFrame:
        df = self.ride_requests_df
        df["request_ts"] = pd.to_datetime(df["request_ts"], errors="coerce")
        df["day"] = df["request_ts"].dt.to_period("D").dt.to_timestamp()

        return (
            df.dropna(subset=["request_ts"])
            .groupby("day")
            .size()
            .reset_index(name="ride_count")
            .sort_values("day")
        )

    def get_ride_requests_count_per_weekday_and_hour_dataframe(self) -> pd.DataFrame:
        df = self.get_all_ride_request_time_date_ts()

        data = pd.DataFrame({
            "Hour": df["Time"].dt.hour,
            "Weekday": df["Date"].dt.day_name()
        })

        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        data["Weekday"] = pd.Categorical(data["Weekday"], categories=weekday_order, ordered=True)

        return data.groupby(["Weekday", "Hour"]).size().reset_index(name="requests")

    #endregion

    #region Helper Functions
    def get_download_count(self) -> int:
        return self.downloads_df.shape[0]

    def get_signup_count(self) -> int:
        return self.signups_df.shape[0]

    def get_ride_requests_count(self) -> int:
        return self.ride_requests_df.shape[0]

    def get_first_ride_request_count(self) -> int:
        return self.ride_requests_df["user_id"].nunique()

    def get_ride_request_accepted_count(self) -> int:
        return self.ride_requests_df[self.ride_requests_df["accept_ts"].notna()]["user_id"].count()

    def get_first_ride_request_accepted_count(self) -> int:
        return self.ride_requests_df[self.ride_requests_df["accept_ts"].notna()]["user_id"].nunique()

    def get_ride_request_pickup_count(self) -> int:
        return self.ride_requests_df[self.ride_requests_df["pickup_ts"].notna()]["user_id"].count()

    def get_first_ride_request_pickup_count(self) -> int:
        return self.ride_requests_df[self.ride_requests_df["pickup_ts"].notna()]["user_id"].nunique()

    def get_ride_request_dropoff_count(self) -> int:
        return self.ride_requests_df[self.ride_requests_df["dropoff_ts"].notna()]["user_id"].count()

    def get_first_ride_request_dropoff_count(self) -> int:
        return self.ride_requests_df[self.ride_requests_df["dropoff_ts"].notna()]["user_id"].nunique()

    def get_transaction_count(self) -> int:
        return self.transactions_df.shape[0]

    def get_first_transaction_count(self) -> int:
        merged = pd.merge(self.ride_requests_df, self.transactions_df, on="ride_id", how="inner")

        return merged["user_id"].nunique()

    def get_approved_transactions_count(self) -> int:
        return int(self.transactions_df[self.transactions_df["charge_status"] == "Approved"]["transaction_id"].count())

    def get_first_approved_transaction_count(self) -> int:
        merged = pd.merge(self.ride_requests_df, self.transactions_df, on="ride_id", how="inner")

        return merged[(merged["charge_status"] == "Approved") & (merged["dropoff_ts"].notna())]["user_id"].nunique()

    #endregion
    
    #region Utility Functions
    @staticmethod
    def save_and_open(fig, filename: str, auto_open: bool = True):
        out_dir = Path("output_html")
        out_dir.mkdir(parents=True, exist_ok=True)

        path = out_dir / filename

        fig.write_html(str(path), auto_open=auto_open, include_plotlyjs="cdn")

    @staticmethod
    def apply_constant_plot_layout(fig):
        fig.update_layout(
            template="plotly_white",
            font=dict(size=15),
            title=dict(font=dict(size=20)),
            legend=dict(
                font=dict(size=13),
                bgcolor="rgba(255,255,255,0.85)",
                bordercolor="rgba(0,0,0,0.10)",
                borderwidth=2
            ),
            margin=dict(l=70, r=40, t=80, b=70),
        )
        return fig
    
    #endregion
