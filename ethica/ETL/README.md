# Ethica ETL

## Validate data

Scan each city/wave folder and report missing participants and/or SD data with no match according to linkage files

For each city/wave:
1. Read linkage file `interact_id`, `ethica_id`
2. Load unique `ethica_id` from raw files in GPS and AXL subfolders. Report any incomplete pair  {`interact_id`; `ethica_id`} for follow-up.

### Notes
- Ethica data format may have changed from year to year and will require some adaptation before being validated

## Load and transform data

For each city/wave/participant/sensor:
1. Read linkage record (`interact_id`, `ethica_id`) in linkage file
2. Read all GPS/AXL data from raw CSV file
3. Export to CSV / zipped CSV, including `city_id`, `wave_id`, `interact_id` and `device_id` at the record level

### Notes
- Ethica data format may have changed from year to year and will require some adaptation to be loaded
- GPS and AXL data are processed separately; other data streams are not processed
- The output of that stage corresponds to the _Elite files_; these files are not saved to the pg database but rather on `nearline` once the ToP have be produced
- Contrary to SenseDoc data, Ethica data are subject to various unexplained data errors, most notably duplicated timestamps; these data errors are removed from the _Elite files_

## Produce data

For each city/wave/participant:
1. Load transformed GPS and AXL data from CSV (see _Load and transfom data_ above)
2. Merge both data streams into ToP, aggregated at 1sec and 5min epochs.
3. Export to pg database; one table per city/wave/epoch
4. Export to CSV, including `city_id`, `wave_id`, `interact_id`, `epoch` at the record level

### Notes
- Due to the specificity of the data acquisition pattern, no PA levels (_ie._ accelerometry counts) are computed for Ethica AXL as the standard algorithm cannot be used with the data
