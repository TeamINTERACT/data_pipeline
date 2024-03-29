"""Validation of SenseDoc data against linkage files

Checks list of folder names against matches in linkage file. Folder names 
{INTERACT_ID}_{SD_ID} must match a record of INTERACT_ID and SD_ID in the 
linkage file. In some cases, directories need to be reorganized into unique 
{INTERACT_ID}_{SD_ID}` pairs with that name. Records which fail validation 
are flagged for follow up.
A second step during validation involves listing all *.sdb files found and 
not matched against linkage file.
--
USAGE: validate.py [TARGET_ROOT_FOLDER]

If TARGET_ROOT_FOLDER not provided, will default to test data folder.
"""

import os
import sys
import logging
import re
import pandas as pd

# Define city_id and wave_id
cities = {'mtl': 'montreal', 
          'skt': 'saskatoon', 
          'van': 'vancouver', 
          'vic': 'victoria'}
waves = [1, 2, 3]

# Define base folder when not provided on the cmd line
root_data_folder = 'data\interact_test_data'


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S') #, level=logging.DEBUG)

    # Get target root folder as command line argument
    if len(sys.argv[1:]):
        root_data_folder = sys.argv[1]

    if not os.path.isdir(root_data_folder):
        logging.error(f'No directory <{root_data_folder}> found! Aborting')
        exit(1)

    # Reporting, stored in a list of tuples (city, wave, n pids, n sdb, status)
    report = []
    matched_sdbs = [] # keep track of all matched sdb files, for 2nd step validation

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
                           '-',
                           'Found duplicated interact_ids'))
                continue

            # Pivot table to extract all SD when more than one has been used
            lk_df_long = pd.wide_to_long(lk_df, ['sd_id', 'sd_firmware', 'sd_start', 'sd_end'], sep="_", i='interact_id', j='sd_rank')
            lk_df_long = lk_df_long.loc[lk_df_long['sd_id'].notna(),['sd_id', 'sd_start', 'sd_end']]
            lk_df_long.reset_index(drop=False, inplace=True)

            # Inspect each participant with SD to look for a matching sdb file 
            # (we only check the first one, if more than one SD has been given to that participant)
            for pid in lk_df_long.itertuples(index=False):
                pid_folder = os.path.join(root_data_folder, city, f'wave_{wave:02d}', 'sensedoc', f'{pid.interact_id}_{pid.sd_id}')
                # Check PID folder exists
                if not os.path.isdir(pid_folder):
                    logging.error(f'Unable to find directory <{os.path.relpath(pid_folder, root_data_folder)}>')
                    continue

                missing_sdb = True # Track if matching sdb file is found in folder
                other_sdb = [] # Track all other (not matching) sdb files in folder
                # Define pattern according to type of sd_id
                psdb = f'SD{pid.sd_id}fw\\d*_.+.sdb'
                psbd_rtc = f'SD{pid.sd_id}fw\\d*_.+_rtc\\d+.sdb'
                for fentry in os.scandir(pid_folder):
                    if re.fullmatch(psdb, fentry.name) and not re.fullmatch(psbd_rtc, fentry.name):
                        missing_sdb= False
                        matched_sdbs.append(os.path.join(pid_folder, fentry.name))
                        break
                    elif re.match('.*.sdb', fentry.name):
                        other_sdb.append(fentry.name)
                if not missing_sdb:
                    logging.info(f'Found sdb file <{fentry.name}> in folder <{os.path.relpath(pid_folder, root_data_folder)}>')
                    n_match += 1
                elif len(other_sdb):
                    logging.error(f'No matching sdb file found in folder <{os.path.relpath(pid_folder, root_data_folder)}> but other sdb file(s) found:\n\t'+'\n\t'.join(other_sdb))
                else:
                    logging.error(f'No sdb file found in folder <{os.path.relpath(pid_folder, root_data_folder)}>')
            
            # Report findings
            #print(f'Expecting {len(lk_df.index)} participants with SD data; found {n_match} participants with matching sdb file')
            report.append((city.capitalize(), 
                           f'Wave {wave}', 
                           str(len(lk_df.index)), 
                           str(len(lk_df_long.index)),
                           str(n_match), 
                           'OK' if n_match == len(lk_df_long.index) else 'Missing SD files'))
            
    report_df = pd.DataFrame(report, columns=['City', 'Wave', 'PIDs with SD', 'Expected #SD', 'Found #SD', 'Status'])
    print(report_df.to_markdown(index=False, tablefmt='presto'))

    # Second step validation: looking for unmatched sdb files
    print('==== SECOND STEP VALIDATION ====')
    unmatched_sdbs = []
    for dirpath, dirnames, filenames in os.walk(root_data_folder):
        for f in filenames:
            if os.path.splitext(f)[1] == '.sdb' and not re.fullmatch('.+_rtc\\d+.sdb', f) and os.path.join(dirpath, f) not in matched_sdbs:
                unmatched_sdbs.append(os.path.join(dirpath, f))
    if len(unmatched_sdbs):
        print(f'The following sdb files have been found in <{root_data_folder}> with no match in linkage files:')
        for i, sdb in enumerate(unmatched_sdbs, 1):
            print(f'{i}. {os.path.relpath(sdb, root_data_folder)}')
    else:
        print('Ok')
