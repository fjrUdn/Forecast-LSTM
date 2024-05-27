import pandas as pd
import numpy as np
import streamlit as st
from keras.models import load_model
from sklearn.preprocessing import MinMaxScaler

st.set_page_config(layout="wide")
st.header('Model Peramalan Harga Komoditas Pangan (LSTM) :sparkles:')

# Load Model 
loaded_model = load_model("dashboard/bestModel_lstm.h5")

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

# Make Prediction
def forecast_data(df, column_name, loaded_model, scale, forecast_steps=93):
    look_back=1
    historical_data_pm = df[column_name].iloc[0:]

    X_forecast = []
    y_forecast = []

    for i in range(len(historical_data_pm.values.reshape(len(historical_data_pm), 1)) - look_back):
        a = historical_data_pm.values.reshape(len(historical_data_pm), 1)[i:(i + look_back), 0]
        X_forecast.append(a)
        y_forecast.append(historical_data_pm.values.reshape(len(historical_data_pm), 1)[i + look_back, 0])

    X_forecast = np.array(X_forecast)
    y_forecast = np.array(y_forecast)

    X_forecast = X_forecast.reshape(X_forecast.shape[0], 1, X_forecast.shape[1])
    pred_forecast = loaded_model.predict(X_forecast[-forecast_steps:])  # Use last X values to forecast future steps

    # Append forecasted values to historical data
    forecasted_values = []
    for i in range(forecast_steps):
        next_input = np.append(X_forecast[-1, 0, 1:], pred_forecast[i])  # Assuming input sequence length is 5
        next_input = next_input.reshape(1, 1, look_back)  # Reshape for LSTM model input

        # Predict the next value
        next_pred = loaded_model.predict(next_input)
        forecasted_values.append(next_pred[0])

    last_date = df.index[-1]  # Ambil tanggal terakhir dalam data
    future_index = pd.date_range(start=last_date + pd.DateOffset(days=1), periods=forecast_steps, freq='D')
    forecast_df = pd.DataFrame({'Forecast': np.array(forecasted_values).flatten()}, index=future_index)

    historical_data_pm_denormalized = scale.inverse_transform(historical_data_pm.values.reshape(-1, 1)).flatten()

    forecasted_values_denormalized = scale.inverse_transform(forecast_df['Forecast'].values.reshape(-1, 1)).flatten()

    historical_data_pm_denorm_df = pd.DataFrame({'Historical Data': historical_data_pm_denormalized}, index=historical_data_pm.index)
    forecasted_values_denorm_pm_df = pd.DataFrame({'Forecast': forecasted_values_denormalized}, index=forecast_df.index)

    combined_denorm_df = pd.concat([historical_data_pm_denorm_df, forecasted_values_denorm_pm_df])

    return combined_denorm_df

# Save Data Prediction
def merge_forecast_data(combined_denorm_df_pm, combined_denorm_df_pw):
    # Convert to DataFrames
    data_df_pm = pd.DataFrame(combined_denorm_df_pm)
    data_df_pw = pd.DataFrame(combined_denorm_df_pw)

    # Add "Pasar Manis" column by filling values from "Historical Data" and "Forecast"
    data_df_pm['Pasar Manis'] = data_df_pm['Historical Data'].combine_first(data_df_pm['Forecast'])

    # Add "Pasar Wage" column by filling values from "Historical Data" and "Forecast"
    data_df_pw['Pasar Wage'] = data_df_pw['Historical Data'].combine_first(data_df_pw['Forecast'])

    # Create "Keterangan" column
    data_df_pm['Keterangan'] = ['Historical Data' if pd.notna(x) else 'Forecast' for x in data_df_pm['Historical Data']]

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

if __name__ == "__main__":
    number = st.number_input("Insert a number", value=0)
    if number > 0:
        main()
