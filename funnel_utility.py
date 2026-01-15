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
    def get_funnel_analysis_dataframe(self) -> pd.DataFrame:
        f_a = self.full_funnel_analysis()   # f_a => funnel_analysis

        df = pd.DataFrame({
            "Conversion From To": ["Download to Sign Ups", "Sign Ups to unique User Ride Requests", "Ride Requests to Transactions", "Transactions to Approved Transactions"],
            "Before": [f_a[0].before, f_a[1].before, f_a[2].before, f_a[3].before],
            "After": [f_a[0].after, f_a[1].after, f_a[2].after, f_a[3].after],
            "Conversion Rate": [f_a[0].conversion_rate, f_a[1].conversion_rate, f_a[2].conversion_rate, f_a[3].conversion_rate]
        })

        return df

    def full_funnel_analysis(self) -> tuple[ConversionStruct, ConversionStruct, ConversionStruct, ConversionStruct]:

        return (self.get_conversion_rate_download_to_signups(), self.get_conversion_rate_signups_to_unique_user_ride_requests(),
                self.get_conversion_rate_ride_requests_to_transactions(), self.get_conversion_rate_transactions_to_approved_transactions())

    def get_conversion_rate_download_to_signups(self) -> ConversionStruct:
        return self.get_conversion_rate_struct(self.get_download_count(), self.get_signup_count())

    def get_conversion_rate_signups_to_unique_user_ride_requests(self) -> ConversionStruct:
        return self.get_conversion_rate_struct(self.get_signup_count(), self.get_unique_user_ride_request_count())

    def get_conversion_rate_ride_requests_to_transactions(self) -> ConversionStruct:
        return self.get_conversion_rate_struct(self.get_ride_requests_count(), self.get_transaction_count())

    def get_conversion_rate_transactions_to_approved_transactions(self) -> ConversionStruct:
        return self.get_conversion_rate_struct(self.get_transaction_count(), self.get_approved_transactions_count())
    #endregion

    #region Platform Analysis
    def get_platform_analysis_dataframe(self) -> pd.DataFrame:
        p_d_c = self.get_total_user_downloads_per_platform()        # p_d_c => platform_download_count
        p_s_c = self.get_total_user_signups_per_platform()          # p_s_c => platform_signup_count
        m_m = self.get_median_money_spent_per_ride_per_platform()     # m_m => median_money

        df = pd.DataFrame({
            "Platform": ["iOS", "Android", "Web"],
            "Download Count": [p_d_c.ios, p_d_c.android, p_d_c.web],
            "Signed Up User Count": [p_s_c.ios, p_s_c.android, p_s_c.web],
            "Download to Sign Up Conversion Rate": [self.get_conversion_rate(p_d_c.ios, p_s_c.ios), self.get_conversion_rate(p_d_c.android, p_s_c.android), self.get_conversion_rate(p_d_c.web, p_s_c.web)],
            "Median Money spent per Ride in $": [m_m.ios, m_m.android, m_m.web],
        })

        return df

    def get_total_user_downloads_per_platform(self) -> UserPerPlatform:
        return self.UserPerPlatform(self.get_total_user_download_count_ios(), self.get_total_user_download_count_android(), self.get_total_user_download_count_web())

    def get_total_user_download_count_ios(self) -> int:
        return self.downloads_df[self.downloads_df["platform"] == "ios"]["app_download_key"].count()

    def get_total_user_download_count_android(self) -> int:
        return self.downloads_df[self.downloads_df["platform"] == "android"]["app_download_key"].count()

    def get_total_user_download_count_web(self) -> int:
        return self.downloads_df[self.downloads_df["platform"] == "web"]["app_download_key"].count()

    def get_total_user_signups_per_platform(self) -> UserPerPlatform:
        return self.UserPerPlatform(self.get_total_user_signups_count_ios(), self.get_total_user_signups_count_android(), self.get_total_user_signups_count_web())

    def get_total_user_signups_count_ios(self) -> int:
        merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id", how="inner")
        return merged[merged["platform"] == "ios"]["app_download_key"].count()

    def get_total_user_signups_count_android(self) -> int:
        merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id",how="inner")
        return merged[merged["platform"] == "android"]["app_download_key"].count()

    def get_total_user_signups_count_web(self) -> int:
        merged = pd.merge(self.downloads_df, self.signups_df, left_on="app_download_key", right_on="session_id",how="inner")
        return merged[merged["platform"] == "web"]["app_download_key"].count()

    def get_median_money_spent_per_ride_per_platform(self) -> MoneySpentPerPlatform:
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


    #endregion

    #region Age Group Analysis
    def get_age_group_analysis_dataframe(self) -> pd.DataFrame:
        s_a_d_c = self.get_signup_age_group_distribution_count()  # s_a_d_c => signup_age_distribution_count
        a_rr_a_d_c = self.get_approved_ride_request_age_group_distribution_count()   # a_rr_a_d_c => approved_riderequest_age_distribution_count
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

    def get_signup_age_group_distribution_count(self) -> AgeGroupDistribution:
        age_distribution = self.AgeGroupDistribution(0,0,0,0,0)
        age_distribution.age_18_to_24 = int(self.signups_df[self.signups_df["age_range"] == "18-24"]["user_id"].count())
        age_distribution.age_25_to_34 = int(self.signups_df[self.signups_df["age_range"] == "25-34"]["user_id"].count())
        age_distribution.age_35_to_44 = int(self.signups_df[self.signups_df["age_range"] == "35-44"]["user_id"].count())
        age_distribution.age_45_to_54 = int(self.signups_df[self.signups_df["age_range"] == "45-54"]["user_id"].count())
        age_distribution.unknown = int(self.signups_df[self.signups_df["age_range"] == "Unknown"]["user_id"].count())

        return age_distribution

    def get_approved_ride_request_age_group_distribution_count(self) -> AgeGroupDistribution:
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

    #endregion

    #region Surge Pricing Analysis
    def get_surge_pricing_analysis_dataframe(self) -> pd.DataFrame:
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

    #endregion

    #region Helper Functions
    def get_download_count(self) -> int:
        return self.downloads_df.shape[0]

    def get_signup_count(self) -> int:
        return self.signups_df.shape[0]

    def get_ride_requests_count(self) -> int:
        return self.ride_requests_df.shape[0]

    def get_unique_user_ride_request_count(self) -> int:
        return self.ride_requests_df["user_id"].nunique()

    def get_transaction_count(self) -> int:
        return self.transactions_df.shape[0]

    def get_approved_transactions_count(self) -> int:
        return int(self.transactions_df[self.transactions_df["charge_status"] == "Approved"]["transaction_id"].count())

    @staticmethod
    def get_conversion_rate(start: int, end: int) -> float:
        return end / start

    def get_conversion_rate_struct(self, start: int, end: int) -> ConversionStruct:
        return self.ConversionStruct(start, end, self.get_conversion_rate(start, end))

    #endregion