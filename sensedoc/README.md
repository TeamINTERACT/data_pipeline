# SenseDoc Data Pipeline

1. **Collect**: Participants are given SenseDocs, hip-worn devices that store gps and acc data onto the device. They are asked to wear the devices when not sleeping, for 10 consecutive days. Devices should be charged daily. Coordinators deliver and retrieve devices.
   
2. **Extract**: Data is pulled from the individual devices by research coordinators, using an extraction tool (SenseAnalytics) provided by MobySens. This extraction includes the proprietary raw data files, and a SQLite3 DB file (and given a .sdb extension). Our migration process preserves those raw data files, but the ingest process is built against the SDB files. Coordinators name each folder with `{INTERACT_ID}_{SD_ID}`, zip the folder and place it on Compute Canada in the Incoming Data folder for their city and wave.
   
3. **Validate**: A python script (`sensedoc/ETL/validate.py`) checks list of folder names against matches in linkage file. Folder names `{INTERACT_ID}_{SD_ID}` must match a record of INTERACT_ID and SD_ID in the linkage file. In some cases, directories need to be reorganized into unique `{INTERACT_ID}_{SD_ID}` pairs with that name. Records which fail validation are flagged for follow up.

   + OUTPUT: Data is backed up to nearline

   ```
   ===== VALIDATING Montreal | Wave 1 =====
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401627014_188>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401751741_51>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401679813_146>
   ===== VALIDATING Montreal | Wave 2 =====
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401034573_39>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401240419_77>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401272178_60>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401465378_51>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401507474_69>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401664309_63>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401727775_50>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401809607_49>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/401952301_6>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/402402064_45>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/402411342_96>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/402495712_36>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/402577721_23>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_02/sensedoc/402781880_95>
   ===== VALIDATING Montreal | Wave 3 =====
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_03/sensedoc/403658820_263>
   [10/31/2023 09:34:14] ERROR: No sdb file found in folder <data_archive/montreal/wave_03/sensedoc/403835859_109>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_03/sensedoc/401399249_102>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_03/sensedoc/401952301_23>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <montreal/wave_03/sensedoc/401844948_36>
   ===== VALIDATING Montreal | Wave 4 =====
   [10/31/2023 09:34:14] WARNING: Linkage file <linkage_mtl_w4.csv> not found, skipping
   ===== VALIDATING Saskatoon | Wave 1 =====
   [10/31/2023 09:34:14] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302610266_367>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302923081_367>
   [10/31/2023 09:34:14] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302273130_375>
   [10/31/2023 09:34:14] ERROR: No matching sdb file found in folder <data_archive/saskatoon/wave_01/sensedoc/302394560_408> but other sdb file(s) found:
         SD375fw2099_20190201_114043.sdb
   ===== VALIDATING Saskatoon | Wave 2 =====
   [10/31/2023 09:34:14] ERROR: Unable to find directory <saskatoon/wave_02/sensedoc/302955394_383>
   ===== VALIDATING Saskatoon | Wave 3 =====
   ===== VALIDATING Saskatoon | Wave 4 =====
   [10/31/2023 09:34:14] WARNING: Linkage file <linkage_skt_w4.csv> not found, skipping
   ===== VALIDATING Vancouver | Wave 1 =====
   ===== VALIDATING Vancouver | Wave 2 =====
   ===== VALIDATING Vancouver | Wave 3 =====
   [10/31/2023 09:34:14] ERROR: Unable to find directory <vancouver/wave_03/sensedoc/203064043_324>
   ===== VALIDATING Vancouver | Wave 4 =====
   [10/31/2023 09:34:14] WARNING: Linkage file <linkage_van_w4.csv> not found, skipping
   ===== VALIDATING Victoria | Wave 1 =====
   [10/31/2023 09:34:14] ERROR: Unable to find directory <victoria/wave_01/sensedoc/101158091_23>
   [10/31/2023 09:34:15] ERROR: Unable to find directory <victoria/wave_01/sensedoc/101891218_111>
   ===== VALIDATING Victoria | Wave 2 =====
   ===== VALIDATING Victoria | Wave 3 =====
   [10/31/2023 09:34:15] ERROR: No sdb file found in folder <data_archive/victoria/wave_03/sensedoc/101435597_445>
   [10/31/2023 09:34:15] ERROR: Unable to find directory <victoria/wave_03/sensedoc/101798447_476>
   [10/31/2023 09:34:15] ERROR: Unable to find directory <victoria/wave_03/sensedoc/101847191_405>
   [10/31/2023 09:34:15] ERROR: No sdb file found in folder <data_archive/victoria/wave_03/sensedoc/101888460_379>
   ===== VALIDATING Victoria | Wave 4 =====
   [10/31/2023 09:34:15] WARNING: Linkage file <linkage_vic_w4.csv> not found, skipping
            City    Wave Expected PIDs with SD Found PIDs with SD                 Status
   0    Montreal  Wave 1                   163                160       Missing SD files
   1    Montreal  Wave 2                    45                 31       Missing SD files
   2    Montreal  Wave 3                    55                 50       Missing SD files
   3    Montreal  Wave 4                     -                  -  No linkage file found
   4   Saskatoon  Wave 1                   112                108       Missing SD files
   5   Saskatoon  Wave 2                    32                 31       Missing SD files
   6   Saskatoon  Wave 3                    10                 10                     OK
   7   Saskatoon  Wave 4                     -                  -  No linkage file found
   8   Vancouver  Wave 1                   152                152                     OK
   9   Vancouver  Wave 2                     0                  0                     OK
   10  Vancouver  Wave 3                    73                 72       Missing SD files
   11  Vancouver  Wave 4                     -                  -  No linkage file found
   12   Victoria  Wave 1                   155                153       Missing SD files
   13   Victoria  Wave 2                   130                130                     OK
   14   Victoria  Wave 3                    89                 85       Missing SD files
   15   Victoria  Wave 4                     -                  -  No linkage file found
   ```
   
