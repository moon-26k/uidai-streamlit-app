import seaborn as sns
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image


# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="UIDAI Behaviour Analysis", layout="wide")

# ---------------- LOGO & TITLE ----------------
col1, col2 = st.columns([1, 4])

with col1:
    try:
        logo = Image.open("logo.png")
        st.image(logo, width=120)
    except:
        st.warning("logo.png not found")

with col2:
    st.title("Smart Aadhaar Update Analytics Portal")

st.divider()
# ---------------- LOAD DATA ----------------
df = pd.read_csv("uidai_final_merged.csv")

# SAFE DATE HANDLING (VERY IMPORTANT)
df['date'] = pd.to_datetime(df['date'], errors='coerce')
df = df.dropna(subset=['date'])

df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['date_only'] = df['date'].dt.strftime("%Y-%m-%d")

# ---------------- SIDEBAR NAVIGATION ----------------
menu = st.sidebar.selectbox(
    "Select Analysis",
    [
        "KPI Overview",
        "Behaviour-Based Zones",
        "Child Biometric Gap (5–17)",
        "System Downtime Detection",
        "Raise Help/Complaint"
    ]
)

# ---------------- KPI OVERVIEW ----------------
if menu == "KPI Overview":
    st.header("Key Performance Indicators")

    total_updates = df[
        [
            'age_0_5','age_5_17','age_18_greater',
            'demo_age_5_17','demo_age_17_',
            'bio_age_5_17','bio_age_17_'
        ]
    ].sum().sum()

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Aadhaar Updates", f"{int(total_updates):,}")
    c2.metric("Children (5–17)", f"{int(df['age_5_17'].sum()):,}")
    c3.metric("Adults (18+)", f"{int(df['age_18_greater'].sum()):,}")

    daily = df.groupby("date")[
        ['age_0_5','age_5_17','age_18_greater']
    ].sum()
    daily['total'] = daily.sum(axis=1)

    st.subheader("Daily Aadhaar Activity Trend")
    st.line_chart(daily['total'])
# ---------------- HEAT MAP SECTION ----------------
    st.subheader("State-wise Update Intensity (Heat Map)")

    # Data prepare karna (State vs Age Groups)
    heatmap_data = df.groupby("state")[['age_0_5', 'age_5_17', 'age_18_greater']].sum()

    # Plot banana
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax)
    
    plt.title("Update Distribution Across States")
    
    # UI par display karna
    st.pyplot(fig)
# ---------------- BEHAVIOUR-BASED ZONES ----------------
elif menu == "Behaviour-Based Zones":
    st.header("Behaviour-Based Update Zones")

    # ========== GRAPH 1 ==========
    st.subheader("Migration-driven Zones (Adults 18+)")

    f1 = st.selectbox(
        "Filter (Migration)",
        ["Overall", "Year-wise", "Month-wise", "Day-wise"],
        key="f1"
    )

    temp1 = df.copy()

    if f1 == "Year-wise":
        y = st.selectbox("Select Year", sorted(df['year'].unique()), key="y1")
        temp1 = df[df['year'] == y]

    elif f1 == "Month-wise":
        m = st.selectbox("Select Month", sorted(df['month'].unique()), key="m1")
        temp1 = df[df['month'] == m]

    elif f1 == "Day-wise":
        d = st.selectbox("Select Date", sorted(df['date_only'].unique()), key="d1")
        temp1 = df[df['date_only'] == d]

    st.bar_chart(
        temp1.groupby("state")['age_18_greater']
        .sum().sort_values(ascending=False).head(10)
    )

    # ========== GRAPH 2 ==========
    st.subheader("Marriage-driven Zones (Demographic Updates)")

    f2 = st.selectbox(
        "Filter (Marriage)",
        ["Overall", "Year-wise", "Month-wise", "Day-wise"],
        key="f2"
    )

    temp2 = df.copy()

    if f2 == "Year-wise":
        y = st.selectbox("Select Year", sorted(df['year'].unique()), key="y2")
        temp2 = df[df['year'] == y]

    elif f2 == "Month-wise":
        m = st.selectbox("Select Month", sorted(df['month'].unique()), key="m2")
        temp2 = df[df['month'] == m]

    elif f2 == "Day-wise":
        d = st.selectbox("Select Date", sorted(df['date_only'].unique()), key="d2")
        temp2 = df[df['date_only'] == d]

    st.bar_chart(
        temp2.groupby("state")['demo_age_17_']
        .sum().sort_values(ascending=False).head(10)
    )

    # ========== GRAPH 3 ==========
    st.subheader("Child-transition Zones (Age 5–17)")

    f3 = st.selectbox(
        "Filter (Child)",
        ["Overall", "Year-wise", "Month-wise", "Day-wise"],
        key="f3"
    )

    temp3 = df.copy()

    if f3 == "Year-wise":
        y = st.selectbox("Select Year", sorted(df['year'].unique()), key="y3")
        temp3 = df[df['year'] == y]

    elif f3 == "Month-wise":
        m = st.selectbox("Select Month", sorted(df['month'].unique()), key="m3")
        temp3 = df[df['month'] == m]

    elif f3 == "Day-wise":
        d = st.selectbox("Select Date", sorted(df['date_only'].unique()), key="d3")
        temp3 = df[df['date_only'] == d]

    st.bar_chart(
        temp3.groupby("state")['age_5_17']
        .sum().sort_values(ascending=False).head(10)
    )


# ---------------- CHILD BIOMETRIC GAP ----------------
elif menu == "Child Biometric Gap (5–17)":
    st.header("Child Biometric Update Gap")

    gap = df[df['bio_age_5_17'] < df['age_5_17'] * 0.5]
    summary = gap.groupby(['state','district']).size().reset_index(name="Low Update Cases")

    st.dataframe(summary.head(15))
    st.warning("Low biometric update activity detected for children aged 5–17.")

# ---------------- SYSTEM DOWNTIME ----------------
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
# ---------------- RAISE HELP / COMPLAINT ----------------
elif menu == "Raise Help/Complaint":
    st.header("⚠️ Raise Help / Complaint")

    st.info(
        "Some applicants do not have Birth Certificate or 10th Marksheet. "
        "But have supporting document like PAN Card , Driving License,etc. "
        "These type of cases mainly occur in rural areas. "
        "Such cases must be escalated to the Main UIDAI Server."
    )

    name = st.text_input("Applicant Name")
    issue = st.text_area("Describe the Issue")
    Aadhar=st.text_input("Aadhar no.")

    if st.button("📩 Raise Complaint"):
        if name == "" or issue == "":
            st.error("Please fill all fields")
        else:
            st.success("Complaint successfully sent to Main Server")

