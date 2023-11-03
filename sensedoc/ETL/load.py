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
from time import perf_counter, strftime
import multiprocessing as mp


# Define city_id and wave_id
cities = {'mtl': 'montreal', 
          'skt': 'saskatoon', 
          'van': 'vancouver', 
          'vic': 'victoria'}
waves = [1, 2, 3]

# Define base folder when not provided on the cmd line
root_data_folder = 'data\interact_test_data'


def single_load_transform(interact_id, src_sdb, dst_dir, start_date=None, end_date=None, city=None, wave=None):
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
    - city (optional): for reporting
    - wave (optional): for reporting

    Returns:
    --------
    A tuple with (city, wave, interact_id, gps_ok, axl_ok)

    Notes:
    ------
    - Dates (in YYYY-MM-DD format) are converted to UTC timestamps, based on the 
        city of participation.
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
        try:
            start_date = datetime.strptime(f'{start_date} 00:00:00', '%Y-%m-%d %H:%M:%S')
            start_date = target_tz.localize(start_date)
            start_date = start_date.astimezone(pytz.utc)
        except Exception as e:
            logging.error(f'Participant # {interact_id}: unexpected error while decoding date ({e})')
            return (city, wave, interact_id, 0, 0)


    if end_date is not None:
        try:
            end_date = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
            end_date = target_tz.localize(end_date)
            end_date = end_date.astimezone(pytz.utc)
        except Exception as e:
            logging.error(f'Participant # {interact_id}: unexpected error while decoding date ({e})')
            return (city, wave, interact_id, 0, 0)

    # Process GPS
    gps_ok = None
    try:
        c0 = perf_counter()
        gps_file = _single_load_transform_gps(interact_id, src_sdb, dst_dir, start_date, end_date)
        c1 = perf_counter()
        gps_ok = 1
        logging.info(f'Participant # {interact_id}: GPS elite file -> {os.path.basename(gps_file)} [{c1-c0:.1f}s]')
    except Exception as e:
        gps_ok = 0
        logging.error(f'Participant # {interact_id}: Unable to process GPS ({e})')

    # Process AXL
    axl_ok = None
    try:
        c0 = perf_counter()
        axl_file = _single_load_transform_axl(interact_id, src_sdb, dst_dir, start_date, end_date)
        c1 = perf_counter()
        axl_ok = 1
        logging.info(f'Participant # {interact_id}: AXL elite file -> {os.path.basename(axl_file)} [{c1-c0:.1f}s]')
    except Exception as e:
        axl_ok = 0
        logging.error(f'Participant # {interact_id}: Unable to process AXL ({e})')

    return (city, wave, interact_id, gps_ok, axl_ok)


def _single_load_transform_gps(interact_id, src_sdb, dst_dir, start_date, end_date) -> str:
    """ Process the GPS data stream 
    
    Returns the path to the newly created CSV file"""

    # Load GPS data from sdb file
    if platform.system() == 'Windows':
        # Connection string varies between Linux/Max and Windows
        sdb_con = create_engine(f'sqlite:///{src_sdb}') 
    else:
        sdb_con = create_engine(f'sqlite:////{src_sdb}')
    gps_df = pd.read_sql_table("gps", sdb_con, parse_dates=["utcdate"])

    # Check if several sdb with _rtcX have been created, deal with the loading in that case
    i = 1
    src_rtc = f'{os.path.splitext(src_sdb)[0]}_rtc{i}{os.path.splitext(src_sdb)[1]}'
    while os.path.exists(src_rtc):
        if platform.system() == 'Windows':
            # Connection string varies between Linux/Max and Windows
            rtc_con = create_engine(f'sqlite:///{src_rtc}') 
        else:
            rtc_con = create_engine(f'sqlite:////{src_rtc}')
        rtc_df = pd.read_sql_table("gps", rtc_con, parse_dates=["utcdate"])
        rtc_df.loc[:,'rtc'] = i # Keep track of rtc count, although not used for the moment
        gps_df = pd.concat([gps_df, rtc_df])
        i += 1
        src_rtc = f'{os.path.splitext(src_sdb)[0]}_rtc{i}{os.path.splitext(src_sdb)[1]}'

    # Filter records based on start/end dates if required (dates already converted in utc timestamps)
    if start_date:
        gps_df = gps_df[gps_df['utcdate'] >= pd.to_datetime(start_date.replace(tzinfo = None))] # Need to drop tz so that pandas can handle it properly
    if end_date:
        gps_df = gps_df[gps_df['utcdate'] <= pd.to_datetime(end_date.replace(tzinfo = None))]

    # Reformat, dropping unused columns and adding interact_id
    gps_df.insert(0, 'interact_id', interact_id)
    gps_df.drop(columns="ts", inplace=True)
    if 'rtc' in gps_df:
        gps_df.drop(columns='rtc', inplace=True)
    gps_df.sort_values(by = "utcdate", inplace=True)
    gps_df = gps_df.convert_dtypes() # Some int were decoded as float in order to handle NULL, this should fix it

    # Save to destination folder
    with NamedTemporaryFile(prefix=f'{interact_id}_GPS-', suffix=".csv", delete=False, dir=dst_dir) as f:
        gps_df.to_csv(f, index=False)

    return f.name

