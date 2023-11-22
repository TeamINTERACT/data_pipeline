"""Loading and transformation of SenseDoc data into (zipped) CSV files

Creates one csv per participant/wave/sensor, file name includes INTERACT_ID. 
The result is a folder per sensor, per city, each with a csv file per 
participant with data and INTERACT_ID.
Resulting CSV files are stored in the <sensedoc_elite_files> subfolder within
each city/wave folder.
--
USAGE: load.py [TARGET_ROOT_FOLDER]

If TARGET_ROOT_FOLDER not provided, will default to test data folder.
"""
# Required to avoid bug in Pandas https://github.com/pandas-dev/pandas/issues/55025
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import sys
import logging
import re
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import platform
from datetime import datetime
import pytz
from tempfile import NamedTemporaryFile
from time import perf_counter, strftime
import multiprocessing as mp
from itertools import starmap


# Define city_id and wave_id
cities = {'mtl': 'montreal', 
          'skt': 'saskatoon', 
          'van': 'vancouver', 
          'vic': 'victoria'}
waves = [1, 2, 3]

# Define base folder when not provided on the cmd line
root_data_folder = 'data\interact_test_data'


def single_load_transform(interact_id, sd_id, src_sdb, dst_dir, 
                          start_date=None, end_date=None, city=None, wave=None,
                          process_gps = True, process_axl = True):
    """
    Processing of a single participant's SD data.
    Load GPS and AXL data separately from sdb file, filter records to keep only
    measurements within start and end dates, then save each of the two streams 
    to a CSV file with interact_id, timestamp followed by axl/gps measurements.

    Parameters:
    -----------
    - interact_id: Participant unique ID
    - sd_id: SenseDoc ID
    - src_sdb: Path to the SDB file, that contains the AXL and GPS data
    - dst_dir: Path where newly created CSV files (one for GPS, one for AXL) will
        be saved 
    - start_date (Optional): if provided, only records on or after the start date will
        be saved to the CSV file; format YYYY-MM-DD
    - end_date (Optional): if provided, only records on or before the end date will
        be saved to the CSV file; format YYYY-MM-DD
    - city (optional): for reporting
    - wave (optional): for reporting
    - process_gps (optional): if true, GPS from sdb will be processed 
    - process_axl (optional): if true, accelerometry from sdb will be processed 

    Returns:
    --------
    A tuple with (city, wave, interact_id, sd_id, gps_ok, axl_ok)

    Notes:
    ------
    - Dates (in YYYY-MM-DD format) are converted to UTC timestamps, based on the 
        city of participation.
        Start date -> start date at 00:00:00 local time
        End date -> end date at 23:59:59 local time
    - rtc sdb files, which happen when the SenseDoc Realt Time Clock is reset unexpectedly,
        are appended to the current output CSV as long as their timestamps fall within 
        period bounds
    """
    logging.debug(f'PID {mp.current_process().pid}: processing {interact_id}/{sd_id}')
    # A bit of checking going-on here:
    # TODO

    # Convert dates to proper UTC timestamp
    tz_lut = {'1': 'America/Vancouver', # Victoria
              '2': 'America/Vancouver', # Vancouver'
              '3': 'America/Regina', # Saskatoon
              '4': 'America/Toronto'} # Montreal
    target_tz = pytz.timezone(tz_lut[str(interact_id)[:1]]) # First number of iid codes the city

    if pd.notna(start_date):
        try:
            start_date = datetime.strptime(f'{start_date} 00:00:00', '%Y-%m-%d %H:%M:%S')
            start_date = target_tz.localize(start_date)
            start_date = start_date.astimezone(pytz.utc)
        except Exception as e:
            logging.error(f'Participant # {interact_id}: unexpected error while decoding date ({e})')
            return (city.capitalize(), wave, interact_id, sd_id, 0, 0)


    if pd.notna(end_date):
        try:
            end_date = datetime.strptime(f'{end_date} 23:59:59', '%Y-%m-%d %H:%M:%S')
            end_date = target_tz.localize(end_date)
            end_date = end_date.astimezone(pytz.utc)
        except Exception as e:
            logging.error(f'Participant # {interact_id}: unexpected error while decoding date ({e})')
            return (city.capitalize(), wave, interact_id, sd_id, 0, 0)

    # Process GPS
    gps_ok = None
    if process_gps:
        try:
            c0 = perf_counter()
            gps_file = _single_load_transform_gps(interact_id, sd_id, src_sdb, dst_dir, start_date, end_date)
            c1 = perf_counter()
            gps_ok = 1
            logging.info(f'Participant # {interact_id}: GPS elite file -> {os.path.basename(gps_file)} [{c1-c0:.1f}s]')
        except Exception as e:
            gps_ok = 0
            logging.error(f'Participant # {interact_id}: Unable to process GPS ({e})')
    else:
        gps_ok = -1

    # Process AXL
    axl_ok = None
    if process_axl:
        try:
            c0 = perf_counter()
            axl_file = _single_load_transform_axl(interact_id, sd_id, src_sdb, dst_dir, start_date, end_date)
            c1 = perf_counter()
            axl_ok = 1
            logging.info(f'Participant # {interact_id}: AXL elite file -> {os.path.basename(axl_file)} [{c1-c0:.1f}s]')
        except Exception as e:
            axl_ok = 0
            logging.error(f'Participant # {interact_id}: Unable to process AXL ({e})')
    else:
        axl_ok = -1

    return (city.capitalize(), wave, interact_id, sd_id, gps_ok, axl_ok)


