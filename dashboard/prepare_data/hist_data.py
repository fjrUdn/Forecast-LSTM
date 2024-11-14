'''
History data bawang merah dan daging ayam
'''
import pandas as pd

def import_data(path):
    '''
    method untuk import data dan mengubah tipe data tanggal
    '''
    df = pd.read_csv(path)
    df['tanggal'] = pd.to_datetime(df['tanggal'])
    df = df.set_index('tanggal')

    return df
