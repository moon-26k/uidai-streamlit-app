import streamlit as st
import pandas as pd

#logo adding
from PIL import Image
logo = Image.open("logo.png")
st.image(logo, width=200)
col1, col2 = st.columns([1,4])

with col1:
    st.image("logo.png", width=120)

with col2:
    st.title("Behaviour-Based Aadhaar Update Analysis System")



st.set_page_config(page_title="UIDAI Behaviour Analysis", layout="wide")

# Load merged data
df = pd.read_csv("uidai_final_merged.csv")
df['date'] = pd.to_datetime(df['date'], errors='coerce')

st.title("Behaviour-Based Aadhaar Update Analysis System")

# Sidebar
menu = st.sidebar.selectbox(
    "Select Analysis",
    [
        "KPI Overview",
        "Behaviour-Based Zones",
        "Child Biometric Gap (5–17)",
        "System Downtime Detection"
    ]
)

# KPI OVERVIEW 
if menu == "KPI Overview":
    st.header("Key Performance Indicators")

    total_updates = df[
        [
            'age_0_5','age_5_17','age_18_greater',
            'demo_age_5_17','demo_age_17_',
            'bio_age_5_17','bio_age_17_'
        ]
    ].sum().sum()

    children = df['age_5_17'].sum()
    adults = df['age_18_greater'].sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Aadhaar Updates", f"{int(total_updates):,}")
    c2.metric("Children (5–17)", f"{int(children):,}")
    c3.metric("Adults (18+)", f"{int(adults):,}")

    daily = df.groupby("date")[
        ['age_0_5','age_5_17','age_18_greater']
    ].sum()
    daily['total'] = daily.sum(axis=1)

    st.subheader("Daily Aadhaar Activity Trend")
    st.line_chart(daily['total'])

#  BEHAVIOUR ZONES
elif menu == "Behaviour-Based Zones":
    st.header("Behaviour-Based Update Zones")

    st.subheader("Migration-driven Zones (Adults 18+)")
    st.bar_chart(df.groupby("state")['age_18_greater'].sum().sort_values(ascending=False).head(10))

    st.subheader("Marriage-driven Zones (Demographic Updates)")
    st.bar_chart(df.groupby("state")['demo_age_17_'].sum().sort_values(ascending=False).head(10))

    st.subheader("Child-transition Zones (Age 5–17)")
    st.bar_chart(df.groupby("state")['age_5_17'].sum().sort_values(ascending=False).head(10))

#  CHILD BIOMETRIC GAP 
elif menu == "Child Biometric Gap (5–17)":
    st.header("Child Biometric Update Gap")

    gap = df[df['bio_age_5_17'] < df['age_5_17'] * 0.5]
    summary = gap.groupby(['state','district']).size().reset_index(name="Low Update Cases")

    st.dataframe(summary.head(15))
    st.warning("Low biometric update activity detected for children aged 5–17. School-based enrolment drives recommended.")

#  SYSTEM DOWNTIME 
elif menu == "System Downtime Detection":
    st.header("System Downtime & Anomaly Detection")

    daily = df.groupby("date")[
        ['age_0_5','age_5_17','age_18_greater']
    ].sum()
    daily['total'] = daily.sum(axis=1)

    st.line_chart(daily['total'])

    threshold = daily['total'].mean() * 0.3
    if daily['total'].min() < threshold:
        st.error("Sudden drop detected — possible server or connectivity issue.")
#help notification box alert
st.markdown("## ⚠️ Special Case – Raise Help Request")

st.warning(
    """
    **Issue Description:**

    There are cases where an Aadhaar holder has incorrect details (for example, Date of Birth) 
    mentioned in their Aadhaar record. The applicant is asked for documents such as a Birth 
    Certificate or 10th Marksheet, which many people—especially in rural areas—do not possess.

    However, the applicant may have other valid supporting documents such as:
    - PAN Card
    - Voter ID
    - Other Government-issued IDs

    Such cases cannot be resolved at the local centre level.
    """
)

if st.button("📩 Raise Issue to Main Server"):
    st.success(
        "Help request successfully sent to the Main Server. "
        "The case will be reviewed and an appropriate solution will be provided."
    )
