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

### Summary

```
===== VALIDATING Montreal | Wave 1 =====
ERROR: Unable to find directory <montreal/wave_01/sensedoc/401627014_188>  | Jeff dit ignore
ERROR: Unable to find directory <montreal/wave_01/sensedoc/401751741_51>   | Jeff dit ignore
ERROR: Unable to find directory <montreal/wave_01/sensedoc/401679813_146>  | Jeff dit ignore
===== VALIDATING Montreal | Wave 2 =====
===== VALIDATING Montreal | Wave 3 =====
ERROR: Unable to find directory <montreal/wave_03/sensedoc/401952301_23>   | Jeff dit ignore
===== VALIDATING Saskatoon | Wave 1 =====
ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302610266_367> | Jeff dit ignore
ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302923081_367> | Jeff dit ignore
ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302273130_375> | Jeff dit ignore
===== VALIDATING Saskatoon | Wave 2 =====
ERROR: Unable to find directory <saskatoon/wave_02/sensedoc/302955394_383> | Jeff dit ignore
===== VALIDATING Saskatoon | Wave 3 =====
===== VALIDATING Vancouver | Wave 1 =====
===== VALIDATING Vancouver | Wave 2 =====
ERROR: Unable to find directory <vancouver/wave_02/sensedoc/202634537_491> | Zoé dit ignore! see sd_id_2
===== VALIDATING Vancouver | Wave 3 =====
===== VALIDATING Victoria | Wave 1 =====
ERROR: Unable to find directory <victoria/wave_01/sensedoc/101158091_23>   | missing file - c'est ok!
ERROR: Unable to find directory <victoria/wave_01/sensedoc/101891218_111>  | Zoé dit ignore see sd_id_2
===== VALIDATING Victoria | Wave 2 =====
===== VALIDATING Victoria | Wave 3 =====
ERROR: Unable to find directory <victoria/wave_03/sensedoc/101847191_405>  | Jeff dit ignore

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
Vancouver | Wave 3 |             76 |             79 |          79 | OK
Victoria  | Wave 1 |            155 |            165 |         163 | Missing SD files
Victoria  | Wave 2 |            130 |            134 |         134 | OK
Victoria  | Wave 3 |             89 |             91 |          90 | Missing SD files

==== SECOND STEP VALIDATION ====
Ok
```

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

### Summary

```
==== PROCESSING REPORT | GPS ====
City      | Wave   |   Error |   OK |   Skipped
-----------+--------+---------+------+-----------
Montreal  | Wave 1 |       0 |    5 |       157
Montreal  | Wave 2 |       0 |    2 |        43
Montreal  | Wave 3 |       0 |    2 |        52
Saskatoon | Wave 1 |       0 |   20 |        91
Saskatoon | Wave 2 |       1 |    1 |        31
Saskatoon | Wave 3 |       0 |    0 |        10
Vancouver | Wave 1 |       0 |    3 |       149
Vancouver | Wave 2 |       0 |    4 |        86
Vancouver | Wave 3 |       0 |    5 |        74
Victoria  | Wave 1 |       0 |    4 |       159
Victoria  | Wave 2 |       0 |    1 |       133
Victoria  | Wave 3 |       0 |    0 |        90

==== PROCESSING REPORT | AXL ====
City      | Wave   |   Error |   OK |   Skipped
-----------+--------+---------+------+-----------
Montreal  | Wave 1 |       0 |    5 |       157
Montreal  | Wave 2 |       0 |    2 |        43
Montreal  | Wave 3 |       0 |    2 |        52
Saskatoon | Wave 1 |       0 |   16 |        95
Saskatoon | Wave 2 |       1 |    1 |        31
Saskatoon | Wave 3 |       0 |    0 |        10
Vancouver | Wave 1 |       1 |    2 |       149
Vancouver | Wave 2 |       0 |    4 |        86
Vancouver | Wave 3 |       0 |    5 |        74
Victoria  | Wave 1 |       0 |    3 |       160
Victoria  | Wave 2 |       0 |    1 |       133
Victoria  | Wave 3 |       0 |    0 |        90
```
_NB_ Skipped datasets have been computed in a previous run and should be counted as _OK_.

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

### Summary:

```
==== PROCESSING REPORT | ToP ====
City   |   Wave |   Error |   OK
--------+--------+---------+------
mtl    |      1 |       1 |  160
mtl    |      2 |       1 |   44
mtl    |      3 |       1 |   53
skt    |      1 |      18 |   93
skt    |      2 |       0 |   32
skt    |      3 |       0 |   10
van    |      1 |       3 |  149
van    |      2 |       3 |   87
van    |      3 |       3 |   76
vic    |      1 |       1 |  162
vic    |      2 |       0 |  134
vic    |      3 |       0 |   90
```

### Validating ToP errors

Python script `sensedoc/ETL/top_error.py` scans the list of elites files and compare them with the ToP records found in database. Any combination of `interact_id`/`sd_id` not found in database is then flagged and the corresponding GPS/AXL files loaded to check for emptyness.

```
   City  Wave        IID   SD
0   mtl     1  401809034  146
1   skt     1  302061859  391
2   skt     1  302265135  441
3   skt     1  302318839  407
4   skt     1  302330481  399
5   skt     1  302394560  408
6   skt     1  302429590  451
7   skt     1  302431853  369
8   skt     1  302487100  403
9   skt     1  302530348  345
10  skt     1  302531549  466
11  skt     1  302591105  426
12  skt     1  302631120  356
13  skt     1  302631199  420
14  skt     1  302641169  391
15  skt     1  302700417  409
16  skt     1  302756755  373
17  skt     1  302832294  439
18  skt     1  302862878  405
19  van     1  201057630  435
20  van     1  201642869  428
21  van     1  201810690  444
22  vic     1  101214983  122
23  mtl     2  402495712   36
24  van     2  201259654  369
25  van     2  201398316  462
26  van     2  202141573  473
27  mtl     3  403835859  109
28  van     3  201210287  349
29  van     3  202116714  403
30  van     3  202662394  401
```

**Conclusion**: all the errors listed above have empty GPS and/or AXL files.

### Adjusting grants on top tables in database

```sql
GRANT USAGE ON SCHEMA top_sd, top_sd2, top_sd3 TO group_dfuller;
GRANT SELECT ON ALL TABLES IN SCHEMA top_sd, top_sd2, top_sd3 TO group_dfuller;
```

# SenseDoc Quality Checks

See `QA` subfolder.
