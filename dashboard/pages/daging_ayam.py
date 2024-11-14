import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from streamlit_folium import st_folium
from babel.numbers import format_currency
import folium
from streamlit_folium import folium_static
import base64
import config.data as data_config
from io import BytesIO
sns.set(style='dark')

st.set_page_config(layout="wide")
# Load data
def load_and_prepare_data(file_path, date_columns):
    # Memuat data dari file Excel
    df = pd.read_excel(file_path)
    df.sort_values(by=date_columns, inplace=True)
    df.reset_index(inplace=True)
    for column in date_columns:
        df[column] = pd.to_datetime(df[column])
    
    return df

df_pm = load_and_prepare_data(f'{data_config.BASE_PATH}/data_daging_ayam_pm.xlsx', ["Date"])
df_pw = load_and_prepare_data(f'{data_config.BASE_PATH}/data_daging_ayam_pw.xlsx', ["Date"])
df_gab = load_and_prepare_data(f'{data_config.BASE_PATH}/data_daging_ayam.xlsx', ["Date"])

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
                (df_pm["Date"] <= str(end_date))]
df1.loc[:, 'Date'] = pd.to_datetime(df1['Date'])

df_pm.set_index('Date', inplace=True)

df2 = df_pw[(df_pw["Date"] >= str(start_date)) &
                (df_pw["Date"] <= str(end_date))]
df2.loc[:, 'Date'] = pd.to_datetime(df2['Date'])

df_pw.set_index('Date', inplace=True)

df3 = df_gab[(df_gab["Date"] >= str(start_date)) &
                (df_gab["Date"] <= str(end_date))]
df3.loc[:, 'Date'] = pd.to_datetime(df3['Date'])

df_gab.set_index('Date', inplace=True)

# Header 
st.header('Forecast Harga Daging Ayam :sparkles:')

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

image_base64 = base64.b64encode(image_stream.getvalue()).decode("utf-8")
html = f'<img src="data:image/png;base64,{image_base64}">'
max_width = 1000
popup_manis = folium.Popup(html, max_width=max_width)

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

image_base64 = base64.b64encode(image_stream.getvalue()).decode("utf-8")
html = f'<img src="data:image/png;base64,{image_base64}">'
max_width = 1000
popup_wage = folium.Popup(html, max_width=max_width)

# Create Folium map
m = folium.Map(location=[-7.4205726027999, 109.24285399533692], zoom_start=15, width='100%', height='100%')
folium.Marker([-7.417745006891739, 109.22726059533683], popup=popup_manis, icon=folium.Icon(color='blue', icon='location', prefix='fa-solid fa-shop'), tooltip=str('Pasar Manis')).add_to(m)
folium.Marker([-7.426524254740998, 109.24983460883072], popup=popup_wage, icon=folium.Icon(color='blue', icon='location', prefix='fa-solid fa-shop'), tooltip=str('Pasar Wage')).add_to(m)

with st.expander("Find market on maps", expanded=True):
    st.subheader('Map')
    st_folium(m, width=2000, height=450)

# st_folium(m, width=2000, height=450)
# st.pyplot(fig)

# st.subheader('List Harga Pasar Manis')
# # tabel bawah
# df1['Date'] = pd.to_datetime(df1['Date'])
# # Mengonversi kolom 'Date' menjadi format string tanpa waktu
# df1['Date'] = df1['Date'].dt.strftime('%Y-%m-%d')

# # Mengonversi kolom Currency menjadi format mata uang Rupiah
# df1['Historical Data'] = df1['Historical Data'].apply(lambda x: locale.currency(x, grouping=True) if pd.notnull(x) else x)
# df1['Forecast'] = df1['Forecast'].apply(lambda x: locale.currency(x, grouping=True)if pd.notnull(x) else x)

# st.dataframe(df1.iloc[:,1:], use_container_width=True, hide_index=True)

# st.subheader('List Harga Pasar Wage')
# # tabel bawah
# df2['Date'] = pd.to_datetime(df2['Date'])
# # Mengonversi kolom 'Date' menjadi format string tanpa waktu
# df2['Date'] = df2['Date'].dt.strftime('%Y-%m-%d')

# # Mengonversi kolom Currency menjadi format mata uang Rupiah
# df2['Historical Data'] = df2['Historical Data'].apply(lambda x: locale.currency(x, grouping=True) if pd.notnull(x) else x)
# df2['Forecast'] = df2['Forecast'].apply(lambda x: locale.currency(x, grouping=True)if pd.notnull(x) else x)

# st.dataframe(df2.iloc[:,1:], use_container_width=True, hide_index=True)
##-----------------------------------------
st.subheader('List Harga')
# tabel bawah
df3['Date'] = pd.to_datetime(df3['Date'])
# Mengonversi kolom 'Date' menjadi format string tanpa waktu
df3['Date'] = df3['Date'].dt.strftime('%Y-%m-%d')

# Mengonversi kolom Currency menjadi format mata uang Rupiah
def format_rupiah(x):
    if pd.notnull(x):
        return 'Rp {:,.2f}'.format(x).replace(',', '.')
    else:
        return x

df3['Pasar Manis'] = df3['Pasar Manis'].apply(format_rupiah)
df3['Pasar Wage'] = df3['Pasar Wage'].apply(format_rupiah)
df3 = df3.reset_index(drop=True)

st.dataframe(df3.iloc[:,2:], use_container_width=True)
