"""Loading and transformation of SenseDoc data into (zipped) CSV files

Creates one csv per participant/wave/sensor, file name includes INTERACT_ID. 
The result is a folder per sensor, per city, each with a csv file per 
participant with data and INTERACT_ID.
Resulting CSV files are stored in the <sensedoc> subfolder.
--
USAGE: load.py [TARGET_ROOT_FOLDER]

If TARGET_ROOT_FOLDER not provided, will default to test data folder.
"""

import os
import sys
import logging
import re
import pandas as pd
from sqlalchemy import create_engine
import platform
from datetime import datetime
import pytz
from tempfile import NamedTemporaryFile


# Define city_id and wave_id
cities = {'mtl': 'montreal', 
          'skt': 'saskatoon', 
          'van': 'vancouver', 
          'vic': 'victoria'}
waves = [1, 2, 3]

# Define base folder when not provided on the cmd line
root_data_folder = 'data\interact_test_data'


def single_load_transform(interact_id, src_sdb, dst_dir, start_date=None, end_date=None):
    """
    Processing of a single participant's SD data.
    Load GPS and AXL data separately from sdb file, filter records to keep only
    measurements within start and end dates, then save each of the two streams 
    to a CSV file with interact_id, timestamp followed by axl/gps measurements.

    Parameters:
    -----------
    - interact_id: Participant unique ID
    - src_sdb: Path to the SDB file, that contains the AXL and GPS data
    - dst_dir: Path where newly created CSV files (one for GPS, one for AXL) will
        be saved 
    - start_date (Optional): if provided, only records on or after the start date will
        be saved to the CSV file; format YYYY-MM-DD
    - end_date (Optional): if provided, only records on or before the end date will
        be saved to the CSV file; format YYYY-MM-DD

    Notes:
    ------
    - Dates (in YYYY-MM-DD format) are converted to UTC timestamps, based on the city of participation.
        Start date -> start date at 00:00:00 local time
        End date -> end date at 23:59:59 local time
    """
    # A bit of checking going-on here:
    # TODO

    # Convert dates to proper UTC timestamp
    tz_lut = {'1': 'America/Vancouver', # Victoria
              '2': 'America/Vancouver', # Vancouver'
              '3': 'America/Regina', # Saskatoon
              '4': 'America/Toronto'} # Montreal
    target_tz = pytz.timezone(tz_lut[str(interact_id)[:1]]) # First number of iid codes the city

    if start_date is not None:
        start_date = datetime.strptime(f'{start_date} 00:00:00', '%Y-%m-%d %H:%M:%S')
        start_date = target_tz.localize(start_date)
        start_date = start_date.astimezone(pytz.utc)

    if end_date is not None:
        end_date = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
        end_date = target_tz.localize(end_date)
        end_date = end_date.astimezone(pytz.utc)

    # Process GPS
    try:
        gps_file = _single_load_transform_gps(interact_id, src_sdb, dst_dir, start_date, end_date)
        logging.info(f'Participant # {interact_id}: GPS elite file -> {os.path.basename(gps_file)}')
    except Exception as e:
        logging.error(f'Participant # {interact_id}: Unable to process GPS ({e})')


def _single_load_transform_gps(interact_id, src_sdb, dst_dir, start_date, end_date) -> str:
    """ Process the GPS data stream 
    
    Returns the path to the newly created CSV file"""

    # TODO: check if several sdb with _rtcX have been created, deal with the loading in that case

    # Load GPS data from sdb file
    if platform.system() == 'Windows':
        # Connection string varies between Linux/Max and Windows
        sdb_con = create_engine(f'sqlite:///{src_sdb}') 
    else:
        sdb_con = create_engine(f'sqlite:////{src_sdb}')
    gps_df = pd.read_sql_table("gps", sdb_con, parse_dates=["utcdate"])

    # Filter records based on start/end dates if required (dates already converted in utc timestamps)
    if start_date:
        gps_df = gps_df[gps_df['utcdate'] >= pd.to_datetime(start_date.replace(tzinfo = None))] # Need to drop tz so that pandas can handle it properly
    if end_date:
        gps_df = gps_df[gps_df['utcdate'] <= pd.to_datetime(end_date.replace(tzinfo = None))]

    # Reformat, dropping unused columns and adding interact_id
    gps_df.insert(0, 'interact_id', interact_id)
    gps_df.drop(columns="ts", inplace=True)
    gps_df = gps_df.convert_dtypes() # Some int were decoded as float in order to handle NULL, this should fix it

    # Save to destination folder
    with NamedTemporaryFile(prefix=f'{interact_id}_GPS-', suffix=".csv", delete=False, dir=dst_dir) as f:
        gps_df.to_csv(f, index=False)

    return f.name

def _single_load_transform_axl(interact_id, src_sdb, dst_dir, start_date=None, end_date=None) -> str:
    """ Process the AXL data stream 
    
    Returns the path to the newly created CSV file"""



