"""Production of ToP (Table of power) from SenseDoc Data

ToP records aggregate the GPS and AXL data into the same table at various
epochs, 1 second epoch being the base epoch from which other aggregation
levels may be built.

For SenseDoc data, 1 minute epoch table is also created along with a
series of additional metrics that help using the data (see data dictionary)

Records are saved directly in database, in tables under the top schema with
the following naming convention: top.SD_<EPOCH>_<CITY_CODE><WAVE>
--
USAGE: top.py [TARGET_ROOT_FOLDER]

If TARGET_ROOT_FOLDER not provided, will default to test data folder.
"""
# Required to avoid bug in Pandas https://github.com/pandas-dev/pandas/issues/55025
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from time import perf_counter
import multiprocessing as mp
from itertools import starmap
from geopy import distance
from pyproj import Transformer, CRS

# Reused from past work (Kole, Ruben)
from activity_count import counts
from wear_time import marking

# create module logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
ch.setFormatter(formatter)
logger.addHandler(ch)


# Define city_id and wave_id
cities = {'mtl': 'montreal', 
          'skt': 'saskatoon', 
          'van': 'vancouver', 
          'vic': 'victoria'}
waves = [1, 2, 3]

# DB credential, etc.
db_user = os.environ.get("USER", os.environ.get("USERNAME", ""))
db_host = "localhost" if os.environ.get("COMPUTERNAME", "") == "VOLVIC" else "cedar-pgsql-vm"

# Define base folder when not provided on the cmd line
root_data_folder = 'data\interact_test_data'


