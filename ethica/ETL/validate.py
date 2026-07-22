"""Validation of Ethica data against linkage files

Ethica data (accelerometer + GPS) is stored in seperate files (one
file per data stream) under a folder named after the study number. 
All Ethica users are listed in the same file. Validating the users
implies reading the user ids in the two AXL and GPS files.
File structure is as follow (NB several studyid folders can live under
the wave subfolder, as English/French studies had to be coded separately):

TARGET_ROOT_FOLDER
    └─ wave_01
        └─ studyid
            ├─ studyid_accelerometer.csv
            ├─ studyid_gps.csv
            └─ [other Ethica data stream files]
--
USAGE: validate.py [TARGET_ROOT_FOLDER [WAVE]]

If TARGET_ROOT_FOLDER not provided, will default to test data folder.
If WAVE is not provided, all waves (1-4) will be processed
"""

import os
import sys
import logging
import re
import pandas as pd
import polars as pl

# Define city_id and wave_id
cities = {'mtl': 'montreal', 
        'skt': 'saskatoon', 
        'van': 'vancouver', 
        'vic': 'victoria'}
waves = [1, 2, 3, 4]

# Define base folder when not provided on the cmd line
root_data_folder = r'data\interact_test_data'

# Number of rows to read in axl and gps files, set to None for production
debug_nrows = None


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S') #, level=logging.DEBUG)

    # Get target root folder as command line argument
    if len(sys.argv[1:]):
        root_data_folder = sys.argv[1]

    if not os.path.isdir(root_data_folder):
        logging.error(f'No directory <{root_data_folder}> found! Aborting')
        exit(1)

    # Get wave id to process
    wave_id = None
    if len(sys.argv[2:]):
        wave_id = int(sys.argv[2])
        if wave_id not in waves:
            logging.error(f'Invalid wave id <{wave_id}>! Aborting')
            exit(1)
        else:
            waves = [wave_id]

    # Reporting, stored in a list of tuples (city, wave, n pids, status)
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
                logging.warning(f'{ccode}-{wave} | Linkage file <{os.path.basename(lk_file_path)}> not found, skipping')
                report.append((city.capitalize(), 
                        f'Wave {wave}', 
                        '-', 
                        '-', 
                        '-', 
                        '-', 
                        'No linkage file found'))
                continue
            if pd.__version__ < '2.2.0': # FutureWarning: Downcasting behavior in replace is deprecated" on a Series
                lk_df = pd.read_csv(lk_file_path, dtype=str).replace('0', pd.NA)
            else:
                with pd.option_context('future.no_silent_downcasting', True):
                    lk_df = pd.read_csv(lk_file_path, dtype=str).replace('0', pd.NA)

            # Check if we get the expected columns according to linkage\README.md
            # that is interact_id, ethica_id; Report as an ERROR and skip if not
            missing_col = False
            for colname in ['interact_id', 'ethica_id']:
                if colname not in lk_df.columns:
                    logging.error(f'{ccode}-{wave} | No column named <{colname}> in linkage file <{os.path.basename(lk_file_path)}>')
                    missing_col = True
            if missing_col:
                report.append((city.capitalize(), 
                        f'Wave {wave}', 
                        '-', 
                        '-', 
                        '-', 
                        '-', 
                        'Linkage file wrongly formatted'))
                continue

            # Keep only participants who did Ethicas
            lk_df = lk_df[['interact_id', 'ethica_id']].dropna().reset_index(drop=True)

            # Display linkage file content for control
            logging.debug(f'{ccode}-{wave} | Linkage file <{os.path.basename(lk_file_path)}>:\n{lk_df.to_string()}')

            # Check if we have duplicated participant
            if not lk_df.interact_id.is_unique:
                logging.error(f'Found duplicated interact_ids in <{os.path.basename(lk_file_path)}>')
                report.append((city.capitalize(), 
                        f'Wave {wave}', 
                        str(len(lk_df.index)), 
                        '-', 
                        '-',
                        '-',
                        'Found duplicated interact_ids'))
                continue

            # Load Ethica GPS and AXL data, stored into studyid subfolder
            ethica_data = os.path.join(root_data_folder, city, f'wave_{wave:02d}', 'ethica')
            if not os.path.exists(ethica_data):
                logging.error(f'{ccode}-{wave} | Missing ethica data folder')
                report.append((city.capitalize(), 
                        f'Wave {wave}', 
                        '-', 
                        '-', 
                        '-',
                        '-',
                        'Missing Ethica data folder'))
                continue

            subdirs = os.listdir(ethica_data)
            studies = []
            not_found = True
            for sd in subdirs:
                # Looking for a folder with a simple number (~study id) as name
                m = re.fullmatch('\\d+', sd)
                if m:
                    not_found = False
                    studies.append(m[0])
            if not_found:
                logging.error(f'{ccode}-{wave} | No subfolder named after study number found in data folder')
                report.append((city.capitalize(), 
                        f'Wave {wave}', 
                        '-', 
                        '-', 
                        '-',
                        '-',
                        'No Ethica study data folder found'))
                continue

            # Process AXL data
            missing_axl = False
            axl_dfs = []
            for studyid in studies:
                axl_file = os.path.join(ethica_data, studyid, f'{studyid}_accelerometer.csv')
                if not os.path.exists(axl_file):
                    logging.error(f'{ccode}-{wave} | Unable to find accelerometer file in Ethica data folder')
                    report.append((city.capitalize(), 
                            f'Wave {wave}', 
                            '-', 
                            '-', 
                            '-',
                            '-',
                            f'No Ethica accelerometer file found in folder {studyid}'))
                    missing_axl = True
                    break
                q = (pl.scan_csv(axl_file, n_rows=debug_nrows)
                    .select('user_id')
                    .unique()
                )
                pldf = q.collect()
                pdf = pldf.to_pandas().astype(str)
                axl_dfs.append(pdf)
            if missing_axl:
                continue
            
            # Merge all idnividual axl_df
            axl_df = pd.concat(axl_dfs)
            axl_df = axl_df[['user_id']].drop_duplicates().reset_index(drop=True) # keep only unique user ids for validation
            axl_df['axl'] = True

            # Process GPS data
            missing_gps = False
            gps_dfs = []
            for studyid in studies:
                gps_file = os.path.join(ethica_data, studyid, f'{studyid}_gps.csv')
                if not os.path.exists(gps_file):
                    logging.error(f'{ccode}-{wave} | Unable to find accelerometer file in Ethica data folder')
                    report.append((city.capitalize(), 
                            f'Wave {wave}', 
                            '-', 
                            '-', 
                            '-',
                            '-',
                            f'No Ethica GPS file found in folder {studyid}'))
                    missing_gps = True
                    break
                q = (pl.scan_csv(gps_file, n_rows=debug_nrows)
                    .select('user_id')
                    .unique()
                )
                pldf = q.collect()
                pdf = pldf.to_pandas().astype(str)
                gps_dfs.append(pdf)
            if missing_gps:
                continue

            # Merge all indivudual gps_df
            gps_df = pd.concat(gps_dfs)
            gps_df = gps_df[['user_id']].drop_duplicates().reset_index(drop=True) # keep only unique user ids for validation
            gps_df['gps'] = True
            if pd.__version__ < '2.2.0': # FutureWarning: Downcasting behavior in replace is deprecated" on a Series
                ethica_df = pd.merge(axl_df, gps_df, how='outer', on='user_id').fillna(False)
            else:
                with pd.option_context('future.no_silent_downcasting', True):
                    ethica_df = pd.merge(axl_df, gps_df, how='outer', on='user_id').fillna(False)

            # Build final df, with linkage data and ethica data
            ethica_df = pd.merge(lk_df, ethica_df, how='outer', left_on='ethica_id', right_on='user_id')

            # Compute metrics:
            # - Number of PIDs with Ethica data
            # - Number of unknown Ethica users (i.e. no matching Interact ID)
            # - Number of PIDs with partial data (axl or gps only)
            pids_w_userid = ethica_df.loc[ethica_df.interact_id.notna() & ethica_df.user_id.notna(),]
            pids_wo_userid = ethica_df.loc[ethica_df.interact_id.notna() & ethica_df.user_id.isna(),]
            unknown_userid = ethica_df.loc[ethica_df.interact_id.isna(),]
            pids_partial = ethica_df.loc[ethica_df.interact_id.notna() & ethica_df.user_id.notna(),]
            if pd.__version__ < '2.2.0': # FutureWarning: Downcasting behavior in replace is deprecated" on a Series
                pids_partial = pids_partial.loc[pids_partial.axl.fillna(False) ^ pids_partial.gps.fillna(False),]
            else:
                with pd.option_context('future.no_silent_downcasting', True):
                    pids_partial = pids_partial.loc[pids_partial.axl.fillna(False) ^ pids_partial.gps.fillna(False),]

            # Report findings
            #print(f'Expecting {len(lk_df.index)} participants with SD data; found {n_match} participants with matching sdb file')
            report.append((city.capitalize(), 
                            f'Wave {wave}', 
                            str(pids_w_userid.shape[0]), 
                            str(pids_wo_userid.shape[0]),
                            str(unknown_userid.shape[0]),
                            str(pids_partial.shape[0]), 
                            'OK' if ((pids_wo_userid.shape[0] + pids_partial.shape[0]) == 0) else 'Incomplete/missing Ethica data'))
            
            # Report issues, if any
            if pids_wo_userid.shape[0] > 0:
                logging.warning(f'{ccode}-{wave} | Ethica data missing for the following PIDs:\n'+'\n'.join(map(lambda i: str(int(i)), pids_wo_userid.interact_id)))
            if unknown_userid.shape[0] > 0:
                logging.warning(f'{ccode}-{wave} | Unknown Ethica users (no matching Interact ID):\n'+'\n'.join(map(lambda i: str(int(i)), unknown_userid.user_id)))
            if pids_partial.shape[0] > 0:
                logging.warning(f'{ccode}-{wave} | Missing axl and/or gps data for the following PIDs:\n'+'\n'.join(map(lambda i: str(int(i)), pids_partial.interact_id)))
            
    report_df = pd.DataFrame(report, columns=['City', 'Wave', 'PIDs with Ethica', 'PIDs missing Ethica', 'Unknown Ethica users', 'Partial data', 'Status'])
    print(report_df.to_markdown(index=False, tablefmt='presto'))