def _single_load_transform_gps(interact_id, sd_id, src_sdb, dst_dir, start_date, end_date) -> str:
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
        i += 1
        src_rtc = f'{os.path.splitext(src_sdb)[0]}_rtc{i}{os.path.splitext(src_sdb)[1]}'
        if rtc_df.empty:
            continue
        rtc_df.loc[:,'rtc'] = i # Keep track of rtc count, although not used for the moment
        gps_df = pd.concat([gps_df, rtc_df])

    # Filter records based on start/end dates if required (dates already converted in utc timestamps)
    if pd.notna(start_date):
        gps_df = gps_df[gps_df['utcdate'] >= pd.to_datetime(start_date.replace(tzinfo = None))] # Need to drop tz so that pandas can handle it properly
    if pd.notna(end_date):
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

    # Try to rename newly created file
    # FIXME: Unable to properly deal with race condition on Linux, althought
    # the risk of having the same name is close to zero
    dst_f = os.path.join(dst_dir, f'{interact_id}_{sd_id}_GPS.csv')
    if not os.path.exists(dst_f):
        os.replace(os.path.join(dst_dir, f.name), dst_f)
    else:
        i = 1
        dst_f = os.path.join(dst_dir, f'{interact_id}_{sd_id}.{i}_GPS.csv')
        while os.path.exists(dst_f):
            i += 1
            dst_f = os.path.join(dst_dir, f'{interact_id}_{sd_id}.{i}_GPS.csv')
        os.replace(os.path.join(dst_dir, f.name), dst_f)

    return dst_f

