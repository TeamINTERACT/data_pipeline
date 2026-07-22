# Ethica ETL

## Validate data

Scan each city/wave folder and report missing participants and/or SD data with no match according to linkage files

For each city/wave:
1. Read linkage file `interact_id`, `ethica_id`
2. Load unique `ethica_id` from raw files in GPS and AXL subfolders. Report any incomplete pair  {`interact_id`; `ethica_id`} for follow-up.

### Notes
- Ethica data format may have changed from year to year and will require some adaptation before being validated

### Summary

 City      | Wave   |   PIDs with Ethica |   PIDs missing Ethica |   Unknown Ethica users |   Partial data | Status
-----------+--------+--------------------+-----------------------+------------------------+----------------+--------------------------------
 Montreal  | Wave 1 |                557 |                    15 |                      3 |            464 | Incomplete/missing Ethica data
 Montreal  | Wave 2 |                164 |                    10 |                      1 |              2 | Incomplete/missing Ethica data
 Montreal  | Wave 3 |                162 |                    12 |                      0 |              1 | Incomplete/missing Ethica data
 Montreal  | Wave 4 |                189 |                     9 |                      1 |              3 | Incomplete/missing Ethica data
 Saskatoon | Wave 1 |                152 |                     8 |                     17 |            137 | Incomplete/missing Ethica data
 Saskatoon | Wave 2 |                 81 |                     5 |                      0 |              5 | Incomplete/missing Ethica data
 Saskatoon | Wave 3 |                 80 |                     1 |                      0 |              3 | Incomplete/missing Ethica data
 Saskatoon | Wave 4 |                 41 |                     2 |                      0 |              0 | Incomplete/missing Ethica data
 Vancouver | Wave 1 |                132 |                     3 |                      4 |              1 | Incomplete/missing Ethica data
 Vancouver | Wave 2 |                 92 |                     5 |                      0 |              0 | Incomplete/missing Ethica data
 Vancouver | Wave 3 |                 77 |                     0 |                      2 |              2 | Incomplete/missing Ethica data
 Vancouver | Wave 4 |                 85 |                     4 |                      1 |              3 | Incomplete/missing Ethica data
 Victoria  | Wave 1 |                150 |                     4 |                     19 |              1 | Incomplete/missing Ethica data
 Victoria  | Wave 2 |                138 |                     0 |                      1 |              0 | OK
 Victoria  | Wave 3 |                119 |                     3 |                      4 |              3 | Incomplete/missing Ethica data
 Victoria  | Wave 4 |                 81 |                     3 |                      3 |              0 | Incomplete/missing Ethica data

Many participants with partial data only have only completed the EMA portion of Ethica, not the AXL/GPS part.

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

### To be discussed/confirmed

- Processing steps (see [Hildebrand _et al_](https://www.ovid.com/jnls/acsm-msse/toc/2014/09000) and [van Hees _et al._](https://doi.org/10.1371/journal.pone.0061691)):
    - No filtering of axl data, we use the raw measurements
    - Compute ENMO at the sample level, whatever the sampling frequency
    - Reduce to 1s epoch by taking the mean of ENMOs
- How to flag non-wear period?
- Which method to extract PA levels from ENMO?
- Incidentally, should we add ENMO to SenseDoc?