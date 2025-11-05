'''
Visualisasi dari hasil peramalan harga yang dihasilkan model
'''
import base64
from io import BytesIO
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_folium import st_folium
import folium
import config.data as data_config
sns.set(style='dark')

st.set_page_config(layout="wide")

@st.cache_data
def load_and_prepare_data(file_path, date_columns):
    '''Memuat data dari file Excel dengan caching'''
    df = pd.read_excel(file_path)
    df.sort_values(by=date_columns, inplace=True)
    df.reset_index(inplace=True)
    for column in date_columns:
        df[column] = pd.to_datetime(df[column])

    return df

# Load data (cached)
df_pm = load_and_prepare_data(f'{data_config.BASE_PATH}/data_bawang_merah_pm.xlsx', ["Date"])
df_pw = load_and_prepare_data(f'{data_config.BASE_PATH}/data_bawang_merah_pw.xlsx', ["Date"])
df_gab = load_and_prepare_data(f'{data_config.BASE_PATH}/data_bawang_merah.xlsx', ["Date"])

min_date = df_gab["Date"].min()
max_date = df_gab["Date"].max()

# sidebar sebelah kiri
with st.sidebar:
    # Menambahkan logo perusahaan
    #st.image("https://github.com/dicodingacademy/assets/raw/main/logo.png")

    # Mengambil start_date & end_date dari date_input
    start_date, end_date = st.date_input(
        label='Rentang Waktu',min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

df1 = df_pm[(df_pm["Date"] >= str(start_date)) &
                (df_pm["Date"] <= str(end_date))].copy()

df_pm.set_index('Date', inplace=True)

df2 = df_pw[(df_pw["Date"] >= str(start_date)) &
                (df_pw["Date"] <= str(end_date))].copy()

df_pw.set_index('Date', inplace=True)

df3 = df_gab[(df_gab["Date"] >= str(start_date)) &
                (df_gab["Date"] <= str(end_date))].copy()

df_gab.set_index('Date', inplace=True)

# Header
st.header('Forecast Harga Bawang Merah :sparkles:')

#Filter Forecast data
forecast_data = df_gab[df_gab['Keterangan'] == 'Forecast']

# Plot Forecast Marker
fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(
    forecast_data.index,
    forecast_data['Pasar Manis'],
    color='red',
    label='Forecast',
    linestyle='--',
    #linewidth=2
)
ax.set_title('Forecast Pasar Manis', fontsize=15)
ax.tick_params(axis='y', labelsize=7)
ax.tick_params(axis='x', labelsize=7, rotation=17)

image_stream = BytesIO()
plt.savefig(image_stream, format='png')
plt.close()

IMAGE_BASE64 = base64.b64encode(image_stream.getvalue()).decode("utf-8")
HTML = f'<img src="data:image/png;base64,{IMAGE_BASE64}">'
MAX_WIDTH = 1000
POPUP_MANIS = folium.Popup(HTML, max_width=MAX_WIDTH)

# Plot Forecast Marker
fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(
    forecast_data.index,
    forecast_data['Pasar Wage'],
    color='red',
    label='Forecast',
    linestyle='--',
    #linewidth=2
)
ax.set_title('Forecast Pasar Wage', fontsize=15)
ax.tick_params(axis='y', labelsize=7)
ax.tick_params(axis='x', labelsize=7, rotation=17)

image_stream = BytesIO()
plt.savefig(image_stream, format='png')
plt.close()

IMAGE_BASE64 = base64.b64encode(image_stream.getvalue()).decode("utf-8")
HTML = f'<img src="data:image/png;base64,{IMAGE_BASE64}">'
MAX_WIDTH = 1000
POPUP_WAGE = folium.Popup(HTML, max_width=MAX_WIDTH)

# Create Folium map
m = folium.Map(
    location=[-7.4205726027999, 109.24285399533692],
    zoom_start=15,
    width='100%',
    height='100%'
)

folium.Marker(
    [-7.417745006891739, 109.22726059533683],
    popup=POPUP_MANIS,
    icon=folium.Icon(color='blue', icon='location', prefix='fa-solid fa-shop'),
    tooltip=str('Pasar Manis')
).add_to(m)

folium.Marker(
    [-7.426524254740998, 109.24983460883072],
    popup=POPUP_WAGE,
    icon=folium.Icon(color='blue', icon='location', prefix='fa-solid fa-shop'),
    tooltip=str('Pasar Wage')
).add_to(m)

with st.expander("Find market on maps", expanded=True):
    st.subheader('Map')
    st_folium(m, width=2000, height=450)

##-----------------------------------------
st.subheader('List Harga')
# tabel bawah
# Date is already in datetime format, just format as string
df3['Date'] = df3['Date'].dt.strftime('%Y-%m-%d')

def format_rupiah(x):
    '''Mengonversi kolom Currency menjadi format mata uang Rupiah'''
    if pd.notnull(x):
        return f"Rp {x:,.2f}".replace(',', '.')

    return x

df3['Pasar Manis'] = df3['Pasar Manis'].apply(format_rupiah)
df3['Pasar Wage'] = df3['Pasar Wage'].apply(format_rupiah)

st.dataframe(df3.iloc[:,2:], use_container_width=True)
