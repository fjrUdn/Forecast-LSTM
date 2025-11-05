'''
Make forecast with LSTM Model
'''
import pandas as pd
import numpy as np

def make_forecast(df, column_name, loaded_model, scale, forecast_steps=93):
    look_back=1
    historical_data = df[column_name].values
    
    # Pre-reshape historical data once
    historical_data_reshaped = historical_data.reshape(-1, 1)

    x_forecast = []
    y_forecast = []

    for i in range(len(historical_data_reshaped) - look_back):
        x_forecast.append(historical_data_reshaped[i:(i + look_back), 0])
        y_forecast.append(historical_data_reshaped[i + look_back, 0])

    x_forecast = np.array(x_forecast)
    y_forecast = np.array(y_forecast)

    x_forecast = x_forecast.reshape(x_forecast.shape[0], 1, x_forecast.shape[1])
    
    # Batch predict instead of predicting forecast_steps separately
    pred_forecast = loaded_model.predict(x_forecast[-forecast_steps:], verbose=0)

    # Iteratively forecast future values
    forecasted_values = []
    last_input = x_forecast[-1:, :, :]  # Keep the last sequence
    
    for i in range(forecast_steps):
        # Predict the next value
        next_pred = loaded_model.predict(last_input, verbose=0)
        forecasted_values.append(next_pred[0])
        
        # Update input for next iteration
        last_input = next_pred.reshape(1, 1, look_back)

    last_date = df.index[-1]  # Ambil tanggal terakhir dalam data
    future_index = pd.date_range(
        start=last_date + pd.DateOffset(days=1),
        periods=forecast_steps,
        freq='D'
    )
    
    # Flatten and reshape once
    forecasted_values_flat = np.array(forecasted_values).flatten()
    forecast_df = pd.DataFrame({
        'Forecast': forecasted_values_flat
        }, index=future_index)

    # Batch inverse transform
    forecasted_values_denormalized = scale.inverse_transform(
        forecasted_values_flat.reshape(-1, 1)
    ).flatten()

    historical_data_denormalized = scale.inverse_transform(
        historical_data_reshaped
    ).flatten()

    historical_data_denorm_df = pd.DataFrame({
        'Historical Data': historical_data_denormalized
    }, index=historical_data.index)

    forecasted_values_denorm_pm_df = pd.DataFrame({
        'Forecast': forecasted_values_denormalized
    }, index=forecast_df.index)

    combined_denorm_df = pd.concat([historical_data_denorm_df, forecasted_values_denorm_pm_df])

    return combined_denorm_df
