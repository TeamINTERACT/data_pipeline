""" Helper functions to deal with zipped files, wrongly named files, etc.
"""

import os
import zipfile
import logging

if zipfile.is_zipfile("sample.zip"):
    with zipfile.ZipFile("sample.zip", mode="r") as archive:
        for file in archive.namelist():
            if file.endswith(".md"):
                archive.extract(file, "output_dir/")


""" VANCOUVER """
def unzip_van(van_zipped, target_folder):
    """ Unzip Van SenseDoc files and copy files into correctly named folder 
    (Called from main_unzip_van function)
    """
    if not zipfile.is_zipfile(van_zipped):
        ValueError(f'<{os.path.basename(van_zipped)}> is not a valid zipped file, aborting!')

    # Extract directory/file structure while skipping MACOSX metadata
    with zipfile.ZipFile(van_zipped, mode="r") as archive:
        for f in archive.namelist():
            if '__MACOSX' in f or '._.DS_Store' in f:
                logging.debug(f'Skipping <{f}>')
                continue
            archive.extract(f, target_folder)

    # Rename extracted participant folder to match naming convention
    # PID-SDID-FW -> PID_SDID
    root_name = os.path.splitext(os.path.basename(archive.filename))[0]
    new_name = '_'.join(root_name.split('-')[:2])
    try:
        os.rename(os.path.join(target_folder, root_name), os.path.join(target_folder, new_name))
    except:
        logging.warning(f'Unable to rename <{root_name}> to <{new_name}> in {target_folder}')

def main_unzip_van(src, dst):
    """ Scan src folder and extract to dst folder """
    for _, _, fs in os.walk(src):
        for f in fs:
            if zipfile.is_zipfile(os.path.join(src, f)):
                logging.info(f'Processing <{f}>')
                unzip_van(os.path.join(src, f), dst)


""" VICTORIA """
def unzip_vic(vic_zipped, target_folder):
    """ Unzip Vic SenseDoc files and copy files into correctly named folder 
    (Called from main_unzip_vic function)
    """
    if not zipfile.is_zipfile(vic_zipped):
        ValueError(f'<{os.path.basename(vic_zipped)}> is not a valid zipped file, aborting!')

    # Extract directory/file structure while skipping MACOSX metadata
    sdid = '000'
    with zipfile.ZipFile(vic_zipped, mode="r") as archive:
        for f in archive.namelist():
            if '__MACOSX' in f or '._.DS_Store' in f or '.dropbox.device' in f:
                logging.debug(f'Skipping <{f}>')
                continue
            # Look for Sd_id
            if f.endswith('.SD2'):
                try:
                    sdid = str(int(os.path.basename(f).replace('.SD2', '').replace('SD', '')))
                except:
                    logging.warning(f'Unable to extract SD ID from <{f}>m skipping')
            archive.extract(f, target_folder)

    # Rename extracted participant folder to match naming convention
    # PID -> PID_SDID
    root_name = os.path.splitext(os.path.basename(archive.filename))[0]
    new_name = f'{root_name}_{sdid}'
    try:
        os.rename(os.path.join(target_folder, root_name), os.path.join(target_folder, new_name))
    except:
        logging.warning(f'Unable to rename <{root_name}> to <{new_name}> in {target_folder}')

def main_unzip_vic(src, dst):
    """ Scan src folder and extract to dst folder """
    for _, _, fs in os.walk(src):
        for f in fs:
            if zipfile.is_zipfile(os.path.join(src, f)) and f.startswith('10'): # Need to discard zip files which are not SD data 
                logging.info(f'Processing <{f}>')
                unzip_vic(os.path.join(src, f), dst)


if __name__ == '__main__':
    logging.basicConfig(format='[%(asctime)s] %(levelname)s: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    # unzip_van("/home/btcrchum/projects/def-dfuller/interact/incoming_data/Vancouver/Wave3/INT-YVR-W3-SD-CC-25JAN2023/201005131-453-2106.zip", "/home/btcrchum/scratch")
    # main_unzip_van("/home/btcrchum/projects/def-dfuller/interact/incoming_data/Vancouver/Wave3/INT-YVR-W3-SD-CC-25JAN2023", "/home/btcrchum/projects/def-dfuller/interact/data_archive/vancouver/wave_03/sensedoc")
    # unzip_vic("/home/btcrchum/projects/def-dfuller/interact/incoming_data/Victoria/Wave3/SenseDoc/101011680.zip", "/home/btcrchum/scratch")
    main_unzip_vic("/home/btcrchum/projects/def-dfuller/interact/incoming_data/Victoria/Wave3/SenseDoc", "/home/btcrchum/projects/def-dfuller/interact/data_archive/victoria/wave_03/sensedoc")