4. **Load**: Developer creates one csv per participant/wave/sensor, file name includes INTERACT_ID. The result is a folder per sensor, per city, each with a csv file per participant with data and INTERACT_ID
   
5. **Transform**: Data is cleaned to remove invalid or corrupt records. Records outside of wear date window are removed (`sd_start_1`; `sd_end_1`/ `sd_start_2`; `sd_end_2`). Since the device is always recording when on, some movement data from the coordinator delivering or retrieving the device may be collected. To filter the data properly, the participant provides wear dates. These wear dates are in the linkage file. Dates are recorded for each SenseDoc worn by a participant. It is possible that a participant missed a day or days within the wear dates. Filtering by date ensures we don’t use coordinator data recorded on the device during delivery /recovery. If there are no wear dates, all records are kept.
   Illegal coordinates, coordinates that cannot correspond to any location on earth, are removed. There are two filters : one for (0,0,0) which is a GPS error condition (technically a spot off the coast of Nigeria, but one seldom visited); one which removes points which require movement faster than 300 km/h to reach. These pop up from satellite errors.
      + OUTPUT: Data is exported as Elite (intermediary) files to Project
      + Data dictionary for **SenseDoc variables** is available here: https://teaminteract.ca/ressources/INTERACT_datadict.html#sensedoc_title 

6. **Produce**: Create Tables of Power (ToP) by a) adding columns; and b) aggregating by epoch. The variables used in the Table of Power will evolve, as the team develops new metrics, important that this code can be easily adapted to integrate more metrics. 
The following columns are added : `INTERACT_ID`, `activity_levels`, `city_id`, `in_city` (flag whether data was collected within CMA), `sumary_count`, `count_x`, `count_y`, `count_z`, `device worn`. See description in GitHub TOP readme and Data Dictionary. 
Data is aggregated by epoch: Three ToPs are created per city per wave: 1 second, 1 minute, 5 minutes.  
    + OUTPUT: 1 table of power per city, per wave per epoch (3/city/wave)
    + Data dictionary for **TOP variables for SenseDoc** is available here: https://teaminteract.ca/ressources/INTERACT_datadict.html#top_title 

7. **Describe**: Create summary statistics:
      + date ranges
      + number of days of data per participant
      + min, max, SD distributions
      + GPS locations
   

