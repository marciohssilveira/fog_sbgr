import pandas as pd

import urllib.request
from urllib.error import HTTPError
import pandas as pd
from pandas.io import parsers
import os
import math
import re
import numpy as np
from pathlib import Path
import warnings
import datetime
import zipfile
import shutil

warnings.filterwarnings('ignore')


class GetInmetData:
    """
    Contain functions to gather data from ISD,
    organise the files in directories and
    extract information from them
    """

    def __init__(self):
        self.station = 'SAO PAULO - MIRANTE'
        self.end_year = datetime.datetime.today().year - 1
        self.start_year = datetime.datetime.today().year - 10

    def download_inmet_data(self):
        """
        Creates the link to download ISD files as well as the directories to put the files
        """
        print(f'Downloading {self.station} data')
        for year in range(self.start_year, self.end_year, 1):
            url = f'https://portal.inmet.gov.br/uploads/dadoshistoricos/{year}.zip'
            Path(f'data/raw/inmet/{self.station}/zip/').mkdir(parents=True, exist_ok=True)
            zip_filename = f'data/raw/inmet/{self.station}/zip/{year}.zip'
            # Only download if file does not exist
            if not os.path.exists(zip_filename):
                try:
                    urllib.request.urlretrieve(url, zip_filename)
                except urllib.error.HTTPError as exception:
                    print(f'Unfortunately there is no {year} data available'
                          f' for {self.station}: Error {exception.code}')
                    continue
            Path(
                f'data/raw/inmet/{self.station}/csv/').mkdir(parents=True, exist_ok=True)
            csv_filepath = f'data/raw/inmet/{self.station}/csv/'
            # # Only unzip if file does not exist
            # if not os.path.exists(_filename):
            with zipfile.ZipFile(zip_filename, 'r') as zip:
                files = zip.namelist()
                regex = re.compile(f'^(?=.*({self.station}))(?!.*box).*$')
                for file in files:
                    if regex.match(file):
                        # Extract a single file from zip
                        # zip.extract(file, csv_filepath)
                        # open the entry so we can copy it
                        member = zip.open(file)

                        with open(os.path.join(csv_filepath, os.path.basename(file)), 'wb') as outfile:
                            # copy it directly to the output directory,
                            # without creating the intermediate directory
                            shutil.copyfileobj(member, outfile)

        print('Download complete\nProcessing files')
        data = self.process_files()
        data.to_csv(f'data/interim/{self.station}_inmet_data.csv', index=False)
        print('Done!')

    def process_files(self):
        """
        Takes all the raw downloaded files and unites them into one file
        """
        csv_path = f'data/raw/inmet/{self.station}/csv'
        csv_list = os.listdir(path=csv_path)

        grouped = []
        for file in sorted(csv_list):
            # DATE column is used as index
            # try:
            inmet_data = pd.read_csv(f'{csv_path}/{file}',
                                     sep=';',
                                     skiprows=8,
                                     encoding='latin_1')
            inmet_data = inmet_data.drop(inmet_data.columns[-1], axis=1)
            inmet_data = inmet_data[['DATA (YYYY-MM-DD)', 'HORA (UTC)',
                                     'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)', 'RADIACAO GLOBAL (KJ/m²)']]
            inmet_data.columns = ['date', 'time',
                                  'precipitation', 'radiation']
            inmet_data['DATE'] = inmet_data['date'].astype(
                str) + ' ' + inmet_data['time'].apply(lambda x: str(x).zfill(4))
            inmet_data = inmet_data[[
                'DATE', 'precipitation', 'radiation']]
            # except:
            #     f'{file} data for {self.station} could not be processed.'
            #     continue
            grouped.append(inmet_data)
        # Stores all data data into a dataframe
        data = pd.concat(grouped, sort=False)
        data = data.apply(lambda x: x.str.replace(',', '.').replace('-9999', 0))
        return data