def _single_load_transform_axl(interact_id, src_sdb, dst_dir, start_date=None, end_date=None) -> str:
    """ Process the AXL data stream 
    
    Returns the path to the newly created CSV file"""

    # Load AXL data from sdb file
    # NB: using the accel_utcdate view, which precompute the utc date/time from the SD timestamp
    if platform.system() == 'Windows':
        # Connection string varies between Linux/Max and Windows
        sdb_con = create_engine(f'sqlite:///{src_sdb}') 
    else:
        sdb_con = create_engine(f'sqlite:////{src_sdb}')
    axl_df = pd.read_sql_table("accel", sdb_con)

    # Check if several sdb with _rtcX have been created, deal with the loading in that case
    i = 1
    src_rtc = f'{os.path.splitext(src_sdb)[0]}_rtc{i}{os.path.splitext(src_sdb)[1]}'
    while os.path.exists(src_rtc):
        if platform.system() == 'Windows':
            # Connection string varies between Linux/Max and Windows
            rtc_con = create_engine(f'sqlite:///{src_rtc}') 
        else:
            rtc_con = create_engine(f'sqlite:////{src_rtc}')
        rtc_df = pd.read_sql_table("accel", rtc_con)
        rtc_df.loc[:,'rtc'] = i # Keep track of rtc count, although not used for the moment
        axl_df = pd.concat([axl_df, rtc_df])
        i += 1
        src_rtc = f'{os.path.splitext(src_sdb)[0]}_rtc{i}{os.path.splitext(src_sdb)[1]}'

    # Convert int axl measures to g
    axl_factor = pd.read_sql_query("SELECT value FROM ancillary WHERE key = 'axlFactor'", sdb_con)
    axl_factor = float(axl_factor.iloc[0, 0])
    for col in ['x', 'y', 'z']:
        axl_df.loc[:,col] = axl_factor * axl_df[col]

    # Add utcdate
    ref_date = pd.read_sql_query("SELECT value FROM ancillary WHERE key = 'refDate'", sdb_con)
    ref_date = pd.to_datetime(ref_date.iloc[0, 0])
    axl_df.insert(0, 'utcdate', ref_date + pd.to_timedelta(axl_df['ts'], unit='Micro'))

    # Filter records based on start/end dates if required (dates already converted in utc timestamps)
    if start_date:
        axl_df = axl_df[axl_df['utcdate'] >= pd.to_datetime(start_date.replace(tzinfo = None))] # Need to drop tz so that pandas can handle it properly
    if end_date:
        axl_df = axl_df[axl_df['utcdate'] <= pd.to_datetime(end_date.replace(tzinfo = None))]

    # Reformat, dropping unused columns and adding interact_id
    axl_df.insert(0, 'interact_id', interact_id)
    axl_df.drop(columns="ts", inplace=True)
    if 'rtc' in axl_df:
        axl_df.drop(columns='rtc', inplace=True)
    axl_df.sort_values(by = "utcdate", inplace=True)
    axl_df = axl_df.convert_dtypes() # Some int were decoded as float in order to handle NULL, this should fix it

    # Save to destination folder
    with NamedTemporaryFile(prefix=f'{interact_id}_AXL-', suffix=".csv", delete=False, dir=dst_dir) as f:
        axl_df.to_csv(f, index=False, float_format="%.5f")
    
    return f.name


