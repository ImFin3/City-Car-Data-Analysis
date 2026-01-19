from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Optional, Tuple

import pandas as pd


# Dezente Business-Farben (gut unterscheidbar)
BUSINESS_COLORS = [
    "#1f77b4",  # blue
    "#2ca02c",  # green
    "#ff7f0e",  # orange
    "#9467bd",  # purple
    "#17becf",  # teal
    "#7f7f7f",  # grey
    "#8c564b",  # brown
    "#bcbd22",  # olive
]


class FunnelUtility:
    """
    1) Lädt Daten
    2) Baut User-Level Tabelle für "erste Fahrt" (first ride) + Stages
    3) Erstellt Funnel Counts & Conversions (overall und segmentiert)
    """

    def __init__(self, data_dir: str = "Resources", output_dir: str = "output_html"):
        self.data_dir = self._resolve_data_dir(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # CSVs laden
        self.downloads = pd.read_csv(self.data_dir / "app_downloads.csv")
        self.signups = pd.read_csv(self.data_dir / "signups.csv")
        self.ride_requests = pd.read_csv(self.data_dir / "ride_requests.csv")
        self.transactions = pd.read_csv(self.data_dir / "transactions.csv")

        self._preprocess()

    # -----------------------
    # Setup / Preprocess
    # -----------------------
    @staticmethod
    def _resolve_data_dir(preferred: str) -> Path:
        """
        Versucht:
        - preferred (z.B. Resources/)
        - ansonsten aktueller Ordner (.)
        """
        p = Path(preferred)
        if p.exists():
            return p

        alt = Path(".")
        if (alt / "app_downloads.csv").exists():
            return alt

        return p

    def _preprocess(self) -> None:
        # Timestamps zu datetime
        self.downloads["download_ts"] = pd.to_datetime(self.downloads["download_ts"], errors="coerce")
        self.signups["signup_ts"] = pd.to_datetime(self.signups["signup_ts"], errors="coerce")

        for c in ["request_ts", "accept_ts", "pickup_ts", "dropoff_ts", "cancel_ts"]:
            self.ride_requests[c] = pd.to_datetime(self.ride_requests[c], errors="coerce")

        self.transactions["transaction_ts"] = pd.to_datetime(self.transactions["transaction_ts"], errors="coerce")

        # Normalisieren
        self.downloads["platform"] = self.downloads["platform"].str.lower().fillna("unknown")
        self.signups["age_range"] = self.signups["age_range"].fillna("Unknown")

    # -----------------------
    # Funnel Definition
    # -----------------------
    @staticmethod
    def stage_definitions() -> List[Dict[str, str]]:
        return [
            {"col": "stage_signup", "label": "Sign up"},
            {"col": "stage_request_created", "label": "First request created"},
            {"col": "stage_request_accepted", "label": "First request accepted"},
            {"col": "stage_pickup_happened", "label": "First pickup happened"},
            {"col": "stage_dropoff_happened", "label": "First dropoff happened"},
            {"col": "stage_transaction_created", "label": "First transaction created"},
            {"col": "stage_payment_approved", "label": "First payment approved"},
        ]

    def build_first_ride_user_df(self) -> pd.DataFrame:
        """
        Ergebnis: 1 Zeile pro Signup-User mit Infos zur ersten Fahrt + Stage-Flags.
        """

        # A) Signup + Platform (über session_id -> app_download_key)
        base = pd.merge(
            self.signups,
            self.downloads[["app_download_key", "platform"]],
            left_on="session_id",
            right_on="app_download_key",
            how="left",
        )

        base["platform_label"] = base["platform"].map(
            {"ios": "iOS", "android": "Android", "web": "Web"}
        ).fillna("Unknown")

        # B) Erste Fahrt pro User (kleinste request_ts)
        rr = self.ride_requests.dropna(subset=["request_ts"]).copy()
        rr = rr.sort_values(["user_id", "request_ts"], ascending=[True, True])

        first_ride = rr.groupby("user_id", as_index=False).first()[
            ["user_id", "ride_id", "request_ts", "accept_ts", "pickup_ts", "dropoff_ts", "cancel_ts"]
        ].rename(
            columns={
                "ride_id": "first_ride_id",
                "request_ts": "first_request_ts",
                "accept_ts": "first_accept_ts",
                "pickup_ts": "first_pickup_ts",
                "dropoff_ts": "first_dropoff_ts",
                "cancel_ts": "first_cancel_ts",
            }
        )

        # C) Transactions pro Ride: "Transaction created" + "Approved?"
        tx = self.transactions.copy()
        tx_agg = (
            tx.groupby("ride_id")
            .agg(
                first_transaction_ts=("transaction_ts", "min"),
                any_payment_approved=("charge_status", lambda s: (s == "Approved").any()),
            )
            .reset_index()
            .rename(columns={"ride_id": "first_ride_id"})
        )

        # D) Alles zusammenführen
        df = pd.merge(base, first_ride, on="user_id", how="left")
        df = pd.merge(df, tx_agg, on="first_ride_id", how="left")

        df["any_payment_approved"] = df["any_payment_approved"].fillna(False)

        # E) Stage Flags (0/1)
        df["stage_signup"] = 1
        df["stage_request_created"] = df["first_request_ts"].notna().astype(int)
        df["stage_request_accepted"] = df["first_accept_ts"].notna().astype(int)
        df["stage_pickup_happened"] = df["first_pickup_ts"].notna().astype(int)
        df["stage_dropoff_happened"] = df["first_dropoff_ts"].notna().astype(int)
        df["stage_transaction_created"] = df["first_transaction_ts"].notna().astype(int)
        df["stage_payment_approved"] = df["any_payment_approved"].astype(int)

        return df

    # -----------------------
    # Funnel Counts + Conversion
    # -----------------------
    def funnel_counts(self, user_df: pd.DataFrame) -> pd.DataFrame:
        stages = self.stage_definitions()
        return pd.DataFrame(
            {
                "Stage": [s["label"] for s in stages],
                "Users": [int(user_df[s["col"]].sum()) for s in stages],
            }
        )

    def funnel_counts_by_group(
        self,
        user_df: pd.DataFrame,
        group_col: str,
        group_order: Optional[List[str]] = None,
    ) -> pd.DataFrame:
        stages = self.stage_definitions()

        if group_order is None:
            groups = sorted(user_df[group_col].fillna("Unknown").astype(str).unique().tolist())
        else:
            present = set(user_df[group_col].fillna("Unknown").astype(str).unique().tolist())
            groups = [g for g in group_order if g in present]

        out = pd.DataFrame({"Stage": [s["label"] for s in stages]})

        for g in groups:
            df_g = user_df[user_df[group_col].fillna("Unknown").astype(str) == g]
            out[g] = [int(df_g[s["col"]].sum()) for s in stages]

        return out

    @staticmethod
    def percent_of_previous(counts_df: pd.DataFrame, value_cols: List[str]) -> pd.DataFrame:
        """
        Wandelt Counts in "% vom vorherigen Step" um.
        Step 1 (Sign up) = 100%.
        """
        pct = counts_df.copy()
        for col in value_cols:
            pct[col] = pct[col].astype(float)
            pct[col] = (pct[col] / pct[col].shift(1)) * 100
            pct.loc[0, col] = 100.0
        return pct

    @staticmethod
    def conversion_table(counts_df: pd.DataFrame, col: str = "Users") -> pd.DataFrame:
        """
        Tabelle: From -> To, Before, After, Conversion (%), Drop-off (%)
        """
        stages = counts_df["Stage"].tolist()
        vals = counts_df[col].astype(float).tolist()

        rows = []
        for i in range(1, len(stages)):
            before = vals[i - 1]
            after = vals[i]
            cr = (after / before * 100) if before > 0 else 0.0
            rows.append(
                {
                    "From": stages[i - 1],
                    "To": stages[i],
                    "Before": int(before),
                    "After": int(after),
                    "Conversion (%)": round(cr, 2),
                    "Drop-off (%)": round(100 - cr, 2),
                }
            )
        return pd.DataFrame(rows)

    @staticmethod
    def worst_step(conv_tbl: pd.DataFrame) -> Tuple[str, float]:
        """
        Gibt die Stage-Transition mit der niedrigsten Conversion zurück.
        """
        if conv_tbl.empty:
            return ("n/a", 0.0)
        idx = conv_tbl["Conversion (%)"].idxmin()
        row = conv_tbl.loc[idx]
        label = f'{row["From"]} → {row["To"]}'
        return (label, float(row["Conversion (%)"]))

    # -----------------------
    # Simple Surge Helpers
    # -----------------------
    def requests_per_hour(self) -> pd.DataFrame:
        df = self.ride_requests.dropna(subset=["request_ts"]).copy()
        df["hour"] = df["request_ts"].dt.hour
        out = df.groupby("hour").size().reindex(range(24), fill_value=0).reset_index(name="requests")
        return out

    def requests_weekday_hour(self) -> pd.DataFrame:
        df = self.ride_requests.dropna(subset=["request_ts"]).copy()
        df["weekday"] = df["request_ts"].dt.day_name()
        df["hour"] = df["request_ts"].dt.hour
        weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        df["weekday"] = pd.Categorical(df["weekday"], categories=weekday_order, ordered=True)
        return df.groupby(["weekday", "hour"]).size().reset_index(name="requests")
