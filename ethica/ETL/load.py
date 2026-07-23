"""Loading and transformation of SenseDoc data into (zipped) CSV files

Creates one csv per participant/wave/sensor, file name includes INTERACT_ID. 
The result is a folder per sensor, per city, each with a csv file per 
participant with data and INTERACT_ID.
Resulting CSV files are stored in the <sensedoc_elite_files> subfolder within
each city/wave folder.
--
USAGE: load.py [TARGET_ROOT_FOLDER [WAVE]]

If TARGET_ROOT_FOLDER not provided, will default to test data folder.
If WAVE is not provided, all waves (1-4) will be processed
"""
# Required to avoid bug in Pandas https://github.com/pandas-dev/pandas/issues/55025
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import sys
import logging
import re
import pandas as pd
import polars as pl
from polars.io.partition import FileProviderArgs
import numpy as np
from tempfile import NamedTemporaryFile
from time import perf_counter
import multiprocessing as mp
from itertools import starmap


# Define city_id and wave_id
cities = {'mtl': 'montreal', 
            'skt': 'saskatoon', 
            'van': 'vancouver', 
            'vic': 'victoria'}
waves = [1, 2, 3, 4]

# Define base folder when not provided on the cmd line
root_data_folder = 'data\interact_test_data'
wave_id = None


def single_load_transform(interact_id, ethica_id, src_dir, dst_dir, 
                        city='', wave='',
                        process_gps = True, process_axl = True):
    """
    Processing of a single participant's SD data.
    Load GPS and AXL data separately from sdb file, filter records to keep only
    measurements within start and end dates, then save each of the two streams 
    to a CSV file with interact_id, timestamp followed by axl/gps measurements.

    Parameters:
    -----------
    - interact_id: Participant unique ID
    - ethica_id: Ethica user ID
    - src_dir: Path to Ethica raw data folder, should be named with the study ID
    - dst_dir: Path where newly created CSV files (one for GPS, one for AXL) will
        be saved 
    - city (optional): for reporting
    - wave (optional): for reporting
    - process_gps (optional): if true, GPS from sdb will be processed 
    - process_axl (optional): if true, accelerometry from sdb will be processed 

    Returns:
    --------
    A tuple with (city, wave, interact_id, ethica_id, gps_ok, axl_ok)
    """
    logging.debug(f'PID {mp.current_process().pid}: processing {interact_id}/{ethica_id}')
    # A bit of checking going-on here:
    # TODO

    # Build AXL and GPS file paths
    study_id = os.path.basename(src_dir)
    if not re.fullmatch('\\d+', study_id):
        logging.error(f'Invalid source folder {src_dir}')
        return (city.capitalize(), wave, interact_id, ethica_id, 0, 0)
    axl_file = os.path.join(src_dir, f'{study_id}_accelerometer.csv')
    gps_file = os.path.join(src_dir, f'{study_id}_gps.csv')

    # Process GPS
    gps_ok = None
    if process_gps:
        try:
            c0 = perf_counter()
            gps_file = _single_load_transform_gps(interact_id, ethica_id, gps_file, dst_dir)
            c1 = perf_counter()
            if gps_file is None:
                gps_ok = -1
            else:
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
            axl_file = _single_load_transform_axl(interact_id, ethica_id, axl_file, dst_dir)
            c1 = perf_counter()
            if axl_file is None:
                axl_ok = -1
            else:
                axl_ok = 1
                logging.info(f'Participant # {interact_id}: AXL elite file -> {os.path.basename(axl_file)} [{c1-c0:.1f}s]')
        except Exception as e:
            axl_ok = 0
            logging.error(f'Participant # {interact_id}: Unable to process AXL ({e})')
    else:
        axl_ok = -1

    return (city.capitalize(), wave, interact_id, ethica_id, gps_ok, axl_ok)


