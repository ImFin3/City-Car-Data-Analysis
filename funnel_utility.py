import pandas as pd
from dataclasses import dataclass

class Utility:

    @dataclass
    class ConversionStruct:
        before: int
        after: int
        conversion_rate: float

    @dataclass
    class UserPerPlatform:
        ios: int
        android: int
        web: int

    @dataclass
    class MoneySpentPerPlatform:
        ios: float
        android: float
        web: float

    @dataclass
    class AgeGroupDistribution:
        age_18_to_24: int
        age_25_to_34: int
        age_35_to_44: int
        age_45_to_54: int
        unknown: int


    #get Data
    def __init__(self):
        self.downloads_df = pd.read_csv("Resources/app_downloads.csv")
        self.reviews_df = pd.read_csv("Resources/reviews.csv")
        self.ride_requests_df = pd.read_csv("Resources/ride_requests.csv")
        self.signups_df = pd.read_csv("Resources/signups.csv")
        self.transactions_df = pd.read_csv("Resources/transactions.csv")


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
            "IOS": [platforms[0].ios, platforms[1].ios, platforms[2].ios, platforms[3].ios,
                    platforms[4].ios, platforms[5].ios, platforms[6].ios, platforms[7].ios],
            "Android": [platforms[0].android, platforms[1].android, platforms[2].android, platforms[3].android,
                        platforms[4].android, platforms[5].android, platforms[6].android, platforms[7].android],
            "Web": [platforms[0].web, platforms[1].web, platforms[2].web, platforms[3].web,
                    platforms[4].web, platforms[5].web, platforms[6].web, platforms[7].web],
            "18-24": [age_groups[0].age_18_to_24, age_groups[1].age_18_to_24, age_groups[2].age_18_to_24, age_groups[3].age_18_to_24,
                      age_groups[4].age_18_to_24, age_groups[5].age_18_to_24, age_groups[6].age_18_to_24, age_groups[7].age_18_to_24],
            "25-34": [age_groups[0].age_25_to_34, age_groups[1].age_25_to_34, age_groups[2].age_25_to_34, age_groups[3].age_25_to_34,
                      age_groups[4].age_25_to_34, age_groups[5].age_25_to_34, age_groups[6].age_25_to_34, age_groups[7].age_25_to_34],
            "35-44": [age_groups[0].age_35_to_44, age_groups[1].age_35_to_44, age_groups[2].age_35_to_44, age_groups[3].age_35_to_44,
                      age_groups[4].age_35_to_44, age_groups[5].age_35_to_44, age_groups[6].age_35_to_44, age_groups[7].age_35_to_44],
            "45-54": [age_groups[0].age_45_to_54, age_groups[1].age_45_to_54, age_groups[2].age_45_to_54, age_groups[3].age_45_to_54,
                      age_groups[4].age_45_to_54, age_groups[5].age_45_to_54, age_groups[6].age_45_to_54, age_groups[7].age_45_to_54],
            "Unknown Age": [age_groups[0].unknown, age_groups[1].unknown, age_groups[2].unknown, age_groups[3].unknown,
                            age_groups[4].unknown, age_groups[5].unknown, age_groups[6].unknown, age_groups[7].unknown]
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
    def get_platform_analysis_dataframe(self) -> pd.DataFrame:
        p_d_c = self.get_download_count_per_platform()        # p_d_c => platform_download_count
        p_s_c = self.get_signup_count_per_platform()          # p_s_c => platform_signup_count
        a_m = self.get_average_money_spent_per_ride_per_platform()     # a_m => average_money

        df = pd.DataFrame({
            "Platform": ["iOS", "Android", "Web"],
            "Download Count": [p_d_c.ios, p_d_c.android, p_d_c.web],
            "Signed Up User Count": [p_s_c.ios, p_s_c.android, p_s_c.web],
            "Download to Sign Up Conversion Rate": [self.get_conversion_rate(p_d_c.ios, p_s_c.ios), self.get_conversion_rate(p_d_c.android, p_s_c.android), self.get_conversion_rate(p_d_c.web, p_s_c.web)],
            "Average Money spent per Ride in $": [a_m.ios, a_m.android, a_m.web],
        })

        return df

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
        merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")

        ios = int(merged[merged["platform"] == "ios"]["app_download_key"].count())
        android = int(merged[merged["platform"] == "android"]["app_download_key"].count())
        web = int(merged[merged["platform"] == "web"]["app_download_key"].count())

        return self.UserPerPlatform(ios, android, web)

    def get_ride_request_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")

        ios = int(download_ride_requests_merged[download_ride_requests_merged["platform"] == "ios"]["user_id"].count())
        android = int(download_ride_requests_merged[download_ride_requests_merged["platform"] == "android"]["user_id"].count())
        web = int(download_ride_requests_merged[download_ride_requests_merged["platform"] == "web"]["user_id"].count())

        return self.UserPerPlatform(ios, android, web)

    def get_first_ride_request_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")

        ios = download_ride_requests_merged[download_ride_requests_merged["platform"] == "ios"]["user_id"].nunique()
        android = download_ride_requests_merged[download_ride_requests_merged["platform"] == "android"]["user_id"].nunique()
        web = download_ride_requests_merged[download_ride_requests_merged["platform"] == "web"]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)

    def get_first_request_accepted_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")

        ios = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "ios") &
                                            (download_ride_requests_merged["accept_ts"].notna())]["user_id"].nunique()
        android = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "android") &
                                            (download_ride_requests_merged["accept_ts"].notna())]["user_id"].nunique()
        web = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "web") &
                                            (download_ride_requests_merged["accept_ts"].notna())]["user_id"].nunique()


        return self.UserPerPlatform(ios, android, web)

    def get_first_request_pickup_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")

        ios = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "ios") &
                                            (download_ride_requests_merged["pickup_ts"].notna())]["user_id"].nunique()
        android = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "android") &
                                                (download_ride_requests_merged["pickup_ts"].notna())]["user_id"].nunique()
        web = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "web") &
                                            (download_ride_requests_merged["pickup_ts"].notna())]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)

    def get_first_request_dropoff_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")

        ios = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "ios") &
                                            (download_ride_requests_merged["pickup_ts"].notna())]["user_id"].nunique()
        android = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "android") &
                                                (download_ride_requests_merged["pickup_ts"].notna())]["user_id"].nunique()
        web = download_ride_requests_merged[(download_ride_requests_merged["platform"] == "web") &
                                            (download_ride_requests_merged["pickup_ts"].notna())]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)


    def get_transaction_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")
        downloads_transactions_merged = pd.merge(download_ride_requests_merged, self.transactions_df, on="ride_id", how="inner")

        ios = int(downloads_transactions_merged[downloads_transactions_merged["platform"] == "ios"]["user_id"].count())
        android = int(downloads_transactions_merged[downloads_transactions_merged["platform"] == "android"]["user_id"].count())
        web = int(downloads_transactions_merged[downloads_transactions_merged["platform"] == "web"]["user_id"].count())

        return self.UserPerPlatform(ios, android, web)

    def get_first_transaction_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")
        downloads_transactions_merged = pd.merge(download_ride_requests_merged, self.transactions_df, on="ride_id", how="inner")

        ios = downloads_transactions_merged[downloads_transactions_merged["platform"] == "ios"]["user_id"].nunique()
        android = downloads_transactions_merged[downloads_transactions_merged["platform"] == "android"]["user_id"].nunique()
        web = downloads_transactions_merged[downloads_transactions_merged["platform"] == "web"]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)
    
    def get_approved_transaction_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")
        downloads_transactions_merged = pd.merge(download_ride_requests_merged, self.transactions_df, on="ride_id", how="inner")

        ios = int(downloads_transactions_merged[(downloads_transactions_merged["platform"] == "ios") & (downloads_transactions_merged["charge_status"] == "Approved")]["user_id"].count())
        android = int(downloads_transactions_merged[(downloads_transactions_merged["platform"] == "android") & (downloads_transactions_merged["charge_status"] == "Approved")]["user_id"].count())
        web = int(downloads_transactions_merged[(downloads_transactions_merged["platform"] == "web") & (downloads_transactions_merged["charge_status"] == "Approved")]["user_id"].count())

        return self.UserPerPlatform(ios, android, web)
        
    def get_first_approved_transaction_count_per_platform(self) -> UserPerPlatform:
        download_signups_merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        download_ride_requests_merged = pd.merge(download_signups_merged, self.ride_requests_df, on="user_id", how="inner")
        downloads_transactions_merged = pd.merge(download_ride_requests_merged, self.transactions_df, on="ride_id", how="inner")

        ios = downloads_transactions_merged[(downloads_transactions_merged["platform"] == "ios") & (downloads_transactions_merged["charge_status"] == "Approved")]["user_id"].nunique()
        android = downloads_transactions_merged[(downloads_transactions_merged["platform"] == "android") & (downloads_transactions_merged["charge_status"] == "Approved")]["user_id"].nunique()
        web = downloads_transactions_merged[(downloads_transactions_merged["platform"] == "web") & (downloads_transactions_merged["charge_status"] == "Approved")]["user_id"].nunique()

        return self.UserPerPlatform(ios, android, web)

    def get_average_money_spent_per_ride_per_platform(self) -> MoneySpentPerPlatform:
        #merge downloads(platform) with signups
        platform_user_id = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id",how="inner")
        #get approved transactions only
        approved_transactions = self.transactions_df[self.transactions_df["charge_status"] == "Approved"]
        #merge transactions with rides
        rides_with_approved_transactions = pd.merge(self.ride_requests_df, approved_transactions, on="ride_id", how="inner")
        #merge platform with rides
        full_data_set = pd.merge(rides_with_approved_transactions, platform_user_id, on="user_id", how="inner")

        #calculate mean of each
        median_ios = full_data_set[full_data_set["platform"] == "ios"]["purchase_amount_usd"].mean()
        median_android = full_data_set[full_data_set["platform"] == "android"]["purchase_amount_usd"].mean()
        median_web = full_data_set[full_data_set["platform"] == "web"]["purchase_amount_usd"].mean()

        return self.MoneySpentPerPlatform(float(median_ios), float(median_android), float(median_web))

    def get_cancellation_rate_per_platform(self):
        merged_df = pd.merge(self.signups_df, self.ride_requests_df, on="user_id", how="inner")
        merged_df = pd.merge(merged_df, self.downloads_df, left_on="session_id", right_on="app_download_key",
                             how="inner")
        platforms = ["ios", "android", "web"]
        cancellation_rates = {}
        for platform in platforms:
            platform_df = merged_df[merged_df["platform"] == platform]
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
    def get_age_group_analysis_dataframe(self) -> pd.DataFrame:
        s_a_d_c = self.get_signup_count_per_age_group()  # s_a_d_c => signup_age_distribution_count
        a_rr_a_d_c = self.get_approved_ride_request_count_per_age_group()   # a_rr_a_d_c => approved_riderequest_age_distribution_count
        r_p_u_18_24 = self.get_conversion_rate(s_a_d_c.age_18_to_24 ,a_rr_a_d_c.age_18_to_24)  # r_p_u => rides_per_user
        r_p_u_25_34 = self.get_conversion_rate(s_a_d_c.age_25_to_34 ,a_rr_a_d_c.age_25_to_34)
        r_p_u_35_44 = self.get_conversion_rate(s_a_d_c.age_35_to_44 ,a_rr_a_d_c.age_35_to_44)
        r_p_u_45_54 = self.get_conversion_rate(s_a_d_c.age_45_to_54 ,a_rr_a_d_c.age_45_to_54)
        r_p_u_unknown = self.get_conversion_rate(s_a_d_c.unknown, a_rr_a_d_c.unknown)

        df = pd.DataFrame({
            "Age Group": ["18-24", "25-34", "35-44", "45-54", "Unknown"],
            "Sign Up Count": [s_a_d_c.age_18_to_24, s_a_d_c.age_25_to_34, s_a_d_c.age_35_to_44, s_a_d_c.age_45_to_54, s_a_d_c.unknown],
            "Approved Ride Request Count": [a_rr_a_d_c.age_18_to_24, a_rr_a_d_c.age_25_to_34, a_rr_a_d_c.age_35_to_44, a_rr_a_d_c.age_45_to_54, a_rr_a_d_c.unknown],
            "Approved Rides per Signed Up User": [r_p_u_18_24, r_p_u_25_34, r_p_u_35_44, r_p_u_45_54, r_p_u_unknown]
        })

        return df

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
        merged = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")

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
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=download_ride_requests[download_ride_requests["age_range"] == "18-24"]["user_id"].nunique(),
            age_25_to_34=download_ride_requests[download_ride_requests["age_range"] == "25-34"]["user_id"].nunique(),
            age_35_to_44=download_ride_requests[download_ride_requests["age_range"] == "35-44"]["user_id"].nunique(),
            age_45_to_54=download_ride_requests[download_ride_requests["age_range"] == "45-54"]["user_id"].nunique(),
            unknown=download_ride_requests[download_ride_requests["age_range"] == "Unknown"]["user_id"].nunique()
        )

        return distribution

    def get_first_request_accepted_count_per_age_group(self) -> AgeGroupDistribution:
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=download_ride_requests[(download_ride_requests["age_range"] == "18-24") &
                                                (download_ride_requests["accept_ts"].notna())]["user_id"].nunique(),
            age_25_to_34=download_ride_requests[(download_ride_requests["age_range"] == "25-34") &
                                                (download_ride_requests["accept_ts"].notna())]["user_id"].nunique(),
            age_35_to_44=download_ride_requests[(download_ride_requests["age_range"] == "35-44") &
                                                (download_ride_requests["accept_ts"].notna())]["user_id"].nunique(),
            age_45_to_54=download_ride_requests[(download_ride_requests["age_range"] == "45-54") &
                                                (download_ride_requests["accept_ts"].notna())]["user_id"].nunique(),
            unknown=download_ride_requests[(download_ride_requests["age_range"] == "Unknown") &
                                           (download_ride_requests["accept_ts"].notna())]["user_id"].nunique()
        )

        return distribution

    def get_first_request_pickup_count_per_age_group(self) -> AgeGroupDistribution:
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=download_ride_requests[(download_ride_requests["age_range"] == "18-24") &
                                                (download_ride_requests["pickup_ts"].notna())]["user_id"].nunique(),
            age_25_to_34=download_ride_requests[(download_ride_requests["age_range"] == "25-34") &
                                                (download_ride_requests["pickup_ts"].notna())]["user_id"].nunique(),
            age_35_to_44=download_ride_requests[(download_ride_requests["age_range"] == "35-44") &
                                                (download_ride_requests["pickup_ts"].notna())]["user_id"].nunique(),
            age_45_to_54=download_ride_requests[(download_ride_requests["age_range"] == "45-54") &
                                                (download_ride_requests["pickup_ts"].notna())]["user_id"].nunique(),
            unknown=download_ride_requests[(download_ride_requests["age_range"] == "Unknown") &
                                           (download_ride_requests["pickup_ts"].notna())]["user_id"].nunique()
        )

        return distribution

    def get_first_request_dropoff_count_per_age_group(self) -> AgeGroupDistribution:
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=download_ride_requests[(download_ride_requests["age_range"] == "18-24") &
                                                (download_ride_requests["dropoff_ts"].notna())]["user_id"].nunique(),
            age_25_to_34=download_ride_requests[(download_ride_requests["age_range"] == "25-34") &
                                                (download_ride_requests["dropoff_ts"].notna())]["user_id"].nunique(),
            age_35_to_44=download_ride_requests[(download_ride_requests["age_range"] == "35-44") &
                                                (download_ride_requests["dropoff_ts"].notna())]["user_id"].nunique(),
            age_45_to_54=download_ride_requests[(download_ride_requests["age_range"] == "45-54") &
                                                (download_ride_requests["dropoff_ts"].notna())]["user_id"].nunique(),
            unknown=download_ride_requests[(download_ride_requests["age_range"] == "Unknown") &
                                           (download_ride_requests["dropoff_ts"].notna())]["user_id"].nunique()
        )

        return distribution

    def get_ride_request_count_per_age_group(self) -> AgeGroupDistribution:
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=int(download_ride_requests[download_ride_requests["age_range"] == "18-24"]["user_id"].count()),
            age_25_to_34=int(download_ride_requests[download_ride_requests["age_range"] == "25-34"]["user_id"].count()),
            age_35_to_44=int(download_ride_requests[download_ride_requests["age_range"] == "35-44"]["user_id"].count()),
            age_45_to_54=int(download_ride_requests[download_ride_requests["age_range"] == "45-54"]["user_id"].count()),
            unknown=int(download_ride_requests[download_ride_requests["age_range"] == "Unknown"]["user_id"].count())
        )

        return distribution

    def get_first_transaction_count_per_age_group(self) -> AgeGroupDistribution:
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")
        download_transactions = pd.merge(download_ride_requests, self.transactions_df, on="ride_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=download_transactions[download_transactions["age_range"] == "18-24"]["user_id"].nunique(),
            age_25_to_34=download_transactions[download_transactions["age_range"] == "25-34"]["user_id"].nunique(),
            age_35_to_44=download_transactions[download_transactions["age_range"] == "35-44"]["user_id"].nunique(),
            age_45_to_54=download_transactions[download_transactions["age_range"] == "45-54"]["user_id"].nunique(),
            unknown=download_transactions[download_transactions["age_range"] == "Unknown"]["user_id"].nunique()
        )

        return distribution

    def get_transaction_count_per_age_group(self) -> AgeGroupDistribution:
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")
        download_transactions = pd.merge(download_ride_requests, self.transactions_df, on="ride_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=int(download_transactions[download_transactions["age_range"] == "18-24"]["user_id"].count()),
            age_25_to_34=int(download_transactions[download_transactions["age_range"] == "25-34"]["user_id"].count()),
            age_35_to_44=int(download_transactions[download_transactions["age_range"] == "35-44"]["user_id"].count()),
            age_45_to_54=int(download_transactions[download_transactions["age_range"] == "45-54"]["user_id"].count()),
            unknown=int(download_transactions[download_transactions["age_range"] == "Unknown"]["user_id"].count())
        )

        return distribution

    def get_first_approved_transaction_count_per_age_group(self) -> AgeGroupDistribution:
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")
        download_transactions = pd.merge(download_ride_requests, self.transactions_df, on="ride_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=download_transactions[(download_transactions["age_range"] == "18-24") & (download_transactions["charge_status"] == "Approved")]["user_id"].nunique(),
            age_25_to_34=download_transactions[(download_transactions["age_range"] == "25-34") & (download_transactions["charge_status"] == "Approved")]["user_id"].nunique(),
            age_35_to_44=download_transactions[(download_transactions["age_range"] == "35-44") & (download_transactions["charge_status"] == "Approved")]["user_id"].nunique(),
            age_45_to_54=download_transactions[(download_transactions["age_range"] == "45-54") & (download_transactions["charge_status"] == "Approved")]["user_id"].nunique(),
            unknown=download_transactions[(download_transactions["age_range"] == "Unknown") & (download_transactions["charge_status"] == "Approved")]["user_id"].nunique()
        )

        return distribution

    def get_approved_transaction_count_per_age_group(self) -> AgeGroupDistribution:
        download_signups = pd.merge(self.downloads_df, self.signups_df, how="inner", left_on="app_download_key", right_on="session_id")
        download_ride_requests = pd.merge(download_signups, self.ride_requests_df, on="user_id", how="inner")
        download_transactions = pd.merge(download_ride_requests, self.transactions_df, on="ride_id", how="inner")

        distribution = self.AgeGroupDistribution(
            age_18_to_24=int(download_transactions[(download_transactions["age_range"] == "18-24") & (download_transactions["charge_status"] == "Approved")]["user_id"].count()),
            age_25_to_34=int(download_transactions[(download_transactions["age_range"] == "25-34") & (download_transactions["charge_status"] == "Approved")]["user_id"].count()),
            age_35_to_44=int(download_transactions[(download_transactions["age_range"] == "35-44") & (download_transactions["charge_status"] == "Approved")]["user_id"].count()),
            age_45_to_54=int(download_transactions[(download_transactions["age_range"] == "45-54") & (download_transactions["charge_status"] == "Approved")]["user_id"].count()),
            unknown=int(download_transactions[(download_transactions["age_range"] == "Unknown") & (download_transactions["charge_status"] == "Approved")]["user_id"].count())
        )

        return distribution


    def get_approved_ride_request_count_per_age_group(self) -> AgeGroupDistribution:
        approved_transactions = self.transactions_df[self.transactions_df["charge_status"] == "Approved"]
        approved_ride_requests = pd.merge(self.ride_requests_df, approved_transactions, on="ride_id", how="inner")
        merged_user_id_with_approved_ride_requests = pd.merge(self.signups_df, approved_ride_requests, on="user_id", how="inner")

        age_distribution = self.AgeGroupDistribution(0, 0, 0, 0, 0)
        age_distribution.age_18_to_24 = int(merged_user_id_with_approved_ride_requests[merged_user_id_with_approved_ride_requests["age_range"] == "18-24"]["user_id"].count())
        age_distribution.age_25_to_34 = int(merged_user_id_with_approved_ride_requests[merged_user_id_with_approved_ride_requests["age_range"] == "25-34"]["user_id"].count())
        age_distribution.age_35_to_44 = int(merged_user_id_with_approved_ride_requests[merged_user_id_with_approved_ride_requests["age_range"] == "35-44"]["user_id"].count())
        age_distribution.age_45_to_54 = int(merged_user_id_with_approved_ride_requests[merged_user_id_with_approved_ride_requests["age_range"] == "45-54"]["user_id"].count())
        age_distribution.unknown = int(merged_user_id_with_approved_ride_requests[merged_user_id_with_approved_ride_requests["age_range"] == "Unknown"]["user_id"].count())

        return age_distribution

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

    @staticmethod
    def get_conversion_rate(start: int, end: int) -> float:
        return end / start * 100

    #endregion
