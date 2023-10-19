"""Validation of SenseDoc data against linkage files

Checks list of folder names against matches in linkage file. Folder names 
{INTERACT_ID}_{SD_ID} must match a record of INTERACT_ID and SD_ID in the 
linkage file. In some cases, directories need to be reorganized into unique 
{INTERACT_ID}_{SD_ID}` pairs with that name. Records which fail validation 
are flagged for follow up.
"""

import os
import logging
import re
import pandas as pd

# Define city_id and wave_id
cities = ['montreal', 'saskatoon', 'vancouver', 'victoria']
waves = ['wave_01', 'wave_02', 'wave_03', 'wave_04']

# Define base folder
root_data_folder = 'data\interact_test_data'


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S') #, level=logging.DEBUG)

    # Reporting, stored in a list of tuples (city, wave, n pids, n sdb, status)
    report = []

    for city in cities:
        for wave in waves:
            n_match = 0

            # Heading
            print(f'===== VALIDATING {city.capitalize()} | {wave.capitalize().replace("_", " ")} =====')

            # Read linkage file
            lk_file_path = os.path.join(root_data_folder, city, wave, f'linkage_{wave}_{city}.csv')
            if not os.path.isfile(lk_file_path):
                logging.warning(f'Linkage file <{os.path.basename(lk_file_path)}> not found, skipping')
                report.append((city.capitalize(), 
                           wave.capitalize().replace("_", " "), 
                           '-', 
                           '-', 
                           'No linkage file found'))
                continue
            lk_df = pd.read_csv(lk_file_path)

            # Check if we get the expected columns according to linkage\README.md
            # that is interact_id, sd_id_1, sd_id_2; Report as an ERROR and skip if not
            missing_col = False
            for colname in ['interact_id', 'sd_id_1', 'sd_id_2']:
                if colname not in lk_df.columns:
                    logging.error(f'No column named <{colname}> in linkage file <{os.path.basename(lk_file_path)}>')
                    missing_col = True
            if missing_col:
                report.append((city.capitalize(), 
                           wave.capitalize().replace("_", " "), 
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
                           wave.capitalize().replace("_", " "), 
                           str(len(lk_df.index)), 
                           '-', 
                           'Found duplicated interact_ids'))
                continue

            # Inspect each participant with SD to look for a matching sdb file
            for pid in lk_df.itertuples(index=False):
                pid_folder = os.path.join(root_data_folder, city, wave, 'sensedoc', str(pid.interact_id))
                missing_sdb = True # Track if matching sdb file is found in folder
                other_sdb = [] # Track all other (not matching) sdb files in folder
                # Define pattern according to type of sd_id
                if isinstance(pid.sd_id_1, str):
                    psdb = f'SD{pid.sd_id_1}fw\\d+_.+.sdb'
                else:
                    psdb = f'SD{pid.sd_id_1:.0f}fw\\d+_.+.sdb'
                for fentry in os.scandir(pid_folder):
                    if re.fullmatch(psdb, fentry.name):
                        missing_sdb= False
                        break
                    elif re.match('.*.sdb', fentry.name):
                        other_sdb.append(fentry.name)
                if not missing_sdb:
                    logging.info(f'Found sdb file <{fentry.name}> in folder <{pid_folder}>')
                    n_match += 1
                elif len(other_sdb):
                    logging.error(f'No matching sdb file found in folder <{pid_folder}> but other sdb file(s) found:\n\t'+'\n\t'.join(other_sdb))
                else:
                    logging.error(f'No sdb file found in folder <{pid_folder}>')
            
            # Report findings
            #print(f'Expecting {len(lk_df.index)} participants with SD data; found {n_match} participants with matching sdb file')
            report.append((city.capitalize(), 
                           wave.capitalize().replace("_", " "), 
                           str(len(lk_df.index)), 
                           str(n_match), 
                           'OK' if n_match == len(lk_df.index) else 'Missing SD files'))

    report_df = pd.DataFrame(report, columns=['City', 'Wave', 'Expected PIDs with SD', 'Found PIDs with SD', 'Status'])
    print(report_df)