"""
Vendor Recommendation & Event Planning AI – Streamlit UI (v2)
───────────────────────────────────────────────────────────────
Two tools in one app:
    ① Vendor Recommendation (same as before)
    ② Event Cost Estimation & Negotiation Bot

Run locally:
    pip install streamlit pandas numpy
    streamlit run streamlit_app.py
No external APIs – everything stays on your machine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import streamlit as st

# ──────────────────────────────── Config ────────────────────────────────────── #
DATA_FILE = Path(__file__).with_name("vendor_data.csv")
TOP_N = 3  # number of vendors to show

# Base service prices (INR). Adjust freely.
SERVICE_DB: Dict[str, Dict[str, float | str]] = {
    "Venue": {"base": 700, "unit": "per_guest"},
    "Catering": {"base": 1200, "unit": "per_guest"},
    "Decor": {"base": 300, "unit": "per_guest"},
    "Photography": {"base": 45000, "unit": "fixed"},
    "Entertainment / DJ": {"base": 35000, "unit": "fixed"},
    "AV Equipment": {"base": 250, "unit": "per_guest"},
    "Security": {"base": 90, "unit": "per_guest"},
    "Transport": {"base": 150, "unit": "per_guest"},
}
TIERS = {
    "Basic": 1.0,
    "Standard": 1.15,
    "Premium": 1.35,
}

# ───────────────────────── Utilities (shared) ───────────────────────────────── #

def load_data(path: Path) -> pd.DataFrame:
    """Read vendor CSV; show Streamlit error if missing."""
    if not path.exists():
        st.error(
            f"🛑 Required file '{path.name}' not found. Place it beside this script or upload it via the sidebar."
        )
        return pd.DataFrame()
    return pd.read_csv(path)


def score_vendors(df: pd.DataFrame, event_type: str, budget: int, city: str) -> pd.DataFrame:
    """Filter & rank vendors via simple heuristic scoring."""
    if df.empty:
        return df

    event_type, city = event_type.lower(), city.lower()

    ok_type = df["event_types"].str.lower().str.contains(event_type)
    ok_budget = (df.min_budget <= budget) & (df.max_budget >= budget)

    cand = df[ok_type & ok_budget].copy()
    if cand.empty:
        return cand

    cand["loc_bonus"] = (cand.city.str.lower() == city).astype(int)
    mid = (cand.min_budget + cand.max_budget) / 2
    cand["budget_bonus"] = 1 - abs(mid - budget) / mid
    cand["score"] = cand.rating * 2 + cand.loc_bonus * 1.5 + cand.budget_bonus

    return cand.sort_values("score", ascending=False)


def checklist(event_type: str) -> List[Tuple[str, str]]:
    timelines = {
        "wedding": [
            ("T‑12 mo", "Set guest list & budget"),
            ("T‑10 mo", "Book venue & caterer"),
            ("T‑8 mo", "Secure décor & photo"),
            ("T‑6 mo", "Send save‑the‑dates"),
            ("T‑3 mo", "Finalize menu & music"),
            ("T‑1 mo", "Confirm all vendors"),
            ("Day 0", "Celebrate!"),
        ],
        "birthday": [
            ("T‑4 wk", "Pick theme & invites"),
            ("T‑3 wk", "Book cake & décor"),
            ("T‑1 wk", "Confirm RSVPs & food"),
            ("Day 0", "Party time!"),
        ],
        "conference": [
            ("T‑6 mo", "Define goals & budget"),
            ("T‑5 mo", "Secure venue & sponsors"),
            ("T‑3 mo", "Open registrations"),
            ("T‑1 mo", "Finalize agenda"),
            ("Day 0", "Run the show"),
        ],
    }
    return timelines.get(event_type.lower(), [("T‑4 wk", "Draft basic timeline")])

# ──────────────────── Cost Estimation & Negotiation Logic ──────────────────── #

def estimate_cost(services: List[str], guests: int, tier_factor: float) -> Tuple[pd.DataFrame, float]:
    """Return cost breakdown & total."""
    rows = []
    for srv in services:
        details = SERVICE_DB[srv]
        base = details["base"]
        if details["unit"] == "per_guest":
            cost = base * guests * tier_factor
        else:  # fixed
            cost = base * tier_factor
        rows.append((srv, details["unit"], cost))
    df = pd.DataFrame(rows, columns=["Service", "Unit", "Cost (₹)"]).sort_values("Service")
    total = df["Cost (₹)"].sum()
    return df, total


def negotiate(estimate_total: float, vendor_quote: float) -> Tuple[str, float]:
    """Return recommendation text & counter‑offer."""
    buffer_low = 0.10  # 10 % profit margin for vendor is okay
    buffer_mid = 0.25  # up to 25 % markup is negotiable

    if vendor_quote <= estimate_total * (1 + buffer_low):
        return "👍 The quote is reasonable. Accept it.", vendor_quote
    elif vendor_quote <= estimate_total * (1 + buffer_mid):
        counter = round(estimate_total * (1 + buffer_low / 2), -2)  # round to nearest 100
        return (
            f"🤝 Fair but can be better. Counter at ₹{counter:,.0f} (splits the difference).",
            counter,
        )
    else:
        counter = round(estimate_total * (1 + buffer_low), -2)
        return (
            f"🧐 Quote is steep! Start with a firm counter of ₹{counter:,.0f}. Be ready to walk away.",
            counter,
        )

# ─────────────────────────────── App Layout ────────────────────────────────── #

st.set_page_config(page_title="Vendor Planner AI", page_icon="🎉", layout="wide")

st.title("🎉 Vendor Recommendation & Event Planning AI")

# Load vendor data (or allow upload)
if not DATA_FILE.exists():
    uploaded = st.file_uploader("Upload vendor_data.csv", type="csv")
    vendors_df = pd.read_csv(uploaded) if uploaded is not None else pd.DataFrame()
else:
    vendors_df = load_data(DATA_FILE)

# Tabs: Recommendation | Estimation
rec_tab, cost_tab = st.tabs(["🏆 Vendor Recommendation", "💰 Estimation & Negotiation"])

# ───────────────────────── Vendor Recommendation Tab ───────────────────────── #
with rec_tab:
    if vendors_df.empty:
        st.warning("Add / upload vendor_data.csv to use this feature.")
    else:
        # Build dropdown lists
        all_events = sorted({evt.strip() for col in vendors_df.event_types for evt in col.split(",")})
        etype = st.selectbox("Event type", all_events, index=0)
        max_budget = int(vendors_df.max_budget.max())
        budget = st.slider("Budget (INR)", 10000, max_budget, step=5000, value=60000)
        city = st.selectbox("City", sorted(vendors_df.city.unique()), index=0)

        if st.button("Recommend Vendors"):
            ranked = score_vendors(vendors_df, etype, budget, city)
            if ranked.empty:
                st.warning("No vendors fit those filters. Try tweaking budget or city.")
            else:
                st.subheader(
                    f"Top {TOP_N} vendors for a {etype.title()} in {city.title()} (₹{budget:,} budget)"
                )
                st.dataframe(
                    ranked.head(TOP_N)[
                        [
                            "name",
                            "city",
                            "rating",
                            "min_budget",
                            "max_budget",
                            "contact",
                        ]
                    ]
                    .rename(
                        columns={
                            "name": "Vendor",
                            "city": "City",
                            "rating": "⭐ Rating",
                            "min_budget": "Min Budget",
                            "max_budget": "Max Budget",
                            "contact": "Contact",
                        }
                    )
                    .style.format({"Min Budget": "₹{:,}", "Max Budget": "₹{:,}"}),
                    use_container_width=True,
                )

                st.subheader("🗓️ Mini‑checklist")
                for when, task in checklist(etype):
                    st.markdown(f"**{when}** — {task}")

# ────────────────────── Cost Estimation & Negotiation Tab ──────────────────── #
with cost_tab:
    st.subheader("1️⃣ Estimate Your Event Cost")

    col1, col2 = st.columns(2)
    with col1:
        guests = st.number_input("Number of guests", min_value=10, max_value=5000, value=150, step=10)
    with col2:
        tier_name = st.radio("Service tier", list(TIERS.keys()), index=1, horizontal=True)
    tier_factor = TIERS[tier_name]

    services = st.multiselect("Select services required", list(SERVICE_DB.keys()), default=list(SERVICE_DB.keys())[:4])

    if st.button("Estimate Cost") and services:
        breakdown_df, total_est = estimate_cost(services, guests, tier_factor)
        st.success(f"Estimated total cost: **₹{int(total_est):,}** (Tier: {tier_name})")
        st.dataframe(breakdown_df.style.format({"Cost (₹)": "₹{:,}"}), use_container_width=True)

        st.subheader("2️⃣ Negotiate With Vendor")
        vendor_quote = st.number_input(
            "Enter vendor's quoted total (INR)", min_value=0, value=int(total_est * 1.25), step=1000
        )
        if st.button("Negotiate"):
            advice, counter_offer = negotiate(total_est, vendor_quote)
            st.info(advice)
            if counter_offer != vendor_quote:
                st.write(f"💡 Suggested counter‑offer: **₹{int(counter_offer):,}**")
    elif not services:
        st.info("Choose at least one service to estimate cost.")