def _single_load_transform_axl(interact_id, sd_id, src_sdb, dst_dir, start_date=None, end_date=None) -> str:
    """ Process the AXL data stream 
    
    Returns the path to the newly created CSV file"""

    def _scale_axl(_axl_df, _con) -> pd.DataFrame:
        """ Scale X,Y,Z values to g and add utcdate """

        # Convert int axl measures to g
        axl_factor = pd.read_sql_query("SELECT value FROM ancillary WHERE key = 'axlFactor'", _con)
        axl_factor = float(axl_factor.iloc[0, 0])
        for col in ['x', 'y', 'z']:
            _axl_df.loc[:,col] = axl_factor * _axl_df[col]

        # Add utcdate
        ref_date = pd.read_sql_query("SELECT value FROM ancillary WHERE key = 'refDate'", _con)
        ref_date = pd.to_datetime(ref_date.iloc[0, 0])
        _axl_df.insert(0, 'utcdate', ref_date + pd.to_timedelta(_axl_df['ts'], unit='Micro'))

        return _axl_df

    # Load AXL data from sdb file
    # NB: using the accel_utcdate view, which precompute the utc date/time from the SD timestamp
    if platform.system() == 'Windows':
        # Connection string varies between Linux/Max and Windows
        sdb_con = create_engine(f'sqlite:///{src_sdb}') 
    else:
        sdb_con = create_engine(f'sqlite:////{src_sdb}')
    axl_df = pd.read_sql_table("accel", sdb_con)

    # Scale timestamp and axes
    axl_df = _scale_axl(axl_df, sdb_con)

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
        i += 1
        src_rtc = f'{os.path.splitext(src_sdb)[0]}_rtc{i}{os.path.splitext(src_sdb)[1]}'
        if rtc_df.empty:
            continue
        rtc_df = _scale_axl(rtc_df, rtc_con)
        rtc_df.loc[:,'rtc'] = i # Keep track of rtc count, although not used for the moment
        axl_df = pd.concat([axl_df, rtc_df])

    # Filter records based on start/end dates if required (dates already converted in utc timestamps)
    if pd.notna(start_date):
        axl_df = axl_df[axl_df['utcdate'] >= pd.to_datetime(start_date.replace(tzinfo = None))] # Need to drop tz so that pandas can handle it properly
    if pd.notna(end_date):
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
    
    # Try to rename newly created file
    # FIXME: Unable to properly deal with race condition on Linux, althought
    # the risk of having the same name is close to zero
    dst_f = os.path.join(dst_dir, f'{interact_id}_{sd_id}_AXL.csv')
    if not os.path.exists(dst_f):
        os.replace(os.path.join(dst_dir, f.name), dst_f)
    else:
        i = 1
        dst_f = os.path.join(dst_dir, f'{interact_id}_{sd_id}.{i}_AXL.csv')
        while os.path.exists(dst_f):
            i += 1
            dst_f = os.path.join(dst_dir, f'{interact_id}_{sd_id}.{i}_AXL.csv')
        os.replace(os.path.join(dst_dir, f.name), dst_f)

    return dst_f


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
        if folder already contains files, the processing of their
        interact_id/sd_id combination will be removed from the processing
        queue 
    2. Search linkage file within each city/wave
    3. Extract metadata for all participants with one or more SD file;
        store in pool worker argument list
    4. Run multiprocessing pool of workers
    5. Report back
    """
    # Store pool worker arguments in list of tuples
    # Arg = (interact_id, src_sdb, dst_dir, start_date, end_date) / see single_load_transform
    wrk_args = []

    for ccode, city in cities.items():
        for wave in waves:
            # Check that city/wave folder exists, which is the case with test data...
            if not os.path.exists(os.path.join(src_dir, city, f'wave_{wave:02d}')):
                logging.warning(f'Unable to find subfolder <{os.path.join(city, f"wave_{wave:02d}")}>, skipping')
                continue
            # Create elite subfolder
            elite_folder = os.path.join(src_dir, city, f'wave_{wave:02d}', 'sensedoc_elite_files')
            existing_files = [] # store (interact_id, sd_id, gps_found, axl_found)
            if os.path.exists(elite_folder):
                # Found a folder, all content will be scan to remove already processed GPS/AXL files from queue
                with os.scandir(elite_folder) as it:
                    existing_files_dict = {}
                    warned = False
                    for f in it:
                        m = re.match('(?P<iid>\\d+)_(?P<sd_id>\\d+)_(?P<sensor>GPS|AXL).csv', f.name)
                        if m is not None:
                            if not warned:
                                logging.warning(f'Elite folder <{os.path.relpath(elite_folder, src_dir)}> contains already processed files, which will be skipped')
                                warned = True
                            found = existing_files_dict.get((m.group('iid'), m.group('sd_id')), {})
                            found[m.group('sensor')] = 1
                            existing_files_dict[(m.group('iid'), m.group('sd_id'))] = found
                    # Restructure dict to list of tuples
                    for iid_sdid, snsr in existing_files_dict.items():
                        iid, sdid = iid_sdid
                        existing_files.append((iid, sdid, snsr.get('GPS', 0), snsr.get('AXL', 0)))
            else:
                os.mkdir(elite_folder)

            # Read linkage file and add corresponding args to list of worker args
            lk_file_path = os.path.join(src_dir, city, f'wave_{wave:02d}', f'linkage_{ccode}_w{wave}.csv')
            if not os.path.isfile(lk_file_path):
                logging.warning(f'Linkage file <{os.path.basename(lk_file_path)}> not found, skipping')
                continue
            lk_df = pd.read_csv(lk_file_path, dtype=str)

            # Keep only participants with SDs and pivot table to extract all SD when more than one
            lk_df = lk_df.loc[lk_df.sd_id_1.notna(),].reset_index(drop=True)
            lk_df_long = pd.wide_to_long(lk_df, ['sd_id', 'sd_firmware', 'sd_start', 'sd_end'], sep="_", i='interact_id', j='sd_rank')
            lk_df_long = lk_df_long.loc[lk_df_long['sd_id'].notna(),['sd_id', 'sd_start', 'sd_end']]
            lk_df_long.reset_index(drop=False, inplace=True)

            # Flag participant/sd already processed, even partially
            processed_df = pd.DataFrame(existing_files, columns=['interact_id', 'sd_id', 'gps_done', 'axl_done'])
            lk_df_long = lk_df_long.merge(processed_df, how='left')
            lk_df_long.loc[:,'process_gps'] = np.where(lk_df_long['gps_done'] == 1, False, True)
            lk_df_long.loc[:,'process_axl'] = np.where(lk_df_long['axl_done'] == 1, False, True)
            lk_df_long.drop(columns=['gps_done', 'axl_done'], inplace=True)

            # Display linkage file content for control
            logging.debug(f'SD to process, according to linkage file <{os.path.basename(lk_file_path)}>:\n{lk_df_long.to_string()}')

            # Load pid/sd metadata for processing by pool of workers
            for pid in lk_df_long.itertuples(index=False):
                pid_folder = os.path.join(src_dir, city, f'wave_{wave:02d}', 'sensedoc', f'{pid.interact_id}_{pid.sd_id}')

                if not os.path.exists(pid_folder):
                    logging.warning(f'No folder <{os.path.relpath(pid_folder, src_dir)}> found, skipping')
                    continue

                missing_sdb = True
                # Define pattern according to type of sd_id
                psdb = f'SD{pid.sd_id}fw\\d*_.+.sdb'
                for fentry in os.scandir(pid_folder):
                    if re.fullmatch(psdb, fentry.name) : #and (pid.process_gps or pid.process_axl):
                        wrk_args.append((pid.interact_id,
                                         pid.sd_id,
                                         os.path.join(pid_folder, fentry.name),
                                         elite_folder,
                                         pid.sd_start,
                                         pid.sd_end,
                                         city, f'Wave {wave}',
                                         pid.process_gps,
                                         pid.process_axl))
                        missing_sdb = False
                        break
                        
                if missing_sdb:
                    logging.warning(f'No sdb file found in folder <{os.path.relpath(pid_folder, src_dir)}>, skipping')
            
    # Multiprocessing run
    c0 = perf_counter()
    if ncpu > 1: # Switch to multiprocessing if more than 1 CPU
        with mp.Pool(processes=ncpu, maxtasksperchild=1) as pool:
            results = pool.starmap_async(single_load_transform, wrk_args)
            result_df = pd.DataFrame([r for r in results.get()], columns=['City', 'Wave', 'iid', 'sd', 'GPS', 'AXL']).convert_dtypes()
    else:
        # Single thread processing (for debug only)
        results = starmap(single_load_transform, wrk_args)
        result_df = pd.DataFrame([r for r in results], columns=['City', 'Wave', 'iid', 'sd', 'GPS', 'AXL']).convert_dtypes()

    # Display stats on computation
    print('==== PROCESSING REPORT | GPS ====')
    result_gps_df = result_df.groupby(['City', 'Wave', 'GPS'], as_index=False).size()
    result_gps_df.loc[result_gps_df['GPS'] == 0,'GPS Statut'] = 'Error'
    result_gps_df.loc[result_gps_df['GPS'] == 1,'GPS Statut'] = 'OK'
    result_gps_df.loc[result_gps_df['GPS'] == -1,'GPS Statut'] = 'Skipped'
    result_gps_df = result_gps_df.pivot(index=['City', 'Wave'], columns='GPS Statut', values='size').fillna(0).convert_dtypes()
    print(result_gps_df.reset_index().to_markdown(index=False, tablefmt='presto'))
    print('==== PROCESSING REPORT | AXL ====')
    result_axl_df = result_df.groupby(['City', 'Wave', 'AXL'], as_index=False).size()
    result_axl_df.loc[result_axl_df['AXL'] == 0,'AXL Statut'] = 'Error'
    result_axl_df.loc[result_axl_df['AXL'] == 1,'AXL Statut'] = 'OK'
    result_axl_df.loc[result_axl_df['AXL'] == -1,'AXL Statut'] = 'Skipped'
    result_axl_df = result_axl_df.pivot(index=['City', 'Wave'], columns='AXL Statut', values='size').fillna(0).convert_dtypes()
    print(result_axl_df.reset_index().to_markdown(index=False, tablefmt='presto'))
    print(f'DONE: {perf_counter() - c0:.1f}s')

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.DEBUG)

    # Get target root folder as command line argument
    if len(sys.argv[1:]):
        root_data_folder = sys.argv[1]

    if not os.path.isdir(root_data_folder):
        logging.error(f'No directory <{root_data_folder}> found! Aborting')
        exit(1)

    ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK',default=1))
    load_transform_sd(root_data_folder, ncpus)