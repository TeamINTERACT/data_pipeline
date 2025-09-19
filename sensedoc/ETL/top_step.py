"""Production of step counts from SenseDoc accelerometer data, 
merged into ToP 

Steps are extracted thanks to a model trained on UK Biobank dataset 
and published in Yuan, H., Chan, S., Creagh, A.P. et al. Self-supervised 
learning for human activity recognition using 700,000 person-days of 
wearable data. npj Digit. Med. 7, 91 (2024). 
(https://doi.org/10.1038/s41746-024-01062-3).

The actual Python module is available at https://github.com/OxWearables/stepcount

Although the model produces steps at various epochs, only the minute 
level is retained and merged into the 1-minute ToP. The follwoing fields are
added to the ToP:
 - steps: number of steps
 - enmo: Euclidean norm minus one and zero-truncated, measured in milli-g.
 - steps_adj: adjusted number of steps
 - enmo_adj: adjusted ENMO
According to help: Crude estimates represent raw metrics calculated directly 
from observed data. Adjusted estimates compensate for missing time-series 
values by imputing each absent timepoint with the average value at that same 
clock time across all other recorded days. To derive adjusted totals and daily 
summaries, any gaps in the required 24‑hour span are similarly imputed; if 
data remain missing after this process, the estimate is reported as NaN.
--
USAGE: stepcount.py [TARGET_ROOT_FOLDER]

If TARGET_ROOT_FOLDER not provided, will default to test data folder.
"""

import os
import sys
import logging
import pandas as pd
from tempfile import NamedTemporaryFile
from sqlalchemy import create_engine, text
import multiprocessing as mp
from itertools import starmap

# stepcount module, see https://github.com/OxWearables/stepcount
from stepcount import stepcount

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

# Define temporary folder to store reformatted CSV file as well as scratch folder
tmp_folder = os.environ.get("SLURM_TMPDIR", 'data/tmp')
scratch_folder = os.environ.get("SCRATCH", 'data/tmp')

def execute_alter_top(city_code:str, wave:int):
    """ Add required new colukns in ToPs
    """
    # A bit of checking needed here:
    if wave not in waves:
        raise ValueError(f'Invalid wave {wave}')
    if city_code not in cities:
        raise ValueError(f'Invalid city code {city_code}')

    top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')
    target_schema = f'top_sd{"" if wave == 1 else wave}'
    target_table1min = f'top_1min_{city_code}'

    # ToP 1 minute table new columns
    stmt_ddl_top1min = f"""
        ALTER TABLE {target_schema}.{target_table1min}
            ADD COLUMN IF NOT EXISTS steps INTEGER,
            ADD COLUMN IF NOT EXISTS enmo FLOAT,
            ADD COLUMN IF NOT EXISTS steps_adj INTEGER,
            ADD COLUMN IF NOT EXISTS enmo_adj FLOAT            
    """

    with top_con.begin() as conn:
        conn.execute(text(stmt_ddl_top1min))


