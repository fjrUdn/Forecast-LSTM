'''
Make forecast with LSTM Model
'''
import pandas as pd
import numpy as np

def make_forecast(df, column_name, loaded_model, scale, forecast_steps=93):
    look_back=1
    historical_data = df[column_name].iloc[0:]
    # # Fit scaler pada kolom tertentu jika belum dilakukan
    # scale.fit(df[[column_name]])

    x_forecast = []
    y_forecast = []

    for i in range(len(historical_data.values.reshape(len(historical_data), 1)) - look_back):
        a = historical_data.values.reshape(len(historical_data), 1)[i:(i + look_back), 0]
        x_forecast.append(a)
        y_forecast.append(historical_data.values.reshape(len(historical_data), 1)[i + look_back, 0])

    x_forecast = np.array(x_forecast)
    y_forecast = np.array(y_forecast)

    x_forecast = x_forecast.reshape(x_forecast.shape[0], 1, x_forecast.shape[1])
    # Use last X values to forecast future steps
    pred_forecast = loaded_model.predict(x_forecast[-forecast_steps:])

    # Append forecasted values to historical data
    forecasted_values = []
    for i in range(forecast_steps):
        # Assuming input sequence length is 5
        next_input = np.append(x_forecast[-1, 0, 1:], pred_forecast[i])
        # Reshape for LSTM model input
        next_input = next_input.reshape(1, 1, look_back)

        # Predict the next value
        next_pred = loaded_model.predict(next_input)
        forecasted_values.append(next_pred[0])

    last_date = df.index[-1]  # Ambil tanggal terakhir dalam data
    future_index = pd.date_range(
        start=last_date + pd.DateOffset(days=1),
        periods=forecast_steps,
        freq='D'
    )
    forecast_df = pd.DataFrame({
        'Forecast': np.array(forecasted_values).flatten()
        }, index=future_index)

    forecasted_values_denormalized = scale.inverse_transform(
        forecast_df['Forecast'].values.reshape(-1, 1)
    ).flatten()

    historical_data_denormalized = scale.inverse_transform(
        historical_data.values.reshape(-1, 1)
    ).flatten()

    historical_data_denorm_df = pd.DataFrame({
        'Historical Data': historical_data_denormalized
    }, index=historical_data.index)

    forecasted_values_denorm_pm_df = pd.DataFrame({
        'Forecast': forecasted_values_denormalized
    }, index=forecast_df.index)

    combined_denorm_df = pd.concat([historical_data_denorm_df, forecasted_values_denorm_pm_df])

    return combined_denorm_df
