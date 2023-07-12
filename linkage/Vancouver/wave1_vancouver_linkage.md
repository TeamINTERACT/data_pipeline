Wave 1 Vancouver Linkage
================
Daniel Fuller

# Vancouver Wave 1 Linkage Files

### Read in Data

Reading in the data. Here we are reading in two files

-   `linkage_for_ingest_van_w1.csv` which is our main file
-   `lut_van.csv` which is a look up table for looking up previous
    versions of the health and VERITAS ID variables. These will not be
    used after Wave 1.

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
van <- read_delim("linkage_for_ingest_van_w1.csv", delim = ";")
```

    ## Rows: 381 Columns: 16
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## chr  (1): data_disposition
    ## dbl  (5): interact_id, ethica_id, sd_id_1, sd_firmware_1, NOTNEEDED_sticker_...
    ## lgl  (8): ethica_start, ethica_end, sd_id_2, sd_firmware_2, sd_start_2, sd_e...
    ## date (2): sd_start_1, sd_end_1
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
lut_van <- read_delim("lut_van.csv", delim = ",")
```

    ## Rows: 381 Columns: 4
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ","
    ## chr (3): ethica_id, treksoft_pid, treksoft_uid
    ## dbl (1): interact_id
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

### Compare IDs between tables

``` r
van_w1 <- full_join(van, lut_van, by="interact_id")
van_w1$eth_check <- ifelse(van_w1$ethica_id.x == van_w1$ethica_id.y, "yes", "no")
table(van_w1$eth_check)
```

    ## 
    ## yes 
    ## 135

4 ethica IDs not in BT’s table but present in mine. Keep longer list of
mine.

### Keeping variables

``` r
van_w1 <- rename(van_w1, 
                 ethica_id = ethica_id.x)
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
van_w1 <- van_w1 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

### Adding columns

``` r
van_w1$plg_id <- NA
van_w1$spam_participant <- NA
van_w1$wave <- 1
```

### Selecting variables

``` r
van_w1 <- select(van_w1, interact_id, treksoft_pid, treksoft_uid, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, data_disposition, plg_id, dropout, wave, test, spam_participant)
```

### Write clean file

``` r
write.csv(van_w1, file= "linkage_van_w1.csv")
```