def _single_load_transform_gps(interact_id, ethica_id, gps_file, dst_dir) -> str:
    """ Process the GPS data stream 
    
    Returns the path to the newly created CSV file"""

    # Load GPS data from CSV file using Polars and Lazy API
    q = (
        pl.scan_csv(gps_file)
        .select(['user_id', 'device_id', 'record_time', 'accu', 'alt', 'bearing', 'lat', 'lon', 'provider', 'satellite_time', 'speed'])
        .filter(pl.col("user_id") == ethica_id)
    )
    gps_df = q.collect()
    gps_df.insert_column(0, (pl.lit(interact_id)).alias('interact_id'))

    # Check if axl df is empty
    if gps_df.is_empty():
        logging.warning(f'Participant # {interact_id}/{ethica_id}: no GPS data (source: <{gps_file}>)')
        return None

    # Save to destination folder
    with NamedTemporaryFile(prefix=f'{interact_id}_GPS-', suffix=".csv", delete=False, dir=dst_dir) as f:
        gps_df.write_csv(f)
    os.chmod(f.name, 0o640) # Give group read on top of owner rw, which is default for NamedTempFile

    # Try to rename newly created file
    # FIXME: Unable to properly deal with race condition on Linux, althought
    # the risk of having the same name is close to zero
    dst_f = os.path.join(dst_dir, f'{interact_id}_{ethica_id}_GPS.csv')
    if not os.path.exists(dst_f):
        os.replace(os.path.join(dst_dir, f.name), dst_f)
    else:
        i = 1
        dst_f = os.path.join(dst_dir, f'{interact_id}_{ethica_id}.{i}_GPS.csv')
        while os.path.exists(dst_f):
            i += 1
            dst_f = os.path.join(dst_dir, f'{interact_id}_{ethica_id}.{i}_GPS.csv')
        os.replace(os.path.join(dst_dir, f.name), dst_f)

    return dst_f

def _single_load_transform_axl(interact_id, ethica_id, axl_file, dst_dir) -> str:
    """ Process the AXL data stream 
    
    Returns the path to the newly created CSV file"""

    # Load AXL data from CSV file using Polars and Lazy API
    q = (
        pl.scan_csv(axl_file)
        .select(['user_id', 'device_id', 'record_time', 'accu', 'x_axis', 'y_axis', 'z_axis'])
        .filter(pl.col("user_id") == ethica_id)
    )
    axl_df = q.collect()
    axl_df.insert_column(0, (pl.lit(interact_id)).alias('interact_id'))

    # Check if axl df is empty
    if axl_df.is_empty():
        logging.warning(f'Participant # {interact_id}/{ethica_id}: no AXL data (source: <{axl_file}>)')
        return None

    # Save to destination folder
    with NamedTemporaryFile(prefix=f'{interact_id}_AXL-', suffix=".csv", delete=False, dir=dst_dir) as f:
        axl_df.write_csv(f)
    os.chmod(f.name, 0o640) # Give group read on top of owner rw, which is default for NamedTempFile
    
    # Try to rename newly created file
    # FIXME: Unable to properly deal with race condition on Linux, althought
    # the risk of having the same name is close to zero
    dst_f = os.path.join(dst_dir, f'{interact_id}_{ethica_id}_AXL.csv')
    if not os.path.exists(dst_f):
        os.replace(os.path.join(dst_dir, f.name), dst_f)
    else:
        i = 1
        dst_f = os.path.join(dst_dir, f'{interact_id}_{ethica_id}.{i}_AXL.csv')
        while os.path.exists(dst_f):
            i += 1
            dst_f = os.path.join(dst_dir, f'{interact_id}_{ethica_id}.{i}_AXL.csv')
        os.replace(os.path.join(dst_dir, f.name), dst_f)

    return dst_f