if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.DEBUG)

    f = single_load_transform(1000, r"I:\Benoit\WORKSPACE\INTERACT_data_pipeline\data\interact_test_data\montreal\wave_01\sensedoc\401228518_50\SD50fw2099_20180829_163512.sdb", 
                               r"I:\Benoit\WORKSPACE\INTERACT_data_pipeline\data\interact_test_data\montreal\wave_01\sensedoc\elite", '2018-07-17', None)


"""     # Get target root folder as command line argument
    if len(sys.argv[1:]):
        root_data_folder = sys.argv[1]

    if not os.path.isdir(root_data_folder):
        logging.error(f'No directory <{root_data_folder}> found! Aborting')
        exit(1)

    # Reporting, stored in a list of tuples (city, wave, n pids, n sdb, status)
    report = []

    for ccode, city in cities.items():
        for wave in waves:
            n_match = 0

            # Heading
            print(f'===== VALIDATING {city.capitalize()} | Wave {wave} =====')

            # Read linkage file
            # lk_file_path = os.path.join(root_data_folder, city, wave, f'linkage_{wave}_{city}.csv') # WRONG LINKAGE FILE NAME TEMPLATE IN TEST DATA
            lk_file_path = os.path.join(root_data_folder, city, f'wave_{wave:02d}', f'linkage_{ccode}_w{wave}.csv')
            if not os.path.isfile(lk_file_path):
                logging.warning(f'Linkage file <{os.path.basename(lk_file_path)}> not found, skipping')
                report.append((city.capitalize(), 
                           f'Wave {wave}', 
                           '-', 
                           '-', 
                           'No linkage file found'))
                continue
            lk_df = pd.read_csv(lk_file_path, dtype=str)

            # Check if we get the expected columns according to linkage\README.md
            # that is interact_id, sd_id_1, sd_id_2; Report as an ERROR and skip if not
            missing_col = False
            for colname in ['interact_id', 'sd_id_1', 'sd_id_2']:
                if colname not in lk_df.columns:
                    logging.error(f'No column named <{colname}> in linkage file <{os.path.basename(lk_file_path)}>')
                    missing_col = True
            if missing_col:
                report.append((city.capitalize(), 
                           f'Wave {wave}', 
                           '-', 
                           '-', 
                           'Linkage file wrongly formatted'))
                continue

            # Keep only participants with SDs
            lk_df = lk_df.loc[lk_df.sd_id_1.notna(),].reset_index(drop=True)

            # Display linkage file content for control
            logging.debug(f'Linkage file <{os.path.basename(lk_file_path)}>:\n{lk_df.to_string()}')

            # Check if we have duplicated participant
            if not lk_df.interact_id.is_unique:
                logging.error(f'Found duplicated interact_ids in <{os.path.basename(lk_file_path)}>')
                report.append((city.capitalize(), 
                           f'Wave {wave}', 
                           str(len(lk_df.index)), 
                           '-', 
                           'Found duplicated interact_ids'))
                continue

            # Inspect each participant with SD to look for a matching sdb file 
            # (we only check the first one, if more than one SD has been given to that participant)
            for pid in lk_df.itertuples(index=False):
                pid_folder = os.path.join(root_data_folder, city, f'wave_{wave:02d}', 'sensedoc', f'{pid.interact_id}_{pid.sd_id_1}')
                # Check PID folder exists
                if not os.path.isdir(pid_folder):
                    logging.error(f'Unable to find directory <{os.path.relpath(pid_folder, root_data_folder)}>')
                    continue

                missing_sdb = True # Track if matching sdb file is found in folder
                other_sdb = [] # Track all other (not matching) sdb files in folder
                # Define pattern according to type of sd_id
                psdb = f'SD{pid.sd_id_1}fw\\d*_.+.sdb'
                for fentry in os.scandir(pid_folder):
                    if re.fullmatch(psdb, fentry.name):
                        missing_sdb= False
                        break
                    elif re.match('.*.sdb', fentry.name):
                        other_sdb.append(fentry.name)
                if not missing_sdb:
                    logging.info(f'Found sdb file <{fentry.name}> in folder <{pid_folder}>')
                    n_match += 1
                elif len(other_sdb):
                    logging.error(f'No matching sdb file found in folder <{pid_folder}> but other sdb file(s) found:\n\t'+'\n\t'.join(other_sdb))
                else:
                    logging.error(f'No sdb file found in folder <{pid_folder}>')
            
            # Report findings
            #print(f'Expecting {len(lk_df.index)} participants with SD data; found {n_match} participants with matching sdb file')
            report.append((city.capitalize(), 
                           f'Wave {wave}', 
                           str(len(lk_df.index)), 
                           str(n_match), 
                           'OK' if n_match == len(lk_df.index) else 'Missing SD files'))

    report_df = pd.DataFrame(report, columns=['City', 'Wave', 'Expected PIDs with SD', 'Found PIDs with SD', 'Status'])
    print(report_df)"""