def load_transform_sd(src_dir, ncpu=None):
    """ Batch process all SenseDoc data to create Elite files,
    e.g. CSV files with raw GPS and AXL data.
    Data is expected to have been validated beforehand and follow
    the directory hierarchy defined in ReadMe file:
        <CITY>
          |
          +- <WAVE_N>
               |
               +- <sensedoc>
                    |
                    +- <iid_sdid>
                         |
                         +- sdb file
    
    CSV files are saved within a newly created <sensedoc_elite_files> 
    directory within the <CITY\WAVE_N> folder, i.e. at the same level
    as the <sensedoc> folder.

    Steps:
    1. Create <sensedoc_elite_files> subfolder within each city/wave;
        folder needs to be empty if already existing
    2. Search linkage file within each city/wave
    3. Extract metadata for all participants with one or more SD file;
        store in pool worker argument list
    4. Run multiprocessing pool of workers
    5. Once all workers have completed, clean the elite files:
        - Drop random part in name -> IID_GPS.CSV / IID_AXL.CSV
        - Append suffix (.N) to name when more than one SD used
    6. Report back
    """
    # Store pool worker arguments in list of tuples
    # Arg = (interact_id, src_sdb, dst_dir, start_date, end_date) / see single_load_transform
    wrk_args = []

    for ccode, city in cities.items():
        for wave in waves:
            # Check that city/wave folder exists, which is the case with test data...
            if not os.path.exists(os.path.join(root_data_folder, city, f'wave_{wave:02d}')):
                logging.warning(f'Unable to find subfolder <{os.path.join(city, f"wave_{wave:02d}")}>, skipping!')
                continue
            # Create elite subfolder
            elite_folder = os.path.join(root_data_folder, city, f'wave_{wave:02d}', 'sensedoc_elite_files')
            if os.path.exists(elite_folder):
                # Check folder is empty, other raise an error
                with os.scandir(elite_folder) as it:
                    if any(it):
                        logging.error(f'Found a non-empty elite folder <{os.path.relpath(elite_folder, root_data_folder)}>, aborting!')
                        exit(1)
            else:
                os.mkdir(elite_folder)

            # Read linkage file and add corresponding args to list of worker args
            lk_file_path = os.path.join(root_data_folder, city, f'wave_{wave:02d}', f'linkage_{ccode}_w{wave}.csv')
            if not os.path.isfile(lk_file_path):
                logging.warning(f'Linkage file <{os.path.basename(lk_file_path)}> not found, skipping')
                continue
            lk_df = pd.read_csv(lk_file_path, dtype=str)

            # Keep only participants with SDs and pivot table to extract all SD when more than one
            lk_df = lk_df.loc[lk_df.sd_id_1.notna(),].reset_index(drop=True)
            lk_df_long = pd.wide_to_long(lk_df, ['sd_id', 'sd_firmware', 'sd_start', 'sd_end'], sep="_", i='interact_id', j='sd_rank')
            lk_df_long = lk_df_long.loc[lk_df_long['sd_id'].notna(),['sd_id', 'sd_start', 'sd_end']]
            lk_df_long.reset_index(drop=False, inplace=True)

            # Display linkage file content for control
            logging.debug(f'Sd to process, according to linkage file <{os.path.basename(lk_file_path)}>:\n{lk_df_long.to_string()}')

            # Load pid/sd metadata for processing by pool of workers
            for pid in lk_df_long.itertuples(index=False):
                pid_folder = os.path.join(root_data_folder, city, f'wave_{wave:02d}', 'sensedoc', f'{pid.interact_id}_{pid.sd_id}')

                if not os.path.exists(pid_folder):
                    logging.warning(f'No folder <{os.path.relpath(pid_folder, root_data_folder)}> found, skipping')
                    continue

                missing_sdb = True
                # Define pattern according to type of sd_id
                psdb = f'SD{pid.sd_id}fw\\d*_.+.sdb'
                for fentry in os.scandir(pid_folder):
                    if re.fullmatch(psdb, fentry.name):
                        wrk_args.append((pid.interact_id, 
                                         os.path.join(pid_folder, fentry.name),
                                         elite_folder,
                                         pid.sd_start,
                                         pid.sd_end,
                                         city, wave))
                        missing_sdb = False
                        break
                        
                if missing_sdb:
                    logging.warning(f'No sdb file found in folder <{os.path.relpath(pid_folder, root_data_folder)}>, skipping')
            
    # DEBUG: display full list of args for workers
    for t in wrk_args:
        print(t)

    # TODO: finalize
    c0 = perf_counter()
    with mp.Pool(2) as pool:
        results = pool.starmap_async(single_load_transform, wrk_args[:3])
        for result in results.get():
            print(f'[{strftime("%X")}] {result}', flush=True)

    print(f'DONE: {perf_counter() - c0:.1f}s')

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S') #, level=logging.DEBUG)

    # f = single_load_transform(1000, r"data\interact_test_data\saskatoon\wave_01\sensedoc\302544861_487\SD487fw2106_20181029_133049.sdb", 
    #                            r"data\interact_test_data\test_elite_files", '2018-10-03', None)

    # Get target root folder as command line argument
    if len(sys.argv[1:]):
        root_data_folder = sys.argv[1]

    if not os.path.isdir(root_data_folder):
        logging.error(f'No directory <{root_data_folder}> found! Aborting')
        exit(1)

    load_transform_sd(root_data_folder)