def single_top_produce(city_code:str, wave:int, root_elite_filename:str, dst_dir, overwrite=False):
    """
    Processing of a single participant's SD data.
    Load GPS and AXL data separately from sdb file, filter records to keep only
    measurements within start and end dates, then save each of the two streams 
    to a CSV file with interact_id, timestamp followed by axl/gps measurements.

    Parameters:
    -----------
    - city_code: one of cities dict key, used to identify target table name in database 
    - wave: used to identify target table name in database
    - root_elite_filename: root elite filename, i.e. without extension nor _GPS/_AXL;
        filenames contain participant ID and SenseDoc ID
    - dst_dir: Path where newly created ToP CSV files (one for 1s epoch, one for 1m epoch) will
        be saved 
    - overwrite (optional): if data for participant & SenseDoc is already stored in DB,
        should it be replaced. If not, ToP for this combination of participant & SenseDoc
        is skipped. 

    Returns:
    --------
    A tuple with (city, wave, root_elite_filename, status_code, status_details)

    Notes:
    ------
    - Cleaning (TODO: add description)
    - Additional metrics (TODO: add description)
    """
    logger.debug(f'PID {mp.current_process().pid}: processing {os.path.basename(root_elite_filename)}')

    # A bit of checking needed here:
    if wave not in waves:
        logger.error(f'Invalid wave {wave}')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, 'Error (Invalid wave)')
    if city_code not in cities:
        logger.error(f'Invalid city code {city_code}')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, 'Error (Invalid city code)')

    # Extract Interact_id and sd_id
    try:
        interact_id, sd_id = os.path.basename(root_elite_filename).split('_')
    except Exception as e:
        logger.error(f'Unable to parse IID / SDID from elite filename {os.path.basename(root_elite_filename)}')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Error parsing ids ({e})')
    
    # Check existence of iid/sd_id top in DB
    top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')
    target_schema = f'top_sd{"" if wave == 1 else wave}'
    target_table1sec = f'top_1sec_{city_code}'
    target_table1min = f'top_1min_{city_code}'
    with top_con.begin() as conn:
        # Check 1 sec ToP
        stmt = text(f"SELECT * FROM {target_schema}.{target_table1sec} "
                    "WHERE interact_id = :interact_id AND sd_id = :sd_id LIMIT 1")
        stmt = stmt.bindparams(interact_id=interact_id,
                               sd_id=sd_id)
        res = conn.execute(stmt).fetchone()
        if res is not None:
            if overwrite:
                stmt = text(f"DELETE FROM {target_schema}.{target_table1sec} "
                    "WHERE interact_id = :interact_id AND sd_id = :sd_id")
                stmt = stmt.bindparams(interact_id=interact_id,
                               sd_id=sd_id)
                conn.execute(stmt)
                
                stmt = text(f"DELETE FROM {target_schema}.{target_table1min} "
                    "WHERE interact_id = :interact_id AND sd_id = :sd_id")
                stmt = stmt.bindparams(interact_id=interact_id,
                               sd_id=sd_id)
                conn.execute(stmt)
            else:
                logger.warning(f'Found participant #{interact_id}/sd #{sd_id} in {target_schema}.{target_table1sec}, skipping')
                return (city_code, wave, os.path.basename(root_elite_filename), -1, 'interact_id/sd_id found in database')
            
        # Check 1 min ToP
        stmt = text(f"SELECT * FROM {target_schema}.{target_table1min} "
                    "WHERE interact_id = :interact_id AND sd_id = :sd_id LIMIT 1")
        stmt = stmt.bindparams(interact_id=interact_id,
                               sd_id=sd_id)
        res = conn.execute(stmt).fetchone()
        if res is not None:
            if overwrite:
                stmt = text(f"DELETE FROM {target_schema}.{target_table1sec} "
                    "WHERE interact_id = :interact_id AND sd_id = :sd_id")
                stmt = stmt.bindparams(interact_id=interact_id,
                               sd_id=sd_id)
                conn.execute(stmt)

                stmt = text(f"DELETE FROM {target_schema}.{target_table1min} "
                    "WHERE interact_id = :interact_id AND sd_id = :sd_id")
                stmt = stmt.bindparams(interact_id=interact_id,
                               sd_id=sd_id)
                conn.execute(stmt)
            else:
                logger.warning(f'Found participant #{interact_id}/sd #{sd_id} in {target_schema}.{target_table1min}, skipping')
                return (city_code, wave, os.path.basename(root_elite_filename), -1, 'interact_id/sd_id found in database')
    
    # Build complete fileanmes to GPS & AXL elite files
    gps_fname = f'{root_elite_filename}_GPS.csv'
    if not os.path.exists(gps_fname):
        logger.warning(f'Unable to find GPS elite file {os.path.basename(gps_fname)}, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Missing file ({os.path.basename(gps_fname)})')
    axl_fname = f'{root_elite_filename}_AXL.csv'
    if not os.path.exists(gps_fname):
        logger.warning(f'Unable to find AXL elite file {os.path.basename(axl_fname)}, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Missing file ({os.path.basename(axl_fname)})')
    
    # Load and clean data
    try:
        gps_df = _load_clean_gps(gps_fname)
    except Exception as e:
        logger.error(f'Unable to load GPS data from {os.path.basename(gps_fname)}, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Error loading GPS ({e})')
    if gps_df.empty:
        logger.error(f'No GPS data in {os.path.basename(gps_fname)}, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Empty GPS file')
    try:
        axl_df = _load_clean_axl(axl_fname)
    except Exception as e:
        logger.error(f'Unable to load AXL data from {os.path.basename(axl_fname)}, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Error loading AXL ({e})')
    if axl_df.empty:
        logger.error(f'No AXL data in {os.path.basename(axl_fname)}, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Empty AXL file')

    # Process 1sec epoch
    try:
        c0 = perf_counter()
        cnt_1s_df = _top_1sec(interact_id, sd_id, gps_df, axl_df)
        c1 = perf_counter()
        logger.info(f'Participant # {interact_id}: ToP 1sec done [{c1-c0:.1f}s]')
    except Exception as e:
        logger.error(f'Unexpected error in ToP 1sec for <{os.path.basename(root_elite_filename)}>, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Error computing ToP 1sec ({e})')

    # Process 1min epoch
    try:
        c0 = perf_counter()
        cnt_1m_df = _top_1min(cnt_1s_df)
        c1 = perf_counter()
        logger.info(f'Participant # {interact_id}: ToP 1min done [{c1-c0:.1f}s]')
    except Exception as e:
        logger.error(f'Unexpected error in ToP 1min for <{os.path.basename(root_elite_filename)}>, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Error computing ToP 1min ({e})')
    
    # Store ToPs in DB
    cnt_1s_df = cnt_1s_df.reset_index()
    cnt_1m_df = cnt_1m_df.reset_index()
    top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')
    with top_con.begin() as conn:
        try:
            cnt_1s_df.to_sql(name=target_table1sec, schema=target_schema, con=conn, if_exists='append', index=False, chunksize=10000)
            cnt_1m_df.to_sql(name=target_table1min, schema=target_schema, con=conn, if_exists='append', index=False, chunksize=10000)
        except Exception as e:
            logger.error(f'Unexpected error while storing ToP in DB for <{os.path.basename(root_elite_filename)}>, skipping')
            return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Error storing ToPs in database ({e})')
        
    # Save to disk
    cnt_1s_df.insert(0, 'city_id', city_code)
    cnt_1s_df.insert(1, 'wave_id', wave)
    cnt_1s_df.insert(2, 'epoch_seconds', 1)
    fname_top1sec = os.path.join(dst_dir, f'{os.path.basename(root_elite_filename)}_top1sec.csv')
    cnt_1s_df.convert_dtypes().to_csv(fname_top1sec, index=False)

    cnt_1m_df.insert(0, 'city_id', city_code)
    cnt_1m_df.insert(1, 'wave_id', wave)
    cnt_1m_df.insert(2, 'epoch_seconds', 60)
    fname_top1min = os.path.join(dst_dir, f'{os.path.basename(root_elite_filename)}_top1min.csv')
    cnt_1m_df.convert_dtypes().to_csv(fname_top1min, index=False)

    return (city_code, wave, os.path.basename(root_elite_filename), 1, 'Ok')


