# Import modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import re

# All files used were download using a python script and stored in ./data/raw
# Then they were concatenated into one file at ./data/sbgr_raw.csv

# Importing the csv into a Pandas DataFrame
data = pd.read_csv('./data/sbgr_raw.csv')


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
wind = get_variable(data, 'WND', wind_cols)

visibility_cols = ['visibility', 'quality', 'variability', 'quality_variability']
visibility = get_variable(data, 'VIS', visibility_cols)

phenomenon_cols = ['phenomenon', 'quality']
phenomenon1 = get_variable(data, 'MW1', phenomenon_cols)
phenomenon2 = get_variable(data, 'MW2', phenomenon_cols)
phenomenon3 = get_variable(data, 'MW3', phenomenon_cols)

sky_cover_cols = ['coverage', 'quality', 'base_height', 'base_height_quality', 'cloud_type', 'cloud_type_quality']
sky_cover1 = get_variable(data, 'GA1', sky_cover_cols)
sky_cover2 = get_variable(data, 'GA2', sky_cover_cols)
sky_cover3 = get_variable(data, 'GA3', sky_cover_cols)
sky_cover4 = get_variable(data, 'GA4', sky_cover_cols)

ceiling_cols = ['ceiling', 'quality', 'determination_code', 'cavok']
ceiling = get_variable(data, 'CIG', ceiling_cols)

temperature_cols = ['temperature', 'quality']
temperature = get_variable(data, 'TMP', temperature_cols)

dew_cols = ['dew', 'quality']
dew = get_variable(data, 'DEW', dew_cols)

# Concatenating all data into a base df containing the meteorological variables
base_data = pd.concat([data[['DATE', 'REM']], wind[['direction', 'speed']].astype(int),
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

base_data.columns = ['DATE', 'REM', 'direction', 'speed', 'visibility',
                     'phenomenon_1', 'phenomenon_2', 'phenomenon_3',
                     'coverage_1', 'coverage_2', 'coverage_3', 'coverage_4',
                     'ceiling', 'cavok', 'temperature', 'dew', 'slp']

# Now let's proceed with some corrections in the data...

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
codes = pd.read_csv('data/wx_codes.csv', sep=';', index_col='Code')
codes.index = codes.index.map("{:02}".format)
codes_dict = codes['Phenomenon'].to_dict()
phenomena = base_data.filter(like='phenomenon')
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

# Exporting clean data
base_data.to_csv('./data/sbgr_clean.csv', index=False)
