import pandas as pd
import  matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from matplotlib.ticker import FuncFormatter

sns.set(style='dark')

def create_daily_rent_df(df):
    daily_rent_df = df.resample(rule='D', on='dteday').agg({
        "cnt": "sum"
    })
    daily_rent_df = daily_rent_df.reset_index()
    daily_rent_df.rename(columns={
        "cnt": "rent_count"
    }, inplace=True)
    
    return daily_rent_df

def create_sum_rent_bike_df(df):
    sum_rent_bike_df = df.groupby("cnt").quantity_x.sum().reset_index()
    return sum_rent_bike_df

def create_byseason_df(df):
    byseason_df = df.groupby(by="season").cnt.sum().reset_index()
    byseason_df.rename(columns={
        "cnt": "rent_count"
    }, inplace=True)
    
    return byseason_df

def create_byworkingday_df(df):
    byworkingday_df = df.groupby(by="workingday").cnt.sum().reset_index()
    byworkingday_df.rename(columns={
        "cnt": "rent_count"
    }, inplace=True)
    
    return byworkingday_df

def create_byweathersit_df(df):
    byweathersit_df = df.groupby(by="weathersit").cnt.sum().reset_index()
    byweathersit_df.rename(columns={
        "cnt": "rent_count"
    }, inplace=True)
    
    return byweathersit_df

def create_rfm_df(df):
    rfm_df = df.groupby(by="instant", as_index=False).agg({
        "dteday": "max",
        "instant": "nunique",
        "cnt": "sum"
    })
    rfm_df.columns = ["instant", "max_order_timestamp", "cnt"]

    # Pastikan konversi ke datetime
    rfm_df["max_order_timestamp"] = pd.to_datetime(rfm_df["max_order_timestamp"], errors='coerce').dt.date
    
    recent_date = df["dteday"].dt.date.max()
    rfm_df["recency"] = rfm_df["max_order_timestamp"].apply(lambda x: (recent_date - x).days)
    rfm_df.drop("max_order_timestamp", axis=1, inplace=True)
    
    return rfm_df

day_df = pd.read_csv("Dashboard/day.csv")
day_df['dteday'] = pd.to_datetime(day_df['dteday'])

datetime_columns = ["dteday"]
day_df.sort_values(by="dteday", inplace=True)
day_df.reset_index(inplace=True)

for column in datetime_columns:
    day_df[column] = pd.to_datetime(day_df[column])
    
min_date = day_df["dteday"].min()
max_date = day_df["dteday"].max()

with st.sidebar:
    # Menambahkan logo perusahaan
    st.image("https://png.pngtree.com/png-clipart/20230807/original/pngtree-vector-illustration-of-a-bicycle-rental-logo-on-a-white-background-vector-picture-image_10130396.png")
    
    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
main_df = day_df[(day_df["dteday"] >= str(start_date)) & 
                (day_df["dteday"] <= str(end_date))]

daily_rent_df = create_daily_rent_df(main_df)
byseason_df = create_byseason_df(main_df)
byworkingday_df = create_byworkingday_df(main_df)
byweathersit_df = create_byweathersit_df(main_df)
rfm_df = create_rfm_df(main_df)

# Fungsi untuk menyesuaikan format sumbu Y
def currency(x, pos):
    return '%1.0f' % x

plt.gca().yaxis.set_major_formatter(FuncFormatter(currency))

palette = sns.color_palette("pastel") 

st.header('Bike Rent Dashboard :sparkles:')
st.subheader('Daily Rent')

total_rent = daily_rent_df.rent_count.sum()
st.metric("Total rent", value=total_rent)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_rent_df["dteday"],
    daily_rent_df["rent_count"],
    marker='o', 
    linewidth=2,
    color="#90CAF9"
)
ax.tick_params(axis='y', labelsize=20)
ax.tick_params(axis='x', labelsize=15)
ax.yaxis.set_major_formatter(FuncFormatter(currency))
st.pyplot(fig)


st.subheader("Customer Demographics")

byseason_df["season"] = byseason_df.season.apply(lambda x: "springer" if x == 1 else("summer" if x == 2 else ("fall" if x == 3 else "winter")))
byworkingday_df["workingday"] = byworkingday_df.workingday.apply(lambda x: "weekend nor holiday" if x == 1 else "otherwise")
byweathersit_df["weathersit"] = byweathersit_df.weathersit.apply(lambda x: "clear" if x == 1 else("mist" if x == 2 else ("light snow" if x == 3 else "heavy rain")))

fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(x="season", y="rent_count", data=byseason_df.sort_values(by="rent_count", ascending=False), palette=palette, ax=ax)
ax.set_ylabel(None, fontsize=20)
ax.set_xlabel("Working day", fontsize=20)
ax.set_title("Number of bikes rented by season", loc="center", fontsize=30)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.yaxis.set_major_formatter(FuncFormatter(currency))
st.pyplot(fig)


fig, ax = plt.subplots(figsize=(20, 10))
sns.barplot(x="workingday", y="rent_count", data=byworkingday_df, palette=palette, ax=ax)
ax.set_ylabel(None, fontsize=20)
ax.set_xlabel("Season", fontsize=20)
ax.set_title("Number of bikes rented by Working day", loc="center", fontsize=30)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.yaxis.set_major_formatter(FuncFormatter(currency))
st.pyplot(fig)


sns.barplot(x="weathersit", y="rent_count", data=byweathersit_df, palette=palette, ax=ax)
ax.set_ylabel(None, fontsize=20)
ax.set_xlabel("weathersit", fontsize=20)
ax.set_title("Number of bikes rented by weathersit", loc="center", fontsize=30)
ax.tick_params(axis='x', labelsize=20)
ax.tick_params(axis='y', labelsize=20)
ax.yaxis.set_major_formatter(FuncFormatter(currency))
st.pyplot(fig)

st.caption('Copyright (c) ToraDk 2024')