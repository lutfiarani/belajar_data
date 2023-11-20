import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import plotly.express as px
from babel.numbers import format_currency

sns.set(style='dark')

st.set_page_config(
    page_title="Bike Sharing Chart",
    page_icon="🧊",
    # layout="wide",
    initial_sidebar_state="expanded"
)


day_df = pd.read_csv(r'dashboard/day.csv')
hour_df = pd.read_csv(r'dashboard/hour.csv')
day_df.head()

datetime_columns = ["dteday"]
 
for column in datetime_columns:
  day_df[column] = pd.to_datetime(day_df[column])

day_df["mnth_full"] = day_df["dteday"].dt.month_name()

monthly_share_df = day_df.query("yr==1").groupby(by=["mnth","mnth_full"]).cnt.sum()
monthly_share_df = monthly_share_df.reset_index()
monthly_share_df.rename(columns={
    "mnth": "bulan_angka",
    "mnth_full": "bulan",
    "cnt": "sharing_count"
}, inplace=True)
monthly_share_df.head(12)

##------------------------------------------------------chart 1---------------------------------------------------------
st.subheader('Number of Sharing Bike')
col1, col2 = st.columns(2)
with col1:
  total_orders = monthly_share_df["sharing_count"].sum()
  st.metric("Total Sharing in 2012", value=f'{total_orders:,}')
 
with col2:
    max_month = monthly_share_df["bulan"].max()
    st.metric("Month with Highest Sharing in 2012", value=max_month)
 
fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    monthly_share_df["bulan"],
    monthly_share_df["sharing_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
 
st.pyplot(fig)

# --------------------------------------------chart 2-------------------------------------------------------------
st.subheader("Best & Worst Month Sharing in 2012")
 
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(24, 6))
col1, col2 = st.columns(2)
with col1:
  month_lowesr=t = monthly_share_df["bulan"].min()
  st.metric("Month with Lowest Bike Sharing in 2012", value=month_lowesr)
 
 
colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
colors_worst = ["#E51515", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
 
sns.barplot(x="sharing_count", y="bulan", data=monthly_share_df.sort_values(by="sharing_count", ascending=False).head(3), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Months with the Highest Bike Sharing", loc="center", fontsize=15)
ax[0].tick_params(axis ='y', labelsize=12)
 
sns.barplot(x="sharing_count", y="bulan", data=monthly_share_df.sort_values(by="sharing_count", ascending=True).head(3), palette=colors_worst, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.set_label_position("right")
ax[1].yaxis.tick_right()
ax[1].set_title("Months with the Lowest Bike Sharing", loc="center", fontsize=15)
ax[1].tick_params(axis='y', labelsize=12)
 
st.pyplot(fig)

#-------------------------------------------chart 3, average rental by hour on holidays-------------------------------------------
st.subheader("Average Bicycle Rental Every Hour on Holidays")


hour_data_df = hour_df.query("yr==1 & holiday==1").groupby(["yr", "hr"]).agg({
    "casual": "mean",
    "registered":"mean",
    "cnt": "mean"
}).sort_values(by="cnt",ascending=False)

hour_data_df = hour_data_df.reset_index()

hour_data_df.rename(columns={
    "hr": "hour",
    "cnt": "qty"
}, inplace=True)

hour_holiday_df = hour_df.query("yr==1 & holiday==1").agg({
    "casual": "mean",
    "registered":"mean",
    "cnt": "mean"
})
fig, ax = plt.subplots(figsize=(20, 10))

col1, col2 = st.columns(2)
with col1:
  total_orders = hour_df["cnt"].mean()
  st.metric("Average Bike Sharing on Holidays in 2012", value=int(total_orders))

with col2:
   highest_hour = hour_df["hr"].max()
   st.metric("Highest Time on Holidays in 2012", value=highest_hour)

colors_ = ["#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4", "#72BCD4"]
sns.barplot(
    x="hour", 
    y="qty",
    data=hour_data_df.sort_values(by="qty", ascending=False),
    palette=colors_,
    ax=ax
)

ax.set_title("Average Bicycle Rental Every Hour on Holidays", loc="center", fontsize=30)
ax.set_ylabel("total")
ax.set_xlabel("hour")
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
st.pyplot(fig)


# --------------------------------Chart 4 - RFI for Sharing Bike, because sharing bike is not have monitary, so I use Intensity---------------------------------------------------
# menghitung Recency, Frequency, intensity, dan score RFI

day_df['dteday'] = pd.to_datetime(day_df['dteday'])
latest_date = day_df['dteday'].max()
day_df['recency'] = (latest_date - day_df['dteday']).dt.days

frequency_bins = pd.qcut(day_df['cnt'], q=[0, 0.25, 0.5, 0.75, 1], labels=False, duplicates='drop')
day_df['frequency'] = frequency_bins

average_intensity = day_df['cnt'].mean()
day_df['intensity'] = pd.cut(day_df['cnt'], bins=[0, average_intensity, float('inf')], labels=[0, 1])

# Convert tipe data categorikal menjadi integer
day_df['frequency'] = day_df['frequency'].astype(int)
day_df['intensity'] = day_df['intensity'].astype(int)

# menghitung RFI score
day_df['rfi_score'] = day_df['recency'] + day_df['frequency'] + day_df['intensity']


st.subheader("Bike Sharing Based on RFI Parameters")


col1, col2, col3 = st.columns(3)
 
with col1:
    avg_recency = round(day_df['recency'].mean())
    st.metric("Average Recency (days)", value=avg_recency)
 
with col2:
    avg_frequency = round(day_df['frequency'].mean(),2)
    st.metric("Average Frequency", value=avg_frequency)
 
with col3:
    avg_intensity = round(day_df['intensity'].mean(),2)
    st.metric("Average Intensity", value=avg_frequency)
 
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(35, 15))
colors = ["#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9", "#90CAF9"]
df = day_df
fig = px.scatter(
    df.query("yr==1"),
    x="recency",
    y="frequency",
    color="rfi_score",
    hover_name="rfi_score",
    log_x=True,
    size_max=60,
)

st.plotly_chart(fig, theme="streamlit", use_container_width=True)