def execute_ddl_top(city_code:str, wave:int):
    """ Create necessary schemas and tables for ToPs
    """
    # A bit of checking needed here:
    if wave not in waves:
        raise ValueError(f'Invalid wave {wave}')
    if city_code not in cities:
        raise ValueError(f'Invalid city code {city_code}')

    top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')
    target_schema = f'top_sd{"" if wave == 1 else wave}'
    target_table1sec = f'top_1sec_{city_code}'
    target_table1min = f'top_1min_{city_code}'

    # ToP 1 second table definition
    stmt_ddl_top1sec = f"""
        CREATE TABLE IF NOT EXISTS {target_schema}.{target_table1sec} (
            interact_id INTEGER,
            sd_id SMALLINT,
            utcdate TIMESTAMP WITH TIME ZONE,
            count_x INTEGER,
            count_y INTEGER,
            count_z INTEGER,
            count_vm REAL,
            lat REAL,
            lon REAL,
            speed REAL,
            course REAL,
            mode TEXT,
            fix TEXT,
            alt REAL,
            mode1 TEXT,
            mode2 SMALLINT,
            sat_used SMALLINT,
            pdop REAL,
            hdop REAL,
            vdop REAL,
            sat_in_view SMALLINT,
            CONSTRAINT {target_schema}_{target_table1sec}_pk PRIMARY KEY (interact_id, sd_id, utcdate)
    )"""

    # ToP 1 minute table definition
    stmt_ddl_top1min = f"""
        CREATE TABLE IF NOT EXISTS {target_schema}.{target_table1min} (
            interact_id INTEGER,
            sd_id SMALLINT,
            utcdate TIMESTAMP WITH TIME ZONE,
            count_x INTEGER,
            count_y INTEGER,
            count_z INTEGER,
            count_vm REAL,
            lat REAL,
            lon REAL,
            alt REAL,
            wearing SMALLINT,
            CONSTRAINT {target_schema}_{target_table1min}_pk PRIMARY KEY (interact_id, sd_id, utcdate)
    )"""

    with top_con.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {target_schema}"))
        conn.execute(text(f"COMMENT ON SCHEMA {target_schema} IS 'SenseDoc table of power for wave {wave}'"))
        conn.execute(text(stmt_ddl_top1sec))
        conn.execute(text(stmt_ddl_top1min))


