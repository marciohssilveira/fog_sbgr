import urllib.request
import pandas as pd
import os
import time
import re

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

# Extracting the data from the columns using the info detailed in ISD data manual
def get_variable(df, column, column_list):
    """
    This function access the raw 'df' (pandas dataframe),
    uses a list with the 'column' name (str) to explore the variable column,
    receives a 'column_list' of the columns names and
    returns a dataframe with the extracted data for the variable indicated.
    """
    variable = pd.DataFrame(df[column], columns=[column])
    variable = variable[column].str.split(',', expand=True)
    variable.columns = column_list
    return variable


# Applying the get_variable() function to the columns with the variables data
wind_cols = ['direction', 'quality', 'type_code', 'speed', 'speed_quality']
wind = get_variable(sbgr_data, 'WND', wind_cols)

visibility_cols = ['visibility', 'quality', 'variability', 'quality_variability']
visibility = get_variable(sbgr_data, 'VIS', visibility_cols)

phenomenon_cols = ['phenomenon', 'quality']
phenomenon1 = get_variable(sbgr_data, 'MW1', phenomenon_cols)
phenomenon2 = get_variable(sbgr_data, 'MW2', phenomenon_cols)
phenomenon3 = get_variable(sbgr_data, 'MW3', phenomenon_cols)

sky_cover_cols = ['coverage', 'quality', 'base_height', 'base_height_quality', 'cloud_type', 'cloud_type_quality']
sky_cover1 = get_variable(sbgr_data, 'GA1', sky_cover_cols)
sky_cover2 = get_variable(sbgr_data, 'GA2', sky_cover_cols)
sky_cover3 = get_variable(sbgr_data, 'GA3', sky_cover_cols)
sky_cover4 = get_variable(sbgr_data, 'GA4', sky_cover_cols)

ceiling_cols = ['ceiling', 'quality', 'determination_code', 'cavok']
ceiling = get_variable(sbgr_data, 'CIG', ceiling_cols)

temperature_cols = ['temperature', 'quality']
temperature = get_variable(sbgr_data, 'TMP', temperature_cols)

dew_cols = ['dew', 'quality']
dew = get_variable(sbgr_data, 'DEW', dew_cols)

# Concatenating all data into a base df containing the meteorological variables
base_data = pd.concat([sbgr_data['REM'], wind[['direction', 'speed']].astype(int),
                       visibility[['visibility']].astype(int),
                       phenomenon1[['phenomenon']], phenomenon2[['phenomenon']], phenomenon3[['phenomenon']],
                       sky_cover1[['coverage']], sky_cover2[['coverage']],
                       sky_cover3[['coverage']], sky_cover4[['coverage']],
                       ceiling[['ceiling']].astype(int), ceiling[['cavok']],
                       temperature[['temperature']].astype(int),
                       dew[['dew']].astype(int)], axis=1)

# Note that there were no information on sea level pressure, which will be extracted from REM column
# Iterating over the METAR messages to extract the slp values
metar = base_data['REM']
pressure = []
for code in metar:
    slp = str(re.findall(r"Q\d.+", code))
    pressure.append(
        slp[3:7])  # the values were put into the list pressure, which will be appended to the final data frame

base_data['slp'] = pressure

base_data.columns = ['REM', 'direction', 'speed', 'visibility',
                     'phenomenon_1', 'phenomenon_2', 'phenomenon_3',
                     'coverage_1', 'coverage_2', 'coverage_3', 'coverage_4',
                     'ceiling', 'cavok', 'temperature', 'dew', 'slp']

# Exporting clean data
base_data.to_csv('./data/sbgr_raw.csv', index=False)