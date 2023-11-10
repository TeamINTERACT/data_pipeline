# SenseDoc Data Pipeline

1. **Collect**: Participants are given SenseDocs, hip-worn devices that store gps and acc data onto the device. They are asked to wear the devices when not sleeping, for 10 consecutive days. Devices should be charged daily. Coordinators deliver and retrieve devices.
   
2. **Extract**: Data is pulled from the individual devices by research coordinators, using an extraction tool (SenseAnalytics) provided by MobySens. This extraction includes the proprietary raw data files, and a SQLite3 DB file (and given a .sdb extension). Our migration process preserves those raw data files, but the ingest process is built against the SDB files. Coordinators name each folder with `{INTERACT_ID}_{SD_ID}`, zip the folder and place it on Compute Canada in the Incoming Data folder for their city and wave.
   
3. **Validate**: A python script (`sensedoc/ETL/validate.py`) checks list of folder names against matches in linkage file. Folder names `{INTERACT_ID}_{SD_ID}` must match a record of INTERACT_ID and SD_ID in the linkage file. In some cases, directories need to be reorganized into unique `{INTERACT_ID}_{SD_ID}` pairs with that name. Records which fail validation are flagged for follow up.

   + OUTPUT: Data is backed up to nearline

   ```
   ===== VALIDATING Montreal | Wave 1 =====
   [11/10/2023 06:13:58] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401627014_188>
   [11/10/2023 06:13:58] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401751741_51>
   [11/10/2023 06:13:58] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401679813_146>
   ===== VALIDATING Montreal | Wave 2 =====
   ===== VALIDATING Montreal | Wave 3 =====
   [11/10/2023 06:13:58] ERROR: Unable to find directory <montreal/wave_03/sensedoc/401952301_23>
   ===== VALIDATING Saskatoon | Wave 1 =====
   [11/10/2023 06:13:58] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302610266_367>
   [11/10/2023 06:13:59] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302923081_367>
   [11/10/2023 06:13:59] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302273130_375>
   ===== VALIDATING Saskatoon | Wave 2 =====
   [11/10/2023 06:13:59] ERROR: Unable to find directory <saskatoon/wave_02/sensedoc/302955394_383>
   ===== VALIDATING Saskatoon | Wave 3 =====
   ===== VALIDATING Vancouver | Wave 1 =====
   ===== VALIDATING Vancouver | Wave 2 =====
   [11/10/2023 06:14:00] ERROR: Unable to find directory <vancouver/wave_02/sensedoc/202634537_491>
   ===== VALIDATING Vancouver | Wave 3 =====
   [11/10/2023 06:14:00] ERROR: Unable to find directory <vancouver/wave_03/sensedoc/203064043_324>
   ===== VALIDATING Victoria | Wave 1 =====
   [11/10/2023 06:14:00] ERROR: Unable to find directory <victoria/wave_01/sensedoc/101158091_23>
   [11/10/2023 06:14:01] ERROR: Unable to find directory <victoria/wave_01/sensedoc/101891218_111>
   ===== VALIDATING Victoria | Wave 2 =====
   ===== VALIDATING Victoria | Wave 3 =====
   [11/10/2023 06:14:01] ERROR: Unable to find directory <victoria/wave_03/sensedoc/101847191_405>

   City      | Wave   |   PIDs with SD |   Expected #SD |   Found #SD | Status
   -----------+--------+----------------+----------------+-------------+------------------
   Montreal  | Wave 1 |            163 |            165 |         162 | Missing SD files
   Montreal  | Wave 2 |             45 |             45 |          45 | OK
   Montreal  | Wave 3 |             55 |             55 |          54 | Missing SD files
   Saskatoon | Wave 1 |            113 |            114 |         111 | Missing SD files
   Saskatoon | Wave 2 |             32 |             34 |          33 | Missing SD files
   Saskatoon | Wave 3 |             10 |             10 |          10 | OK
   Vancouver | Wave 1 |            152 |            152 |         152 | OK
   Vancouver | Wave 2 |             84 |             91 |          90 | Missing SD files
   Vancouver | Wave 3 |             73 |             76 |          75 | Missing SD files
   Victoria  | Wave 1 |            155 |            165 |         163 | Missing SD files
   Victoria  | Wave 2 |            130 |            134 |         134 | OK
   Victoria  | Wave 3 |             89 |             91 |          90 | Missing SD files
   
   ==== SECOND STEP VALIDATION ====
   The following sdb files have been found in </home/btcrchum/projects/def-dfuller/interact/data_archive> with no match in linkage files:
   1. victoria/wave_03/sensedoc/101435597_374/101435597_445/SDfw_20210621_103435.sdb
   2. montreal/wave_02/sensedoc/402312216_280/investigate.sdb
   3. vancouver/wave_03/sensedoc/201210287_349/SD349fw2110_20221011_113814.sdb
   4. vancouver/wave_03/sensedoc/202662394_401/SD401fw2110_20220910_111205.sdb
   5. vancouver/wave_03/sensedoc/202116714_403/SD403fw2106_20220903_104635.sdb
   6. vancouver/wave_03/sensedoc/203659654_324/SD324fw2099_20220903_105938.sdb
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
   

