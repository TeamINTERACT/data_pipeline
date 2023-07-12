Wave 2 Victoria Linkage
================
Daniel Fuller

# Victoria Wave 2 Linkage Files

### Read in Data

Reading in the data. Here we are reading in two files

-   `linkage_for_ingest_vic_w2.csv` which is our main file
-   `lut_vic2.csv` which is a look up table for looking up previous
    versions of the health and VERITAS ID variables. These will not be
    used after Wave 1.

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
vic <- read_delim("linkage_for_ingest_vic_w2.csv", delim = ";", name_repair = "universal")
```

    ## New names:
    ## Rows: 315 Columns: 22
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: ";" chr
    ## (6): date_range_messy, Ethica.Dates.2019, Health.Survey, VERITAS.Survey... dbl
    ## (7): interact_id, sensedoc_serial, sensedoc_revno, sd_id_2, sd_firmware... lgl
    ## (5): ...16, ...17, ...18, ...19, ...21 date (4): start_date, end_date,
    ## sd_start_2, sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `Ethica ID` -> `Ethica.ID`
    ## • `Ethica Dates 2019` -> `Ethica.Dates.2019`
    ## • `Health Survey` -> `Health.Survey`
    ## • `VERITAS Survey` -> `VERITAS.Survey`
    ## • `` -> `...16`
    ## • `` -> `...17`
    ## • `` -> `...18`
    ## • `` -> `...19`
    ## • `` -> `...21`

``` r
lut_vic <- read_delim("lut_vic2.csv", delim = ",", name_repair = "universal")
```

    ## Rows: 451 Columns: 3
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ","
    ## dbl (3): interact_id, treksoft_uid, treksoft_pid
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
vic_w2 <- full_join(vic, lut_vic, by = "interact_id")
colnames(vic_w2)
```

    ##  [1] "interact_id"       "sensedoc_serial"   "sensedoc_revno"   
    ##  [4] "start_date"        "end_date"          "date_range_messy" 
    ##  [7] "sd_id_2"           "sd_firmware_2"     "sd_start_2"       
    ## [10] "sd_end_2"          "Ethica.ID"         "Ethica.Dates.2019"
    ## [13] "Health.Survey"     "VERITAS.Survey"    "Notes"            
    ## [16] "...16"             "...17"             "...18"            
    ## [19] "...19"             "test"              "...21"            
    ## [22] "data_disposition"  "treksoft_uid"      "treksoft_pid"

### Rename variables

``` r
vic_w2 <- rename(vic_w2, 
                 sd_id_1 = sensedoc_serial,
                 ethica_id = Ethica.ID,
                 sd_start_1 = start_date,
                 sd_end_1 = end_date,
                 sd_firmware_1 = sensedoc_revno)
```

### Keeping variables

``` r
vic_w2 <- select(vic_w2, interact_id, ethica_id, sd_id_1, sd_start_1, sd_end_1, sd_id_2, sd_start_2, sd_end_2, data_disposition)
```

### Flag test accounts

``` r
ethica_tests <- c("1451", "2036", 
                  "5256", "1454", 
                  "8911", "1469",
                  "1462", "9321", 
                  "12641", "12638", 
                  "12617", "1470",
                  "4579", "5367",
                  "5399","3962")
```

``` r
vic_w2 <- vic_w2 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

### Adding columns

``` r
vic_w2$dropout <- NA
vic_w2$plg_id <- NA
vic_w2$wave <- 2
```

### Write clean file

``` r
write.csv(vic_w2, file= "linkage_vic_w2.csv")
```