def _get_planimetric_coords(lat_lon_alt_df:pd.DataFrame) -> pd.DataFrame:
    """ Project the coords in dataframe (columns: lat; lon; alt) to
    NAD83 / Statistics Canada Lambert.
    Any lat/lon outside AOI get NaN
    """
    # Define transformer WGS84 -> LCC
    wgs = CRS(4326)
    lcc = CRS(3347)
    lcc_area = lcc.area_of_use
    t = Transformer.from_crs(wgs, lcc)

    # Project lat/lon to planimetric coordinates
    x, y, z = t.transform(lat_lon_alt_df['lat'],
                          lat_lon_alt_df['lon'],
                          lat_lon_alt_df['alt'])
    lcc_df = pd.DataFrame({'x': x,
                           'y': y,
                           'z': z,
                           'lat': lat_lon_alt_df['lat'],
                           'lon': lat_lon_alt_df['lon']})

    # Reset coords outside Caanada
    lcc_df.loc[lcc_df['lon'] < lcc_area.west, ['x', 'y', 'z']] = None
    lcc_df.loc[lcc_df['lon'] > lcc_area.east, ['x', 'y', 'z']] = None
    lcc_df.loc[lcc_df['lat'] < lcc_area.south, ['x', 'y', 'z']] = None
    lcc_df.loc[lcc_df['lat'] > lcc_area.north, ['x', 'y', 'z']] = None

    return lcc_df.drop(columns=['lat','lon'])


def _get_geographic_coords(x_y_z_df:pd.DataFrame) -> pd.DataFrame:
    """ Project the coords in dataframe (columns: x; y; z) to WGS84
    """
    # Define transformer WGS84 -> LCC
    wgs = CRS(4326)
    lcc = CRS(3347)
    t = Transformer.from_crs(lcc, wgs)

    # Project lat/lon to planimetric coordinates
    lat, lon, alt = t.transform(x_y_z_df['x'],
                          x_y_z_df['y'],
                          x_y_z_df['z'])
    geo_df = pd.DataFrame({'lat': lat,
                           'lon': lon,
                           'alt': alt})
    return geo_df


def _load_clean_gps(gps_elite_filename:str, max_speed=300) -> pd.DataFrame:
    """ Read GPS elite file and clean the fixes, including by removing
    fixes with a speed over max_speed (in km/h)
    
    Returns a pandas df"""
    gps_df = pd.read_csv(gps_elite_filename).drop(columns="interact_id")
    gps_df['utcdate'] = pd.to_datetime(gps_df['utcdate'], format="%Y-%m-%d %H:%M:%S", utc=True)
    gps_df = gps_df.sort_values(by='utcdate') # should be already sorted but who knows...

    # Clean fixes:
    # - drop 0, 0 and any out of range coordinates
    # - drop fixes with an apparent speed > max_speed (in km/h)
    # - remove time duplicates (keep the last, as for )
    gps_df['keep'] = True
    gps_df['keep'] = ~ ((gps_df.lat == 0) & (gps_df.lon == 0)) & gps_df.keep
    gps_df['keep'] = ~ ((gps_df.lat > 90) | (gps_df.lat < -90)) & gps_df.keep
    gps_df['keep'] = ~ ((gps_df.lon > 180) | (gps_df.lon < -180)) & gps_df.keep
    gps_df = gps_df[gps_df.keep]

    gps_df[['prev_utcdate', 'prev_lat', 'prev_lon']] = gps_df[['utcdate', 'lat', 'lon']].shift(1)
    valid_idx = gps_df[['utcdate', 'lat', 'lon', 'prev_utcdate','prev_lat', 'prev_lon']].notna().all(axis=1)
    gps_df.loc[valid_idx, 'dist2prev'] = gps_df[valid_idx].apply(lambda x: distance.distance((x.lat, x.lon), (x.prev_lat, x.prev_lon)).m, axis=1)
    gps_df['app_speed'] = 3.6 * gps_df.dist2prev / (gps_df.utcdate - gps_df.prev_utcdate).dt.total_seconds()
    gps_df = gps_df.loc[gps_df.app_speed < max_speed].drop(columns=['keep', 'prev_utcdate', 'prev_lat', 'prev_lon', 'dist2prev', 'app_speed'])

    gps_df = gps_df.drop_duplicates('utcdate', keep='last')
    gps_df = gps_df.reset_index(drop=True)

    return gps_df

