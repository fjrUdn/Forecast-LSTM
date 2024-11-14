'''
Program Peramalan Harga Komoditas Pangan
di Pasar Tradisional Kabupaten Banyumas
'''

import streamlit as st
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler
import config.model as model_config
import config.data as data_config
from prepare_data.hist_data import import_data
from forecast_data.forecast import make_forecast
from forecast_data.merge import merge_forecast_data
import tensorflow as tf

# set tensorflow to run only on cpu
tf.config.set_visible_devices([], 'GPU')

# data model dan histori data
MODEL_PATH = model_config.MODEL_FILE_NAME
DATA_BAWANG = data_config.DATA_BAWANG_MERAH
DATA_AYAM = data_config.DATA_DAGING_AYAM

# Load Model
loaded_model = load_model(MODEL_PATH)

# import dan scaling data
df_bawang = import_data(DATA_BAWANG)
df_ayam = import_data(DATA_AYAM)

# buat objek scaler
scale = MinMaxScaler()
df_bawang['pasar manis'] = scale.fit_transform(df_bawang[['pasar manis']])
df_bawang['pasar wage'] = scale.fit_transform(df_bawang[['pasar wage']])
df_ayam['pasar manis'] = scale.fit_transform(df_ayam[['pasar manis']])
df_ayam['pasar wage'] = scale.fit_transform(df_ayam[['pasar wage']])

st.set_page_config(layout="wide")
st.header('Model Peramalan Harga Komoditas Pangan (LSTM) :sparkles:')

# Main
def main():
    '''
    Fungsi utama dari program ini
    '''
    # tampilan awal
    st.write("Jumlah hari yang akan diprediksi : ", forecast_days)
    st.write("Forecast data....")

    # Buat forecast data
    bawang_pm = make_forecast(df_bawang,'pasar manis', loaded_model, scale, forecast_days)
    bawang_pw = make_forecast(df_bawang,'pasar wage', loaded_model, scale, forecast_days)
    ayam_pm = make_forecast(df_ayam,'pasar manis', loaded_model, scale, forecast_days)
    ayam_pw = make_forecast(df_ayam,'pasar wage', loaded_model, scale, forecast_days)

    # loading..
    st.write("Hampir selesai....")

    # merge data hasil forecast
    ayam_gab = merge_forecast_data(ayam_pm, ayam_pw)
    bawang_gab = merge_forecast_data(bawang_pm, bawang_pw)

    # Export data forecast untuk visualisasi
    try:
        ayam_gab.to_excel(f"{data_config.BASE_PATH}/data_daging_ayam.xlsx")
        bawang_gab.to_excel(f"{data_config.BASE_PATH}/data_bawang_merah.xlsx")
    except FileNotFoundError:
        print("Error: Jalur direktori tidak ditemukan."
              "Periksa kembali BASE_PATH atau lokasi penyimpanan.")
    except PermissionError:
        print("Error: Tidak memiliki izin untuk menulis ke file."
              "Tutup file jika sedang terbuka atau periksa izin direktori.")
    except IOError as e:
        print(f"Error I/O terjadi: {e}")

    # done
    st.write("Sukses")
    st.write("Silahkan klik tombol bawang merah atau "
             "daging ayam di sebelah kiri untuk melihat hasil")

if __name__ == "__main__":
    forecast_days = st.number_input("Masukkan angka sesuai kebutuhan Anda"
                             " untuk meramalkan jumlah hari", value=0)
    if forecast_days > 0:
        main()
