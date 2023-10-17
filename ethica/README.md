# Ethica Data Pipeline

1. **Collect**: Data is uploaded by the individual phones multiple times per day and cached on Ethica Data's servers until the end of the study.
   
2. **Extract**: The data is exported by Ethica into zipped CSV files. At the end of a study, a member of the INTERACT team contacts Ethica and asks them to send the data. Each year, Ethica has provided the data a bit differently. The research team places data on DRAC. Raw data is stored in the `data_archive` folder. Expected in the file: One folder per city/wave (Ethica study), subfolders for each data source 
   
3. **Validate**: Ensure all Ethica IDs match with INTERACT ID by extracting Ethica IDs from the Ethica data files and dashboard file. Ethica IDs that exist on the dashboard or in Ethica data files but are not in the INTERACT linkage file are verified (e.g., it’s possible someone has stopped the study and provides no data in the Ethica data csv files but exists in the dashboard).
   + OUTPUT: Data is backed up to nearline
   
4. **Load**: Developer creates one csv per participant/wave/sensor, file name includes INTERACT_ID. The result is a folder per sensor, per city, each with a csv file per participant with data and INTERACT_ID.
   
5. **Transform**:  Illegal coordinates, coordinates that cannot correspond to any location on earth, are removed. There are two filters : one for (0,0,0) which is a GPS error condition (technically a spot off the coast of Nigeria, but one seldom visited); one which removes points which require movement faster than 300 km/h to reach. These pop up from satellite errors. Duplicated time stamps are removed: For all records with the same time stamp, the location with the smallest error is kept. All other records are removed. Note that those records are valid, but without timestamps, unreliable.
      + OUTPUT: Export Elite files: each data source in Ethica as csv, with linked INTERACT_ID to Project 
      + Data dictionary for **Ethica variables** is available here: https://teaminteract.ca/ressources/INTERACT_datadict.html#ethica_title

6. **Produce**: Create Tables of Power (ToP) by a) adding columns; and b) aggregating by epoch. The variables used in the Table of Power will evolve, as the team develops new metrics, important that this code can be easily adapted to integrate more metrics.  
The following columns are added : `INTERACT_ID`, `activity_levels`, `city_id`, `in_city` (flag whether data was collected within CMA), `sumary_count`, `count_x`, `count_y`, `count_z`, `device_worn`.
Data is aggregated by epoch: Two ToPs are created per city per wave: 1 second, 5 minutes. _NB: NO PHYSICAL ACTIVITY LEVELS ARE COMPUTED FOR ETHICA AXL DATA, AS WE HAVE NO VALIDATED ALGORITHM TO DERIVE THEM FROM THE 1-IN-5 DATA ACQUISITION PATTERN_
    + OUTPUT: 1 table of power per city, per wave per epoch (2/city/wave) 
    + Data dictionary for **TOP variables for Ethica** is available here: https://teaminteract.ca/ressources/INTERACT_datadict.html#top_title 

14. **Describe**: Create summary statistics:
      + date ranges
      + number of days of data per participant
      + min, max, SD distributions
      + GPS locations
   
