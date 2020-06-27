import urllib.request
import pandas as pd
import os
import time
import math
import re
import numpy as np

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

# Some corrections in the data...

# Wind
# According with the manual, wind direction as 999 can be missing or variable wind.
# It can be calm too, as seen by the data (comparing them to METAR)...
# When the wind is calm, let's set them to 0
base_data['direction'][(base_data['direction'] == 999) & (base_data['speed'] == 0)] = 0
base_data['speed'][(base_data['direction'] == 999) & (base_data['speed'] == 0)] = 0

# When the wind is variable, let's set only the direction to 0
base_data['direction'][(base_data['direction'] == 999) & (base_data['speed'] != 0)] = 0

# According to the manual, speed_rate seen as 9999 means it is missing.
# Or it is just a typo at the METAR. Let's just delete them...
base_data['speed'][base_data['speed'] == 9999] = 0

# Visibility
# The manual says visibility values of 999999 means they are missing.
# If CAVOK is Y, it means the visibility is greater than 10000 meters...
# Also, values of visibility above 10,000m must not be considered as restrictive to the operations,
# thus, let's just set them as unlimited...
base_data['visibility'][(base_data['visibility'] > 9001) & (base_data['visibility'] < 999998)] = 10000
base_data['visibility'][base_data['visibility'] == 999999] = 10000

# Wx
# A csv file with all phenomenon codes was created using the ISD manual
# Then they were put in a dict and then replaced in the rows
codes = pd.read_csv('./data/wx_codes.csv', sep=';', index_col='Code')
codes.index = codes.index.map("{:02}".format)
codes_dict = codes['Phenomenon'].to_dict()
phenomena = base_data.filter(like='phenomenon').fillna('00').astype(int).astype(str).replace('0', 'None')
base_data[phenomena.columns] = phenomena.replace(codes_dict)


# Ceiling
# According to the manual, ceiling regarded as 99999 means it's missing (from the METAR) and 22000 means unlimited...
# BUT... "ceiling values above 1600m (5000ft) are not considered ceiling" Lets just make them NaN...
base_data['ceiling'] = base_data['ceiling'].astype(int)
base_data['ceiling'][(base_data['ceiling'] > 1599)] = np.nan

# Temperature
# The manual says temperature/dew values above 9999 means they are missing...
base_data['temperature'][base_data['temperature'] == 9999] = np.nan
base_data['dew'][base_data['dew'] == 9999] = np.nan

# Sea Level Pressure
# As we extracted the slp values from METAR message using regex,
# some typos corrupted the data extracted. Let's just ignore them...
dirty = base_data['slp'].tolist()
dirty = [str(i) for i in dirty]


clean = []
for value in dirty:
    if not value.isdigit():
        clean.append(9999)
    else:
        clean.append(value)

clean = [float(x) for x in clean]
base_data['slp'] = clean

# Also, values of pressure greater than 1050 and lesser than 900 are absurd.
# They are probably typos as well so let's get rid of them...
base_data['slp'][(base_data['slp'] > 1050) | (base_data['slp'] < 900)] = np.nan

# Correcting data for standard units

# Wind direction is in degrees, which is fine...

# Wind Speed is in meters per second and scaled by 10, let's downscale them and convert to knots...
base_data['speed'] = base_data['speed'] * 0.194384

# Ceiling is in meters, let's set them to feet
base_data['ceiling'] = round(base_data['ceiling'] * 3.28084)

# Visibility is in meters, which is fine...

# Temperature and dew are scaled by 10, let's downscale them...
base_data['temperature'] = base_data['temperature'] / 10
base_data['dew'] = base_data['dew'] / 10

# Pressure is in Hectopascal, which is fine...


# Broad view of the data
# print(base_data.describe())

# Dropping unused columns
base_data = base_data.drop(['REM', 'cavok'], axis=1).round(0)


# Create a column for relative humidity
def calculate_rh(temperature, dew):
    """
    Receives air temperature (t) and dew point (d) and returns relative humidity
    RH = 100*(EXP((17.625*TD)/(243.04+TD))/EXP((17.625*T)/(243.04+T)))
    """
    rh_list = []
    for t, d in zip(temperature, dew):
        rh = 100 * ((math.exp((17.625 * d) / (243.04 + d))) / (math.exp((17.625 * t) / (243.04 + t))))
        rh_list.append(rh)
    return rh_list


base_data['rh'] = calculate_rh(base_data['temperature'], base_data['dew'])

base_data.to_csv('./data/sbgr_data.csv')