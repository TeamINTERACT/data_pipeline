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
    lk_df = pl.read_csv(lk_file_path, null_values='NA').filter(pl.col('interact_id').is_not_null())

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
        _lf = pl.scan_csv(_gps_file, schema_overrides={
                'bearing': pl.Float64,
                'speed': pl.Float64
            }).select(['user_id', 'device_id', 'record_time', 'accu', 'alt', 'bearing', 'lat', 'lon', 'provider', 'satellite_time', 'speed'])
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