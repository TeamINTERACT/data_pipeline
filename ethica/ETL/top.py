"""Production of ToP (Table of power) from Ethica Data

ToP records aggregate the GPS and AXL data into the same table at 1 minute
epoch after imputation of AXL data.

Imputation of AXL data is done according to two approaches: Gaussian Process 
Variational Autoencoder (GPVAE) and MissForest, a random forest imputation
algorithm.

Recommended workflow (Bernard):
 1. Validate required columns.
 2. Parse timestamps and standardise timezone.
 3. Sort and deduplicate.
 4. Convert all axes to g.
 5. check for corrupted or implausible values;
 6. calculate one-second magnitude and ENMO;
 7. aggregate to minute level;
 8. create a complete minute grid;
 9. save the original missingness mask;
 10. split training and evaluation data before making windows;
 11. standardise deep-model inputs using training statistics only;
 12. fit the model;
 13. replace only originally missing values;
 14. reverse standardisation;
 15. recalculate magnitude and ENMO;
 16. save observed values, imputed values, timestamps, metadata, and missingness flags.

Records are saved directly in database, in tables under the top schema with
the following naming convention: top_ethica<WAVE>.top_<EPOCH>_<CITY_CODE>
--
USAGE: top.py [TARGET_ROOT_FOLDER [WAVE]]

If TARGET_ROOT_FOLDER not provided, will default to test data folder.
If WAVE is not provided, all waves (1-4) will be processed
"""
# Required to avoid bug in Pandas https://github.com/pandas-dev/pandas/issues/55025
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import sys
import re
import io
import logging
import contextlib
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text
from time import perf_counter
import multiprocessing as mp
from itertools import starmap
from geopy import distance
from pyproj import Transformer, CRS
from pygrinder import mcar

# A bit of hugly stuff to avoid the ASCII message when importing GPVAE
_stdout = sys.stdout
sys.stdout = open(os.devnull, "w", encoding="utf-8")
try:
    from pypots.imputation.gpvae import GPVAE
finally:
    sys.stdout.close()
    sys.stdout = _stdout

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
waves = [1, 2, 3, 4]

# DB credential, etc.
db_user = os.environ.get("USER", os.environ.get("USERNAME", ""))
db_host = "localhost" if os.environ.get("COMPUTERNAME", "") == "VOLVIC" else "cedar-pgsql-vm"

# Define base folder when not provided on the cmd line
root_data_folder = r'data\interact_test_data'
wave_id = None

# GPVAE hyperparameters (from Bernard's code)
def _pick_device() -> str:
    if os.environ.get("FORCE_CPU", "0") == "1":
        return "cpu"
    try:
        import torch  # noqa: F401
        return "cuda" if torch.cuda.is_available() else "cpu"
    except Exception:
        return "cpu"

DEVICE = _pick_device()
N_STEPS = 60
STRIDE = 60

GPVAE_INIT = dict(
    n_steps=N_STEPS,
    n_features=3, # 3D axl values
    latent_size=16,

    encoder_sizes=(64, 64),
    decoder_sizes=(64, 64),

    kernel="cauchy",
    beta=0.2,

    # training controls
    batch_size=128,
    epochs=50,
    patience=10,

    # model internals
    M=1,
    K=1,
    sigma=1.0,
    length_scale=7.0,
    kernel_scales=1,
    window_size=3,

    device=DEVICE,
    saving_path=None,
    verbose=True,
)

