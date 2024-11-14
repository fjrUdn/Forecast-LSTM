'''
Save Data Prediction
'''
import pandas as pd

def merge_forecast_data(forecast_pm, forecast_pw):
    '''
    Method ini digunakan untuk menggabungkan data hasil peramalan
    '''
    # Convert to DataFrames
    data_df_pm = pd.DataFrame(forecast_pm)
    data_df_pw = pd.DataFrame(forecast_pw)

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
