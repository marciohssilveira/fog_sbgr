import urllib.request
import pandas as pd
import os
import time

# Fetching the files from NOAA Integrated Surface Database (ISD)
# License: https://www.ncdc.noaa.gov/isd/data-access
# Documentation: https://www.ncei.noaa.gov/data/global-hourly/doc/isd-format-document.pdf

print('Downloading files...')
start_time = time.time()
for year in range(2009, 2020, 1):
    url = f'https://www.ncei.noaa.gov/data/global-hourly/access/{year}/83075099999.csv'
    print(f'Downloading {year} files from {url}')
    filename = f'./data/raw/sbgr_{year}.csv'
    urllib.request.urlretrieve(url, filename)
print(f'Files downloaded in {time.time() - start_time}s')


# Using pandas to concatenate all raw csv into only one file
CSV = os.listdir(path='data/raw/')
PATH = 'data/raw/'
grouped = []
for file in sorted(CSV):
    # DATE column was used as index
    df = pd.read_csv(PATH + file, index_col='DATE')
    grouped.append(df)
# stores all data data into a dataframe
sbgr_data = pd.concat(grouped, sort=False)
# setting index to datetime format
sbgr_data.index = pd.to_datetime(sbgr_data.index)

sbgr_data.to_csv('./data/sbgr_raw.csv')