def single_top_produce(city_code:str, wave:int, root_elite_filename:str, dst_dir, overwrite=False):
    """
    Processing of a single participant's Ethica data.
    Load GPS and AXL data files, .

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

    # Extract Interact_id
    interact_id = os.path.basename(root_elite_filename)
    
    # Check existence of iid/sd_id top in DB
    top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')
    target_schema = f'top_ethica{"" if wave == 1 else wave}'
    target_table1min = f'top_1min_{city_code}'
    with top_con.begin() as conn:
        # Check 1 min ToP
        stmt = text(f"SELECT * FROM {target_schema}.{target_table1min} "
                    "WHERE interact_id = :interact_id LIMIT 1")
        stmt = stmt.bindparams(interact_id=interact_id)
        res = conn.execute(stmt).fetchone()
        if res is not None:
            if overwrite:
                stmt = text(f"DELETE FROM {target_schema}.{target_table1min} "
                    "WHERE interact_id = :interact_id")
                stmt = stmt.bindparams(interact_id=interact_id)
                conn.execute(stmt)
            else:
                logger.warning(f'Found participant #{interact_id} in {target_schema}.{target_table1min}, skipping')
                return (city_code, wave, os.path.basename(root_elite_filename), -1, 'interact_id found in database')
    
    # Build complete fileanmes to GPS & AXL elite files
    # TODO: check with Dan if we want to process participants with only AXL or GPS 
    gps_fname = f'{root_elite_filename}_GPS.csv'
    if not os.path.exists(gps_fname):
        logger.warning(f'Unable to find GPS elite file {os.path.basename(gps_fname)}, skipping')
        return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Missing file ({os.path.basename(gps_fname)})')
    axl_fname = f'{root_elite_filename}_AXL.csv'
    if not os.path.exists(axl_fname):
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
    cnt_1m_df = cnt_1m_df.reset_index()
    top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')
    with top_con.begin() as conn:
        try:
            cnt_1m_df.to_sql(name=target_table1min, schema=target_schema, con=conn, if_exists='append', index=False, chunksize=10000)
        except Exception as e:
            logger.error(f'Unexpected error while storing ToP in DB for <{os.path.basename(root_elite_filename)}>, skipping')
            return (city_code, wave, os.path.basename(root_elite_filename), 0, f'Error storing ToPs in database ({e})')
        
    # Save to disk
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
    target_schema = f'top_ethica{"" if wave == 1 else wave}'
    target_table1min = f'top_1min_{city_code}'

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
        conn.execute(text(f"COMMENT ON SCHEMA {target_schema} IS 'Ethica table of power for wave {wave}'"))
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
    gps_df = pd.read_csv(gps_elite_filename).drop(columns=['interact_id','ethica_id','device_id'])
    gps_df['record_time'] = pd.to_datetime(gps_df['record_time']) # Format YYYY-MM-DD HH:MM:SS.ssss+0000, decoded automatically to UTC timestamp
    gps_df['satellite_time'] = pd.to_datetime(gps_df['satellite_time']) # idem
    gps_df = gps_df.sort_values(by='satellite_time') # should be already sorted but who knows...

    # Clean fixes:
    # - drop 0, 0 and any out of range coordinates
    # - drop fixes with an apparent speed > max_speed (in km/h)
    # - remove time duplicates (keep the most accurate fix)
    gps_df['keep'] = True
    gps_df['keep'] = ~ ((gps_df.lat == 0) & (gps_df.lon == 0)) & gps_df.keep
    gps_df['keep'] = ~ ((gps_df.lat > 90) | (gps_df.lat < -90)) & gps_df.keep
    gps_df['keep'] = ~ ((gps_df.lon > 180) | (gps_df.lon < -180)) & gps_df.keep
    gps_df = gps_df[gps_df.keep]

    gps_df[['prev_satellite_time', 'prev_lat', 'prev_lon']] = gps_df[['satellite_time', 'lat', 'lon']].shift(1)
    valid_idx = gps_df[['satellite_time', 'lat', 'lon', 'prev_utcdate','prev_lat', 'prev_lon']].notna().all(axis=1)
    gps_df.loc[valid_idx, 'dist2prev'] = gps_df[valid_idx].apply(lambda x: distance.distance((x.lat, x.lon), (x.prev_lat, x.prev_lon)).m, axis=1)
    gps_df['app_speed'] = 3.6 * gps_df.dist2prev / (gps_df.satellite_time - gps_df.prev_satellite_time).dt.total_seconds()
    gps_df = gps_df.loc[gps_df.app_speed < max_speed].drop(columns=['keep', 'prev_satellite_time', 'prev_lat', 'prev_lon', 'dist2prev', 'app_speed'])

    gps_df = gps_df.sort_values(['satellite_time', 'accu']).drop_duplicates('satellite_time')
    gps_df = gps_df.reset_index(drop=True)

    return gps_df

def _load_clean_axl(axl_elite_filename:str) -> pd.DataFrame:
    """ Read AXL elite file and clean the measurements 
    
    Returns a pandas df"""
    axl_df = pd.read_csv(axl_elite_filename).drop(columns=['interact_id','ethica_id','device_id'])
    axl_df['record_time'] = pd.to_datetime(axl_df['record_time'])
    axl_df = axl_df.sort_values(by='record_time') # should be already sorted but who knows...

    # Not much cleaning here except getting rid of overlapping measurement periods
    axl_df = axl_df.drop_duplicates('record_time', keep='first')

    # Compute g from m/s^2 measurements
    g = 9.80665 # 1g in m/s^2
    axl_df[['x_axis','y_axis','z_axis']] = axl_df[['x_axis','y_axis','z_axis']] / g
    axl_df[['x_axis','y_axis','z_axis']] = axl_df[['x_axis','y_axis','z_axis']].astype(np.float32)
    axl_df = axl_df.reset_index(drop=True)

    return axl_df

def _resample1min_axl(axl_df: pd.DataFrame) -> pd.DataFrame:
    """ Resample raw AXL data to 1 minute epoch dataset
    by taking the mean of 3D accelerometer values and create
    NA rows for missing minute epoch in order to have a 
    continuous range of 1 minute epoch from min to max timestamps """
    axl_df['record_time'] = axl_df['record_time'].dt.floor('min')
    axl_df = axl_df.groupby('record_time', as_index=False)[['x_axis','y_axis','z_axis']].agg('mean')

    # Create continuous range of 1 minute epochs, from min to max ts
    full_time = pd.date_range(
        axl_df["record_time"].min(),
        axl_df["record_time"].max(),
        freq="1min",
    )
    axl_df = axl_df.set_index('record_time').reindex(full_time).rename_axis('record_time').reset_index()

    return axl_df

def _impute_axl_gpvae(axl1min_df: pd.DataFrame, gpvae_mdl: GPVAE) -> pd.DataFrame:
    """ Takes a 1-min epoch Ethica Axl dataframe and return a 1 minute
    imputed axl dataframe, using a pretrained Gaussian Process Variational 
    Autoencoder model """
    # TODO
    # Impute data using trained GPVAE model
    # 1. structure data to match requirements (fct: make_windows);
    #   keeping range indices of missing data
    # 2. impute data using model
    # 3. restore original non-missing data in imputed data
    raise NotImplemented()

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


def make_windows(min_df: pd.DataFrame, n_steps: int, stride: int):
    """ From Bernard's code
    Build the samples for training/validation/imputation of the 3D accel
    data through GP-VAE model
    
    Parameters:
    -----------
    min_df: the 1 minute epoch pooled dataset, mandatory columns:
        interact_id, wave, x, y, z
    n_steps: the window length (ie. number of consecutive minutes per window)
    stride: the span between one window and the following, in minutes
    """
    X_list, maps = [], []

    for (_, _), g in min_df.groupby(["interact_id", "wave"], sort=False):
        g = g.sort_values("record_time")
        vals = g[['x_axis','y_axis','z_axis']].to_numpy(dtype=np.float32)
        idxs = g.index.to_numpy()

        T = len(g)
        start = 0
        while start + n_steps <= T:
            sl = slice(start, start + n_steps)
            X_list.append(vals[sl])
            maps.append(idxs[sl])
            start += stride

    if not X_list:
        return np.empty((0, n_steps, 3), dtype=np.float32), []

    return np.stack(X_list, axis=0), maps

def _wrapper_make1min_axl(wave, interact_id, raw_axl_file, target_dir):
    """ Helper function to read, resample and store AXL file for each
    interact_id/wave. Resampled files are stored in the target_dir and
    named according the the pattern axl1min_<wave>_<interact_id>.feather.

    Add wave and interact_id identifiers to help with pooled training.
    
    Feather file format is chosen for its read/write performance"""
    axl_df = _load_clean_axl(raw_axl_file)
    axl_df = _resample1min_axl(axl_df)
    axl_df.insert(0, 'wave', wave)
    axl_df.insert(1, 'interact_id', interact_id)
    # save reseampled dataframe to file for reuse
    outfile = os.path.join(target_dir, f'axl1min_{wave}_{interact_id}.feather')
    axl_df.to_feather(outfile)
    return axl_df

def train_gpvae_model(src_dir, train_split=.8, ncpu=1) -> GPVAE:
    """ Train a GP-VAE model for accelerometer data imputation at 
    the 1 minute epoch.
    All participants' raw axl files are read, then resampled at 
    the 1 minute epoch and pooled to train the model. Train_split percents of
    participants are used for training, while the remaining is used for validation.

    NB: 1 minute resampled axl data is temporarily stored in directory
    to allow reusing them for imputation.
    """
    # Create tmp dir where resampled 1 min data will be saved for reuse
    tmpdir = os.environ.get('SCRATCH', os.environ.get('TEMP', ''))
    tmpdir = os.path.join(tmpdir, 'axl1min')
    os.makedirs(tmpdir, exist_ok=True)

    # Store pool worker arguments in list of tuples
    # Arg = (wave, interact_id, axl_filename, target_dir) / see _wrapper_make1min_axl
    wrk_args = set()

    src_dir = os.path.abspath(src_dir)
    for ccode, city in cities.items():
        for wave in waves:
            # Build ethica elite file folder path, it should already exist
            elite_folder = os.path.join(src_dir, city, f'wave_{wave:02d}', 'ethica_elite_files')
            if not os.path.exists(elite_folder):
                logger.warning(f'Unable to find elite subfolder <{os.path.relpath(elite_folder, src_dir)}>, skipping')
                continue

            # Found a folder, add all axl files to queue
            with os.scandir(elite_folder) as it:
                for f in it:
                    if re.match('^\\d+_AXL.csv$', f.name):
                        # AXL raw file, let's get what we need: interact_id
                        interact_id = int(re.match('^\\d+', f.name)[0])
                        axl_fname = os.path.abspath(f.path)
                        wrk_args.add((wave, interact_id, axl_fname, tmpdir))

    # Multiprocessing resampling to 1 minute
    # Provide a pooled dataframe with resampled axl measures for all participants
    c0 = perf_counter()
    if ncpu > 1: # Switch to multiprocessing if more than 1 CPU
        with mp.Pool(processes=ncpu, maxtasksperchild=1) as pool:
            results = pool.starmap_async(_wrapper_make1min_axl, wrk_args)
            pooled_axl_df = pd.concat([r for r in results.get()])
    else:
        # Single thread processing (for debug only)
        results = starmap(_wrapper_make1min_axl, wrk_args)
        pooled_axl_df = pd.concat([r for r in results])

    # Train GPVAE on the pooled df
    # 1. load GPVAE hyperparameters
    # 2. split training and validation data; split by participant/wave, 
    #   not randomly from samples to avoid destroying the temporal 
    #   structure of timeseries
    # 3. make both dataset ready for GPVAE input (fct: make_windows)
    # 4. init GPVAE model and fit training/validation data
    pooled_axl_df['dummy_id'] = pooled_axl_df["interact_id"].astype(str).str.cat(pooled_axl_df["wave"].astype(str), sep='-')
    participants = pooled_axl_df["dummy_id"].unique()
    rng = np.random.default_rng(42)
    rng.shuffle(participants)

    n_train = max(1, int(train_split * len(participants)))
    val_ids = set(participants[n_train:])
    train_ids = set(participants[:n_train])

    train_df = pooled_axl_df[pooled_axl_df["dummy_id"].isin(train_ids)].drop(columns='dummy_id')
    val_df   = pooled_axl_df[pooled_axl_df["dummy_id"].isin(val_ids)].drop(columns='dummy_id')

    X_train, _ = make_windows(train_df, n_steps=N_STEPS, stride=STRIDE)
    X_val_ori, _   = make_windows(val_df,   n_steps=N_STEPS, stride=STRIDE)

    # GPVAE requires validation set with ground truth + missing data
    # we use pygrinder.mcar to generate randomly missing data
    X_val = mcar(X_val_ori, p=.1)

    # Init GPVAE and train/vaidate model
    GPVAE_INIT['saving_path'] = tmpdir
    gpvae_mdl = GPVAE(**GPVAE_INIT)
    gpvae_mdl.fit({'X':X_train}, {'X':X_val, 'X_ori': X_val_ori})
    gpvae_mdl.save(os.path.join(tmpdir, 'gpvae_mdl'), overwrite=True)

    return gpvae_mdl

def top_produce_ethica(src_dir, ncpu=1):
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
            # Check if city has no SD data, then skip. This happened at w4 for skt and van
            if wave == 4 and ccode in ['van', 'skt']:
                continue

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

    # Get wave id to process
    if len(sys.argv[2:]):
        wave_id = int(sys.argv[2])
        if wave_id not in waves:
            logging.error(f'Invalid wave id <{wave_id}>! Aborting')
            exit(1)
        else:
            waves = [wave_id]

    ncpu = int(os.environ.get('SLURM_CPUS_PER_TASK',default=6))
    c0 = perf_counter()
    m = train_gpvae_model(root_data_folder, ncpu=ncpu)
    print(m)
    print(f'Done {perf_counter() - c0:.2f}')
    #top_produce_sd(root_data_folder, ncpus)
