# SenseDoc ETL

## Validate data

See script `sensedoc\ETL\validate.py`

Scan each city/wave folder and report missing participants and/or SD data with no match according to linkage files

For each city/wave:
1. Read linkage file `interact_id`, `sd_id` (more than 1 SD_ID possible)
2. Look for a matching folder named `{interact_id}_{sd_id}`; this folder contains one or more SQLite3 databases with SenseDoc sensor data. Report any missing folder for follow-up.

### Notes

- Vancouver and Victoria wave 3 data required to be unzipped and renamed before being validated, see script `sensedoc\ETL\utilities.py`
- Jeff's flag (_e.g._ `ignore`) are not considered when looking for data
- As of commit `#348ef11`, participant'S data folder with `sdb` files are not listed in linkage file are ignored

## Load and transform data

See script `sensedoc\ETL\load.py`

For each city/wave/participant/sensor:
1. Read linkage record (`interact_id`, `sd_id`, `sd_start`; `sd_end`) in linkage file (_NB:_ more than 1 SD_ID possible)
2. Read all GPS/AXL data from SQLite3 databases (more than 1 db can exist if SD data import has detected potential timestamp overlap)
3. Concatenate all GPS/AXL data sources into one single GPS/AXL dataframe; keep the last records in queue in case of timestamp overlap
4. Filter GPS/AXL dataframe to keep only records with survey period defined by [`sd_start`; `sd_end`]
5. Export to CSV / zipped CSV, including `city_id`, `wave_id`, `interact_id` and `sd_id` at the record level

### Notes

- GPS and AXL data are processed separately
- The output of that stage corresponds to the _Elite files_; these files are not saved to the pg database but rather on `nearline` once the ToP have be produced
- Apart from the period filter (_i.e_ removing all data outside survey period as defined in linkage file), no further cleaning is apply to the _elite files_ in order to have raw data as much as possible.

## Produce data

See script `sensedoc\ETL\top.py`

For each city/wave/participant:
1. Load transformed GPS and AXL data from CSV (see _Load and transfom data_ above)
2. Merge both data streams into ToP, aggregated at 1sec and 1min epochs.
3. Export to pg database; one table per city/wave/epoch
4. Export to CSV, including `city_id`, `wave_id`, `interact_id`, `epoch` at the record level

### Notes

- GPS data is filtered to remove:
    + invalid coordinates, specifically lat/lon of 0°; 0°
    + fix with an apparent speed over 300km/h (TBD)
- AXL data with overlapping timestamps, which may occur due to resync of the SD RTC: the most recent (_i.e_ last recorded measurement) is kept
- 1 min aggregated locations are built from median GPS locations