def _load_clean_axl(axl_elite_filename:str) -> pd.DataFrame:
    """ Read AXL elite file and clean the measurements 
    
    Returns a pandas df"""
    axl_df = pd.read_csv(axl_elite_filename).drop(columns="interact_id")
    axl_df['utcdate'] = pd.to_datetime(axl_df['utcdate'], format="%Y-%m-%d %H:%M:%S.%f", utc=True)
    axl_df = axl_df.sort_values(by='utcdate') # should be already sorted but who knows...

    # Not much cleaning here except getting rid of overlapping measurement periods:
    # we keep the last measurements as they are supposed to be less prone to RTC drift
    # (because they are closer to a clock resynch')
    axl_df = axl_df.drop_duplicates('utcdate', keep='last')

    # Cast g-measurements to float32, to drop unnecessary precision and save space
    axl_df[['x', 'y', 'z']] = axl_df[['x', 'y', 'z']].astype(np.float32)
    axl_df = axl_df.reset_index(drop=True)

    return axl_df


def _top_1sec(interact_id, sd_id, gps_df:pd.DataFrame, axl_df:pd.DataFrame) -> pd.DataFrame:
    """ Compute the ToP at the 1 second epoch
    
    Returns a pandas df, with utcdate index"""

    # Compute axl sampling frequency, which is needed for AG counts
    _delta_smp_sec = (axl_df['utcdate'] - axl_df['utcdate'].shift(1)).dt.total_seconds()
    axl_delta = np.median(_delta_smp_sec.dropna())
    axl_fs = int(round(1 / axl_delta))
    if axl_fs < 30:
        # Brond's algo requires sampling freq to be at least 30Hz
        logger.warning(f'AXL data for participant #{interact_id} / {sd_id} below threshold ({axl_fs} Hz), skipping')
        return pd.DataFrame()

    # Resample and fill gaps of AXL
    # NB: using resample() instead of asfreq() to keep measurements falling
    # on timestamps dropped once resampled
    axl_df = axl_df.set_index('utcdate')
    axl_df = axl_df.resample(f'{axl_delta}S').median()
    axl_df = axl_df.fillna(method='ffill')

    # Compute Actigraph counts, using J. Brond algo
    cnt_x = counts(axl_df['x'], axl_fs).astype(int)
    cnt_y = counts(axl_df['y'], axl_fs).astype(int)
    cnt_z = counts(axl_df['z'], axl_fs).astype(int)
    cnt_vm = np.sqrt(cnt_x**2 + cnt_y**2 + cnt_z**2) # Compute 3D vector magnitude
    cnt_idx = pd.date_range(axl_df.index[0], periods=len(cnt_x), freq='1S', name='utcdate')
    cnt_df = pd.DataFrame({'count_x': cnt_x,
                           'count_y': cnt_y,
                           'count_z': cnt_z,
                           'count_vm': cnt_vm},
                           index=cnt_idx)

    # Merge with GPS data and return
    cnt_df = cnt_df.join(gps_df.set_index('utcdate'), on='utcdate')
    cnt_df.insert(0, 'interact_id', int(interact_id))
    cnt_df.insert(1, 'sd_id', int(sd_id))
    return cnt_df


def _top_1min(top_1sec:pd.DataFrame) -> pd.DataFrame:
    """ Compute the ToP at the 1 minute epoch
    
    Returns a pandas df, with utcdate index"""

    # Any aggregation on coords need to be done on planimetric coordinates
    xyz_df = _get_planimetric_coords(top_1sec)
    xyz_df.index = top_1sec.index

    # Aggregate 1sec epoch into 1min epoch
    # - suming counts
    cnt_1min_df = top_1sec.resample('1min').agg({'interact_id': 'first',
                                                 'sd_id': 'first',
                                                 'count_x': 'sum',
                                                 'count_y': 'sum',
                                                 'count_z': 'sum'})
    cnt_1min_df['count_vm'] = np.sqrt(cnt_1min_df['count_x']**2 + cnt_1min_df['count_y']**2 + cnt_1min_df['count_z']**2)

    # - median location for GPS
    loc_1min_df = xyz_df.resample('1min').median()
    locll_1min_df = _get_geographic_coords(loc_1min_df) # Reproject into wgs84
    locll_1min_df.index = loc_1min_df.index

    top_df = cnt_1min_df.join(locll_1min_df, on='utcdate')

    # Mark wear/non-wear period and return
    top_df = marking(top_df, 90)
    return top_df