def load_transform_ethica(src_dir, ncpu=1):
    """ Batch process all Ethica data to create Elite files,
    e.g. CSV files with raw GPS and AXL data.
    Data is expected to have been validated beforehand and follow
    the directory hierarchy defined in ReadMe file:
        <CITY>
            └─ <WAVE_N>
                └─ ethica
                    └─ <STUDY_ID>
                        ├─ <STUDY_ID>_accelerometer.csv
                        ├─ <STUDY_ID>_gps.csv
                        └─ [other Ethica data stream files]
    
    CSV files are saved within a newly created <ethica_elite_files> 
    directory within the <CITY\WAVE_N> folder, i.e. at the same level
    as the <sensedoc> folder.

    Steps:
    1. Create <ethica_elite_files> subfolder within each city/wave;
        if folder already contains files, the processing of their
        interact_id/ethica_id combination will be removed from the processing
        queue 
    2. Search linkage file within each city/wave
    3. Extract metadata for all participants with Ethica data;
        store in pool worker argument list
    4. Run multiprocessing pool of workers
    5. Report back
    """
    # Store pool worker arguments in list of tuples
    # Arg = (interact_id, ethica_id, src_dir, dst_dir) / see single_load_transform
    wrk_args = []

    for ccode, city in cities.items():
        for wave in waves:
            # Check that city/wave folder exists, which is the case with test data...
            if not os.path.exists(os.path.join(src_dir, city, f'wave_{wave:02d}')):
                logging.warning(f'Unable to find subfolder <{os.path.join(city, f"wave_{wave:02d}")}>, skipping')
                continue
            # Create elite subfolder
            elite_folder = os.path.join(src_dir, city, f'wave_{wave:02d}', 'ethica_elite_files')
            existing_files = [] # store (interact_id, ethica_id, gps_found, axl_found)
            if os.path.exists(elite_folder):
                # Found a folder, all content will be scan to remove already processed GPS/AXL files from queue
                with os.scandir(elite_folder) as it:
                    existing_files_dict = {}
                    warned = False
                    for f in it:
                        m = re.match('(?P<iid>\\d+)_(?P<uid>\\d+)_(?P<sensor>GPS|AXL).csv', f.name)
                        if m is not None:
                            if not warned:
                                logging.warning(f'Elite folder <{os.path.relpath(elite_folder, src_dir)}> contains already processed files, which will be skipped')
                                warned = True
                            found = existing_files_dict.get((m.group('iid'), m.group('uid')), {})
                            found[m.group('sensor')] = 1
                            existing_files_dict[(m.group('iid'), m.group('uid'))] = found
                    # Restructure dict to list of tuples
                    for iid_uid, snsr in existing_files_dict.items():
                        iid, uid = iid_uid
                        existing_files.append((iid, uid, snsr.get('GPS', 0), snsr.get('AXL', 0)))
            else:
                os.mkdir(elite_folder)

            # Read linkage file and add corresponding args to list of worker args
            lk_file_path = os.path.join(src_dir, city, f'wave_{wave:02d}', f'linkage_{ccode}_w{wave}.csv')
            if not os.path.isfile(lk_file_path):
                logging.warning(f'Linkage file <{os.path.basename(lk_file_path)}> not found, skipping')
                continue
            if pd.__version__ < '2.2.0': # FutureWarning: Downcasting behavior in replace is deprecated" on a Series
                lk_df = pd.read_csv(lk_file_path, dtype=str).replace('0', pd.NA)
            else:
                with pd.option_context('future.no_silent_downcasting', True):
                    lk_df = pd.read_csv(lk_file_path, dtype=str).replace('0', pd.NA)

            # Keep only participants who did Ethicas
            lk_df = lk_df[['interact_id', 'ethica_id']].dropna().reset_index(drop=True)

            # Flag participant already processed, even partially
            processed_df = pd.DataFrame(existing_files, columns=['interact_id', 'ethica_id', 'gps_done', 'axl_done'])
            lk_df = lk_df.merge(processed_df, how='left')
            lk_df.loc[:,'process_gps'] = np.where(lk_df['gps_done'] == 1, False, True)
            lk_df.loc[:,'process_axl'] = np.where(lk_df['axl_done'] == 1, False, True)
            lk_df.drop(columns=['gps_done', 'axl_done'], inplace=True)

            # Display linkage file content for control
            logging.debug(f'Participants to process, according to linkage file <{os.path.basename(lk_file_path)}>:\n{lk_df.to_string()}')

            # Find all Ethica study data folder
            ethica_dir = os.path.join(src_dir, city, f'wave_{wave:02d}', 'ethica')
            subdirs = os.listdir(ethica_dir)
            studies = []
            not_found = True
            for sd in subdirs:
                # Looking for a folder with a simple number (~study id) as name
                m = re.fullmatch('\\d+', sd)
                if m:
                    not_found = False
                    studies.append(m[0])
            if not_found:
                logging.warning(f'{ccode}-{wave} | No subfolder named after study number found in Ethica data folder')
                continue

            # Load pid metadata for processing by pool of workers
            for pid in lk_df.itertuples(index=False):
                for sid in studies:
                    wrk_args.append((int(pid.interact_id), int(pid.ethica_id),
                                    os.path.join(ethica_dir, sid), elite_folder,
                                    city, f'Wave {wave}',
                                    pid.process_gps, pid.process_axl))
            
    # Multiprocessing run
    c0 = perf_counter()
    if ncpu > 1: # Switch to multiprocessing if more than 1 CPU
        logging.info(f'Multiprocessing with {ncpu} cores')
        with mp.Pool(processes=ncpu, maxtasksperchild=1) as pool:
            results = pool.starmap_async(single_load_transform, wrk_args)
            result_df = pd.DataFrame([r for r in results.get()], columns=['City', 'Wave', 'iid', 'uid', 'GPS', 'AXL']).convert_dtypes()
    else:
        # Single thread processing (for debug only)
        results = starmap(single_load_transform, wrk_args)
        result_df = pd.DataFrame([r for r in results], columns=['City', 'Wave', 'iid', 'uid', 'GPS', 'AXL']).convert_dtypes()

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

