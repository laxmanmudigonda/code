# ui/app.py

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import streamlit as st
from datetime import datetime
import random
import string

from src.agent1_predictor import predict_risk_tier
from agents.agent2_predictor import predict_conversion
from agents.agent3_predictor import analyze_premium
from agents.agent4_router import route_decision

st.set_page_config(
    page_title="QuoteIQ - Insurance Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ----------------------------
# Helpers
# ----------------------------

def random_ref():
    return "#" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ----------------------------
# Session State
# ----------------------------

if "results" not in st.session_state:
    st.session_state.results = None

if "quote" not in st.session_state:
    st.session_state.quote = None

if "quote_ref" not in st.session_state:
    st.session_state.quote_ref = random_ref()

# ----------------------------
# Header
# ----------------------------

st.title("🚗 QuoteIQ")
st.caption("Insurance Analytics Platform")

tab1, tab2 = st.tabs(["Pipeline Overview", "Analyze Quote"])

# =================================================
# TAB 1
# =================================================

with tab1:

    st.header("4-Agent Insurance Pipeline")

    col1,col2,col3,col4 = st.columns(4)

    col1.info("Agent 1\n\nRisk Profiler")
    col2.info("Agent 2\n\nConversion Predictor")
    col3.info("Agent 3\n\nPremium Advisor")
    col4.info("Agent 4\n\nDecision Router")

# =================================================
# TAB 2
# =================================================

with tab2:

    with st.sidebar:

        st.header("New Quote")

        driver_age = st.number_input("Age", 16, 90, 30)
        driving_exp = st.number_input("Driving Experience", 0, 60, 5)

        prev_accidents = st.number_input("Accidents",0,10,0)
        prev_citations = st.number_input("Citations",0,10,0)

        veh_usage = st.selectbox(
            "Vehicle Usage",
            ["Commute","Pleasure","Business"]
        )

        coverage = st.selectbox(
            "Coverage",
            ["Liability","Collision","Comprehensive"]
        )

        agent_type = st.selectbox(
            "Agent Type",
            ["EA","IA","Online"]
        )

        region = st.selectbox(
            "Region",
            ["North","South","East","West"]
        )

        re_quote = st.selectbox("Re Quote",["No","Yes"])

        quoted_premium = st.number_input(
            "Quoted Premium",
            100.0,
            5000.0,
            700.0
        )

        hh_drivers = st.number_input(
            "Household Drivers",
            1,
            5,
            2
        )

        sal_range = st.selectbox(
            "Salary Range",
            ["<50K","50K-70K","70K-100K",">100K"]
        )

        analyze = st.button("⚡ Analyze Quote")

    # ------------------------------------------------

    if analyze:

        quote = {
    "Prev_Accidents": prev_accidents,
    "Prev_Citations": prev_citations,
    "Driving_Exp": driving_exp,
    "Driver_Age": driver_age,

    "Annual_Miles": 12000,   # ✅ FIX (model requires this)
    "Veh_Usage": veh_usage,

    "Re_Quote": re_quote,
    "Q_Valid_DT": 5,

    "Coverage": coverage,
    "Agent_Type": agent_type,
    "Region": region,

    "Sal_Range": sal_range,
    "HH_Drivers": hh_drivers,

    "Quoted_Premium": quoted_premium
}

        st.session_state.quote = quote

        risk_tier,risk_probs = predict_risk_tier(quote)

        conv_output = predict_conversion(quote,risk_tier)

        premium_output = analyze_premium(
            quote,
            risk_tier,
            conv_output
        )

        decision_output = route_decision(
            risk_tier,
            conv_output,
            premium_output,
            agent_type,
            region
        )

        st.session_state.results = {

            "risk_tier":risk_tier,
            "risk_probs":risk_probs,
            "conv_output":conv_output,
            "premium_output":premium_output,
            "decision_output":decision_output
        }

    # ------------------------------------------------

    if st.session_state.results:

        res = st.session_state.results
        quote = st.session_state.quote

        st.success(f"Decision: {res['decision_output']['decision']}")

        st.write("Quote Ref:",st.session_state.quote_ref)

        bind_yes = res["conv_output"]["conversion_probability"] / 100
        bind_no = 1-bind_yes

        col1,col2,col3 = st.columns(3)

        # -----------------------
        # Risk
        # -----------------------

        with col1:

            st.metric(
                "Risk Tier",
                res["risk_tier"]
            )

        # -----------------------
        # Conversion
        # -----------------------

        with col2:

            st.metric(
                "Bind Probability",
                f"{bind_yes*100:.1f}%"
            )

        # -----------------------
        # Premium
        # -----------------------

        with col3:

            rec = res["premium_output"]["recommended_premium"]

            st.metric(
                "Recommended Premium",
                f"${rec}",
                delta=f"${rec-quote['Quoted_Premium']}"
            )

        st.divider()

        st.subheader("Quote Snapshot")

        c1,c2,c3,c4 = st.columns(4)

        c1.write("Driver Age",quote["Driver_Age"])
        c2.write("Experience",quote["Driving_Exp"])
        c3.write("Accidents",quote["Prev_Accidents"])
        c4.write("Coverage",quote["Coverage"])

    else:

        st.info("Enter quote details and click Analyze Quote.")