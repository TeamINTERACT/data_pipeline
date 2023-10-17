# SenseDoc ETL

## Validate data

Scan each city/wave folder and report missing participants and/or SD data with no match according to linkage files

For each city/wave:
1. Read linkage file `interact_id`, `sd_id` (more than 1 SD_ID possible)
2. Look for a matching folder named `{interact_id}_{sd_id}`; this folder contains one or more SQLite3 databases with SenseDoc sensor data. Report any missing folder for follow-up.

## Load and transform data

For each city/wave/participant/sensor:
1. Read linkage record (`interact_id`, `sd_id`, `sd_start`; `sd_end`) in linkage file (_NB:_ more than 1 SD_ID possible)
2. Read all GPS/AXL data from SQLite3 databases (more than 1 db can exist if SD data import has detected potential timestamp overlap)
3. Concatenate all GPS/AXL data sources into one single GPS/AXL dataframe; keep the last records in queue in case of timestamp overlap
4. Filter GPS/AXL dataframe to keep only records with survey period defined by [`sd_start`; `sd_end`]
5. Export to CSV / zipped CSV, including `city_id`, `wave_id`, `interact_id` and `sd_id` at the record level

### Notes
- GPS and AXL data are processed separately
- The output of that stage corresponds to the _Elite files_; these files are not saved to the pg database but rather on `nearline` once the ToP have be produced

## Produce data

For each city/wave/participant:
1. Load transformed GPS and AXL data from CSV (see _Load and transfom data_ above)
2. Merge both data streams into ToP, aggregated at 1sec, 1min and 5min epochs.
3. Export to pg database; one table per city/wave/epoch
4. Export to CSV, including `city_id`, `wave_id`, `interact_id`, `epoch` at the record level