def single_load_transform_pl(ccode, wave, src_dir):
    """
    Extract/laod/transform Ethica data for one combination of city/wave.
    Load GPS and AXL data separately from the huge data files and split into
    inidividual CSV files. Leverage polars LazyFrame API to have a chance of
    chewing up those huge files.

    Parameters:
    -----------
    - ccode [str]: 
    - wave [int]:
    - src_dir: Path to data folder for the specified city/wave, i.e.
        .../data_archive/<city>/<wave>/
    - process_gps (optional): if true, GPS from sdb will be processed 
    - process_axl (optional): if true, accelerometry from sdb will be processed 

    Returns:
    --------
    A tuple with (city, wave, message)
    """

    # Check that city/wave folder exists, which is the case with test data...
    city = cities[ccode]
    if not os.path.exists(src_dir):
        msg = f'Unable to find subfolder <{src_dir}>'
        logging.warning(f'{msg}, skipping')
        return (city, wave, f'Error: {msg}')
    # Create elite subfolder
    elite_folder = os.path.join(src_dir, 'ethica_elite_files')
    existing_files = [] # store (interact_id, ethica_id, gps_found, axl_found)
    if os.path.exists(elite_folder):
        # Found a folder, all content will be scan to remove already processed GPS/AXL files from queue
        with os.scandir(elite_folder) as it:
            existing_files_dict = {}
            warned = False
            for f in it:
                m = re.match('(?P<iid>\\d+)_(?P<sensor>GPS|AXL).csv', f.name)
                if m is not None:
                    if not warned:
                        logging.warning('Elite folder contains already processed files, which will be skipped')
                        warned = True
                    found = existing_files_dict.get(m.group('iid'), {})
                    found[m.group('sensor')] = True
                    existing_files_dict[m.group('iid')] = found
            # Restructure dict to list of tuples
            for iid, snsr in existing_files_dict.items():
                existing_files.append((int(iid), snsr.get('GPS', False), snsr.get('AXL', False)))
    else:
        os.mkdir(elite_folder)

    # Read linkage file and add corresponding args to list of worker args
    lk_file_path = os.path.join(src_dir, f'linkage_{ccode}_w{wave}.csv')
    if not os.path.isfile(lk_file_path):
        msg = f'Linkage file <{os.path.basename(lk_file_path)}> not found'
        logging.warning(f'{msg}, skipping')
        return (city, wave, f'Error: {msg}')
    lk_df = pl.read_csv(lk_file_path)

    # Flag participant already processed, even partially
    if existing_files:
        processed_df = pl.DataFrame(existing_files, schema=['interact_id', 'gps_done', 'axl_done'], orient='row')
        lk_df = lk_df.join(processed_df, how='left', on='interact_id')
    else:
        # No existing files found
        lk_df = lk_df.with_columns(
            gps_done = pl.lit(False),
            axl_done = pl.lit(False)
        )

    # Create separate luts for GPS and AXL
    lut_gps_lf = lk_df.filter(~pl.col('gps_done')|pl.col('gps_done').is_null()).select(['interact_id', 'ethica_id']).lazy()
    lut_axl_lf = lk_df.filter(~pl.col('axl_done')|pl.col('axl_done').is_null()).select(['interact_id', 'ethica_id']).lazy()

    # Find all Ethica study data folder
    ethica_dir = os.path.join(src_dir, 'ethica')
    subdirs = os.listdir(ethica_dir)
    studies = []
    not_found = True
    for sd in subdirs:
        # Looking for a folder with a simple number (~study id) as name
        m = re.fullmatch('\\d+', sd)
        if m:
            not_found = False
            studies.append(m[0])
    if not_found:
        logging.warning(f'{ccode.upper()}-{wave} | No subfolder named after study number found in Ethica data folder')
        return (city, wave, 'Error: no valid study subfolder found')

    #### GPS ####
    # Read data files as polars LazyFrames
    gps_lfs = []
    for sid in studies:
        _gps_file = os.path.join(ethica_dir, sid, f'{sid}_gps.csv')
        _lf = pl.scan_csv(_gps_file).select(['user_id', 'device_id', 'record_time', 'accu', 'alt', 'bearing', 'lat', 'lon', 'provider', 'satellite_time', 'speed'])
        _lf = lut_gps_lf.join(_lf, how='inner', left_on='ethica_id', right_on='user_id')
        gps_lfs.append(_lf)
    gps_lf = pl.concat(gps_lfs) # Merge separate data files into on (even bigger!) LazyFrame for simplicity

    # Split LazyFrame into separate CSV
    def _file_path_provider_gps(args:FileProviderArgs) -> str:
        # Flagged as unstable, working as of polars 1.43
        return f'{args.partition_keys[0,0]}_GPS.csv'

    gps_lf.sink_csv(
        pl.PartitionBy( # Flagged as unstable, working as of polars 1.43
            elite_folder,
            key='interact_id',
            file_path_provider=_file_path_provider_gps,
            include_key=True
        ),
        mkdir=True
    )

    #### AXL ####
    # Read data files as polars LazyFrames
    axl_lfs = []
    for sid in studies:
        _axl_file = os.path.join(ethica_dir, sid, f'{sid}_accelerometer.csv')
        _lf = pl.scan_csv(_axl_file).select(['user_id', 'device_id', 'record_time', 'accu', 'x_axis', 'y_axis', 'z_axis'])
        _lf = lut_axl_lf.join(_lf, how='inner', left_on='ethica_id', right_on='user_id')
        axl_lfs.append(_lf)
    axl_lf = pl.concat(axl_lfs) # Merge separate data files into on (even bigger!) LazyFrame for simplicity

    # Split LazyFrame into separate CSV
    def _file_path_provider_axl(args:FileProviderArgs) -> str:
        # Flagged as unstable, working as of polars 1.43
        return f'{args.partition_keys[0,0]}_AXL.csv'

    axl_lf.sink_csv(
        pl.PartitionBy( # Flagged as unstable, working as of polars 1.43
            elite_folder,
            key='interact_id',
            file_path_provider=_file_path_provider_axl,
            include_key=True
        ),
        mkdir=True
    )

    return (city, wave, 'OK')