def single_step_produce(city_code:str, wave:int, axl_elite_filename:str, dst_dir):
    """
    Processing of a single participant's SD data.
    Load AXL data from elite file subfolder. Reformat AXL CSV to match stepcount
    requirements, then feed the stepcount main function with the temporaly stored
    CSV file. Minute level and Adjusted minute lavel CSV files are then imported 
    and appended to the ToP in the database.

    Parameters:
    -----------
    - city_code: one of cities dict key, used to identify target table name in database 
    - wave: used to identify target table name in database
    - axl_elite_filename: AXL elite filename, including edxtension;
        filenames contain participant ID and SenseDoc ID
    - dst_dir: Path where step count CSV files 

    Returns:
    --------
    A tuple with (city, wave, axl_elite_filename, status_code, status_details)

    Notes:
    ------
    - Cleaning (TODO: add description)
    - Additional metrics (TODO: add description)
    """
    logger.debug(f'PID {mp.current_process().pid}: processing {os.path.basename(axl_elite_filename)}')

    # A bit of checking needed here:
    if wave not in waves:
        logger.error(f'Invalid wave {wave}')
        return (city_code, wave, os.path.basename(axl_elite_filename), 0, 'Error (Invalid wave)')
    if city_code not in cities:
        logger.error(f'Invalid city code {city_code}')
        return (city_code, wave, os.path.basename(axl_elite_filename), 0, 'Error (Invalid city code)')
    if not os.path.exists(axl_elite_filename):
        logger.warning(f'Unable to find AXL elite file {os.path.basename(axl_elite_filename)}, skipping')
        return (city_code, wave, os.path.basename(axl_elite_filename), 0, f'Missing file ({os.path.basename(axl_elite_filename)})')

    # Extract Interact_id and sd_id
    try:
        interact_id, sd_id, _ = os.path.basename(axl_elite_filename).split('_')
    except Exception as e:
        logger.error(f'Unable to parse IID / SDID from elite filename {os.path.basename(axl_elite_filename)}')
        return (city_code, wave, os.path.basename(axl_elite_filename), 0, f'Error parsing ids ({e})')
    
    # Check existence of iid/sd_id top in DB
    top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')
    target_schema = f'top_sd{"" if wave == 1 else wave}'
    target_table1min = f'top_1min_{city_code}'
    with top_con.begin() as conn:
        # Check 1 min ToP
        stmt = text(f"SELECT * FROM {target_schema}.{target_table1min} "
                    "WHERE interact_id = :interact_id AND sd_id = :sd_id LIMIT 1")
        stmt = stmt.bindparams(interact_id=interact_id,
                               sd_id=sd_id)
        res = conn.execute(stmt).fetchone()
        if res is None:
            logger.warning(f'Unable to find participant #{interact_id}/sd #{sd_id} in {target_schema}.{target_table1min}, skipping')
            return (city_code, wave, os.path.basename(axl_elite_filename), -1, 'interact_id/sd_id not found in database')
        
    # Load and clean data
    try:
        axl_filename = _etl_axl(axl_elite_filename)
    except Exception as e:
        logger.error(f'Unable to format AXL data from {os.path.basename(axl_elite_filename)}, skipping')
        return (city_code, wave, os.path.basename(axl_elite_filename), 0, f'Error formatting AXL ({e})')

    # Compute steps
    out_folder = os.path.join(scratch_folder, "outputs_stepcount", f"w{wave}")
    sys.argv += [axl_filename, "-q", 
                 "-d", "cpu", 
                 "-t", "ssl", 
                 "--txyz", "utcdate,x,y,z", 
                 "-o", out_folder]
    stepcount.main()

    # Get minute and minuteAdjusted files
    rootname = os.path.splitext(os.path.basename(axl_filename))[0]
    stepCnt_filename = os.path.join(out_folder, rootname, f'{rootname}-Minutely.csv.gz')
    stepCntAdj_filename = os.path.join(out_folder, rootname, f'{rootname}-MinutelyAdjusted.csv.gz')    
    stepCnt = pd.read_csv(stepCnt_filename).drop(columns="Filename")
    stepCnt['interact_id'] = int(interact_id)
    stepCnt['sd_id'] = int(sd_id)
    stepCnt['utcdate'] = pd.to_datetime(stepCnt['Time'], format="%Y-%m-%d %H:%M:%S", utc=True)
    stepCntAdj = pd.read_csv(stepCntAdj_filename).drop(columns="Filename")
    stepCntAdj['interact_id'] = int(interact_id)
    stepCntAdj['sd_id'] = int(sd_id)
    stepCntAdj['utcdate'] = pd.to_datetime(stepCnt['Time'], format="%Y-%m-%d %H:%M:%S", utc=True)

    # Push to temp table and update table
    top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')

    tmp_step_table = f'sc_{interact_id}_{sd_id}'
    tmp_stepAdj_table = f'sca_{interact_id}_{sd_id}'
    stepCnt.to_sql(name=tmp_step_table, con=top_con, if_exists='replace')
    stepCntAdj.to_sql(name=tmp_stepAdj_table, con=top_con, if_exists='replace')

    target_schema = f'top_sd{"" if wave == 1 else wave}'
    target_table1min = f'top_1min_{city_code}'
    stmt_update_top1min = f"""
        UPDATE {target_schema}.{target_table1min} AS top
            SET steps = sc."Steps",
                enmo = sc."ENMO(mg)",
                steps_adj = sca."Steps",
                enmo_adj = sca."ENMO(mg)"
            FROM {tmp_step_table} AS sc, {tmp_stepAdj_table} sca
            WHERE (sc.interact_id, sc.sd_id, sc.utcdate) = (top.interact_id, top.sd_id, top.utcdate)
                AND (sca.interact_id, sca.sd_id, sca.utcdate) = (top.interact_id, top.sd_id, top.utcdate)
    """
    stmt_cleanup_step = f"""
        DROP TABLE IF EXISTS {tmp_step_table}, {tmp_stepAdj_table}
    """

    with top_con.begin() as conn:
        conn.execute(text(stmt_update_top1min))
        conn.execute(text(stmt_cleanup_step))
    

def _etl_axl(axl_elite_filename:str) -> pd.DataFrame:
    """ Read AXL elite file and save it as a CSV compatible with stepcount 
    
    Returns path to the CSV file"""
    axl_df = pd.read_csv(axl_elite_filename).drop(columns="interact_id")
    axl_df['utcdate'] = pd.to_datetime(axl_df['utcdate'], format="%Y-%m-%d %H:%M:%S.%f", utc=True)
    axl_df = axl_df.sort_values(by='utcdate') # should be already sorted but who knows...

    # Save to temp CSV file
    tmpf = NamedTemporaryFile(dir=tmp_folder, suffix='.csv', mode="w+", delete=False, newline='')
    axl_df.to_csv(tmpf, index=False, date_format="%Y-%m-%d %H:%M:%S.%f")

    return tmpf.name


if __name__ == '__main__':
    execute_alter_top('mtl', 1)
    single_step_produce('mtl', 1, 
                        r'data\interact_test_data\montreal\wave_01\sensedoc_elite_files\401102101_60_AXL.csv',
                        r'data/output_step')