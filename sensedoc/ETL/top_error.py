""" NOT PART OF THE REGULAR DATA PIPELINE
Helper proc to look for IID/SD not computed after top.py script
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, text


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
root_data_folder = '/home/btcrchum/projects/def-dfuller/interact/data_archive'

# Store pool worker arguments in list of tuples
# Arg = (city_code, wave, iid, sdid)
wrk_args = set()

src_dir = os.path.abspath(root_data_folder)
for ccode, city in cities.items():
    for wave in waves:
        # Create top subfolder
        top_folder = os.path.join(root_data_folder, city, f'wave_{wave:02d}', 'sensedoc_top_files')
        Path(top_folder).mkdir(parents=True, exist_ok=True)

        # Check that city/wave folder exists, which is the case with test data...
        elite_folder = os.path.join(root_data_folder, city, f'wave_{wave:02d}', 'sensedoc_elite_files')
        if not os.path.exists(elite_folder):
            continue

        # Found a folder, all content will be scan to add GPS/AXL combination to queue
        with os.scandir(elite_folder) as it:
            for f in it:
                root_elite_fname = os.path.abspath(f.path)
                root_elite_fname = root_elite_fname.removesuffix("_AXL.csv")
                root_elite_fname = root_elite_fname.removesuffix("_GPS.csv")
                iid, sd_id = os.path.basename(root_elite_fname).split('_')
                wrk_args.add((ccode, wave, iid, sd_id))

# Extract all processed iid/sd from top
done = set()

top_con = create_engine(f'postgresql://{db_user}@{db_host}/interact_db')
for ccode, city in cities.items():
    for wave in waves:
        target_schema = f'top_sd{"" if wave == 1 else wave}'
        target_table = f'top_1min_{ccode}'
        sql = f"SELECT DISTINCT '{ccode}' AS ccode, {wave} AS wave, interact_id, sd_id FROM {target_schema}.{target_table}"
        top_iid_df = pd.read_sql_query(sql, con=top_con)

        # Updating the set of processed IID/SD
        done.update(top_iid_df.itertuples(index=False))
        print(f'{ccode}, w{wave} -> {len(done)} cumulative elements')

# Find which IID/SD have not been processed
not_done = wrk_args.difference(done)
not_done_df = pd.DataFrame(not_done, columns=['City', 'Wave', 'IID', 'SD']).sort_values(by=['Wave', 'City', 'IID']).reset_index(drop=True)
print(not_done_df)

# Scan files of those IID/SD
for idx, ccode, wave, iid, sdid in not_done_df.itertuples():
    print('\n{:=^50}'.format(f' {idx} | {wave} | {ccode} | {iid} | {sdid} '))
    elite_folder = os.path.join(root_data_folder, cities[ccode], f'wave_{wave:02d}', 'sensedoc_elite_files')
    elite_gps = os.path.join(elite_folder, f'{iid}_{sdid}_GPS.csv')
    elite_axl = os.path.join(elite_folder, f'{iid}_{sdid}_AXL.csv')
    try:
        gps_df = pd.read_csv(elite_gps)
        print(gps_df)
    except Exception as e:
        print(f'Unable to read GPS file ({e})')
    try:
        axl_df = pd.read_csv(elite_axl)
        print(axl_df)
    except Exception as e:
        print(f'Unable to read AXL file ({e})')
    