def load_transform_ethica_pl(src_dir, ncpu=1):
    """ Batch process all Ethica data to create Elite files,
    e.g. CSV files with raw GPS and AXL data.
    Data is expected to have been validated beforehand and follow
    the directory hierarchy defined in ReadMe file:
        <CITY>
            └─ <WAVE_N>
                └─ ethica
                    └─ <STUDY_ID>
                        ├─ <STUDY_ID>_accelerometer.csv
                        ├─ <STUDY_ID>_gps.csv
                        └─ [other Ethica data stream files]
    
    CSV files are saved within a newly created <ethica_elite_files> 
    directory within the <CITY\WAVE_N> folder, i.e. at the same level
    as the <sensedoc> folder.

    Steps:
    1. Create <ethica_elite_files> subfolder within each city/wave;
        if folder already contains files, the processing of their
        interact_id/ethica_id combination will be removed from the processing
        queue 
    2. Search linkage file within each city/wave
    3. Lazy scan/partition/sink the huge data files into individual CSV, using polars
    5. Report back

    Parameters:
    -----------
    - src_dir: Path to data folder for the specified city/wave, i.e.
        .../data_archive/
    - ncpu (default=1): number of CPU over which processing will be distributed
        NB: polars is already multiprocessor aware; we only distribute the load
        by city/wave combination to avoid having multiple processes access the
        same huge data file.
    """
    # Build list of args to by spread over CPUs
    wrk_args = [(ccode, wave, os.path.join(src_dir, city, f'wave_{wave:02d}')) for ccode, city in cities.items() for wave in waves]

    # Multiprocessing run
    c0 = perf_counter()
    if ncpu > 3: # Switch to multiprocessing if more than 3 CPU
        ncpu = int(ncpu/2) # Keep some CPU margin for polars MP capability. Anyway, bottleneck is probably I/O
        logging.info(f'Multiprocessing with {ncpu} cores')
        with mp.Pool(processes=ncpu, maxtasksperchild=1) as pool:
            results = pool.starmap_async(single_load_transform_pl, wrk_args)
            result_df = pd.DataFrame([r for r in results.get()], columns=['City', 'Wave', 'Message']).convert_dtypes()
    else:
        # Single thread processing (for debug only)
        results = starmap(single_load_transform, wrk_args)
        result_df = pd.DataFrame([r for r in results], columns=['City', 'Wave', 'Message']).convert_dtypes()
    print(result_df.to_markdown(index=False, tablefmt='presto'))
    print(f'DONE: {perf_counter() - c0:.1f}s')

if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S') #, level=logging.DEBUG)

    # Get target root folder as command line argument
    if len(sys.argv[1:]):
        root_data_folder = sys.argv[1]

    if not os.path.isdir(root_data_folder):
        logging.error(f'No directory <{root_data_folder}> found! Aborting')
        exit(1)

    # Get wave id to process
    if len(sys.argv[2:]):
        wave_id = int(sys.argv[2])
        if wave_id not in waves:
            logging.error(f'Invalid wave id <{wave_id}>! Aborting')
            exit(1)
        else:
            waves = [wave_id]

    ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK',default=1))
    load_transform_ethica_pl(root_data_folder, ncpus)