def top_produce_sd(src_dir, ncpu=None):
    """ Batch process all SenseDoc Elite files, which are a pair of CSV files 
    with raw GPS and AXL data.
    Data is expected to have been validated beforehand and follow
    the directory hierarchy defined in ReadMe file:
        <CITY>
          |
          +- <WAVE_N>
               |
               +- <sensedoc_elite_files>
                    |
                    +- GPS and AXL elite files
    
    Steps:
    1. Create schemas/tables in database if required as well as <sensedoc_top_files> 
        subfolder within each city/wave
    2. Scan elite file subfolder and store in pool worker argument list
    3. Run multiprocessing pool of workers
    4. Report back
    """
    # Store pool worker arguments in list of tuples
    # Arg = (city_code, wave, root_elite_filename, overwrite) / see single_top_produce
    wrk_args = set()

    src_dir = os.path.abspath(src_dir)
    for ccode, city in cities.items():
        for wave in waves:
            # Create the required schemas/tables fro top
            execute_ddl_top(ccode, wave)

            # Create top subfolder
            top_folder = os.path.join(src_dir, city, f'wave_{wave:02d}', 'sensedoc_top_files')
            Path(top_folder).mkdir(parents=True, exist_ok=True)

            # Check that city/wave folder exists, which is the case with test data...
            elite_folder = os.path.join(src_dir, city, f'wave_{wave:02d}', 'sensedoc_elite_files')
            if not os.path.exists(elite_folder):
                logger.warning(f'Unable to find elite subfolder <{os.path.relpath(elite_folder, src_dir)}>, skipping')
                continue

            # Found a folder, all content will be scan to add GPS/AXL combination to queue
            with os.scandir(elite_folder) as it:
                for f in it:
                    root_elite_fname = os.path.abspath(f.path)
                    root_elite_fname = root_elite_fname.removesuffix("_AXL.csv")
                    root_elite_fname = root_elite_fname.removesuffix("_GPS.csv")
                    wrk_args.add((ccode, wave, root_elite_fname, top_folder, False))
                                    
    # Multiprocessing run
    c0 = perf_counter()
    if ncpu > 1: # Switch to multiprocessing if more than 1 CPU
        logger.info(f'Multiprocessing with {ncpu} cores')
        with mp.Pool(processes=ncpu, maxtasksperchild=1) as pool:
            results = pool.starmap_async(single_top_produce, wrk_args)
            result_df = pd.DataFrame([r for r in results.get()], columns=['City', 'Wave', 'Filename', 'Status', 'Details']).convert_dtypes()
    else:
        # Single thread processing (for debug only)
        results = starmap(single_top_produce, wrk_args)
        result_df = pd.DataFrame([r for r in results], columns=['City', 'Wave', 'Filename', 'Status', 'Details']).convert_dtypes()

    print(result_df)

    # Display stats on computation
    print('==== PROCESSING REPORT | ToP ====')
    result_gps_df = result_df.groupby(['City', 'Wave', 'Status'], as_index=False).size()
    result_gps_df.loc[result_gps_df['Status'] == 0,'ToP Status'] = 'Error'
    result_gps_df.loc[result_gps_df['Status'] == 1,'ToP Status'] = 'OK'
    result_gps_df.loc[result_gps_df['Status'] == -1,'ToP Status'] = 'Skipped'
    result_gps_df = result_gps_df.pivot(index=['City', 'Wave'], columns='ToP Status', values='size').fillna(0).convert_dtypes()
    print(result_gps_df.reset_index().to_markdown(index=False, tablefmt='presto'))
    print(f'DONE: {perf_counter() - c0:.1f}s')

if __name__ == '__main__':
    # Get target root folder as command line argument
    if len(sys.argv[1:]):
        root_data_folder = sys.argv[1]

    if not os.path.isdir(root_data_folder):
        logger.error(f'No directory <{root_data_folder}> found! Aborting')
        exit(1)

    ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK',default=6))
    top_produce_sd(root_data_folder, ncpus)
