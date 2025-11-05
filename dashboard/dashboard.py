import pandas as pd
import numpy as np
import streamlit as st
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(layout="wide")
st.header('Model Peramalan Harga Komoditas Pangan (LSTM) :sparkles:')

@st.cache_resource
def load_lstm_model():
    '''Cache the model loading to avoid reloading on every run'''
    return load_model("dashboard/bestModel_lstm.h5")

@st.cache_data
def load_and_prepare_data():
    '''Cache data loading and preparation'''
    # Prepare Data
    df = pd.read_csv('dashboard/data_daging_ayam_clean23.csv')
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df = df.set_index('tanggal')

    df1 = pd.read_csv('dashboard/data_bawang_merah_clean23.csv')
    df1['tanggal'] = pd.to_datetime(df1['tanggal'])
    df1 = df1.set_index('tanggal')

    scale = MinMaxScaler()
    df['pasar manis'] = scale.fit_transform(df[['pasar manis']])
    df['pasar wage'] = scale.fit_transform(df[['pasar wage']])
    df1['pasar manis'] = scale.fit_transform(df1[['pasar manis']])
    df1['pasar wage'] = scale.fit_transform(df1[['pasar wage']])

    min_val = scale.data_min_
    max_val = scale.data_max_
    
    return df, df1, scale, min_val, max_val

# Load Model (cached)
loaded_model = load_lstm_model()

# Load and prepare data (cached)
df, df1, scale, min_val, max_val = load_and_prepare_data()

# Make Prediction
def forecast_data(df, column_name, loaded_model, scale, forecast_steps=93):
    look_back=1
    historical_data_pm = df[column_name].values
    
    # Pre-reshape historical data once
    historical_data_reshaped = historical_data_pm.reshape(-1, 1)

    X_forecast = []
    y_forecast = []

    for i in range(len(historical_data_reshaped) - look_back):
        X_forecast.append(historical_data_reshaped[i:(i + look_back), 0])
        y_forecast.append(historical_data_reshaped[i + look_back, 0])

    X_forecast = np.array(X_forecast)
    y_forecast = np.array(y_forecast)

    X_forecast = X_forecast.reshape(X_forecast.shape[0], 1, X_forecast.shape[1])
    
    # Iteratively forecast future values
    forecasted_values = []
    last_input = X_forecast[-1:, :, :]  # Keep the last sequence
    
    for i in range(forecast_steps):
        # Predict the next value (suppress verbose output)
        next_pred = loaded_model.predict(last_input, verbose=0)
        forecasted_values.append(next_pred[0])
        
        # Update input for next iteration
        last_input = next_pred.reshape(1, 1, look_back)

    last_date = df.index[-1]  # Ambil tanggal terakhir dalam data
    future_index = pd.date_range(start=last_date + pd.DateOffset(days=1), periods=forecast_steps, freq='D')
    
    forecasted_values_flat = np.array(forecasted_values).flatten()
    forecast_df = pd.DataFrame({'Forecast': forecasted_values_flat}, index=future_index)

    historical_data_pm_denormalized = scale.inverse_transform(historical_data_reshaped).flatten()
    forecasted_values_denormalized = scale.inverse_transform(forecasted_values_flat.reshape(-1, 1)).flatten()

    historical_data_pm_denorm_df = pd.DataFrame({'Historical Data': historical_data_pm_denormalized}, index=df[column_name].index)
    forecasted_values_denorm_pm_df = pd.DataFrame({'Forecast': forecasted_values_denormalized}, index=forecast_df.index)

    combined_denorm_df = pd.concat([historical_data_pm_denorm_df, forecasted_values_denorm_pm_df])

    return combined_denorm_df

# Save Data Prediction
def merge_forecast_data(combined_denorm_df_pm, combined_denorm_df_pw):
    # DataFrames are already passed in, no need to convert
    data_df_pm = combined_denorm_df_pm if isinstance(combined_denorm_df_pm, pd.DataFrame) else pd.DataFrame(combined_denorm_df_pm)
    data_df_pw = combined_denorm_df_pw if isinstance(combined_denorm_df_pw, pd.DataFrame) else pd.DataFrame(combined_denorm_df_pw)

    # Add "Pasar Manis" column by filling values from "Historical Data" and "Forecast"
    data_df_pm['Pasar Manis'] = data_df_pm['Historical Data'].combine_first(data_df_pm['Forecast'])

    # Add "Pasar Wage" column by filling values from "Historical Data" and "Forecast"
    data_df_pw['Pasar Wage'] = data_df_pw['Historical Data'].combine_first(data_df_pw['Forecast'])

    # Create "Keterangan" column using vectorized operation
    data_df_pm['Keterangan'] = data_df_pm['Historical Data'].notna().map({True: 'Historical Data', False: 'Forecast'})

    # Merge DataFrames based on index
    final_df = pd.DataFrame({
        'Date': data_df_pm.index,
        'Pasar Manis': data_df_pm['Pasar Manis'],
        'Pasar Wage': data_df_pw['Pasar Wage'],
        'Keterangan': data_df_pm['Keterangan']
    })

    # Reset index
    final_df = final_df.reset_index(drop=True)
    
    return final_df

# Main
def main():
    st.write("Jumlah hari yang akan diprediksi : ", number)
    st.write("Forecast data....")
    ayam_pm = forecast_data(df,'pasar manis', loaded_model, scale, number) 
    ayam_pw = forecast_data(df,'pasar wage', loaded_model, scale, number)
    bawang_pm = forecast_data(df1,'pasar manis', loaded_model, scale, number)
    st.write("Hampir selesai....")
    bawang_pw = forecast_data(df1,'pasar wage', loaded_model, scale, number)
    ayam_gab = merge_forecast_data(ayam_pm, ayam_pw)
    bawang_gab = merge_forecast_data(bawang_pm, bawang_pw)
    ayam_gab.to_excel("dashboard/data_daging_ayam.xlsx")
    bawang_gab.to_excel("dashboard/data_bawang_merah.xlsx")
    st.write("Sukses")
    st.write("Silahkan klik tombol bawang merah atau daging ayam di sebelah kiri untuk melihat hasil")    
if __name__ == "__main__":
    number = st.number_input("Masukkan angka sesuai kebutuhan Anda untuk meramalkan jumlah hari", value=0)
    if number > 0:
        main()
