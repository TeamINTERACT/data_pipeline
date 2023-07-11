Wave 2 Saskatoon Linkage
================
Daniel Fuller

# Saskatoon Wave 2 Linkage Files

### Read in Data

Reading in the data. Here we are reading in one files

-   `linkage_for_ingest_skt_w2.csv` which is our main file

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
skt_w2 <- read_delim("linkage_for_ingest_skt_w2.csv", delim = ",")
```

    ## New names:
    ## Rows: 644 Columns: 15
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (5): ...1, interact_id, ethica_id, sensedoc1_id,
    ## sensedoc2_id lgl (3): sensedoc3_id, sensedoc3_wear_start_date,
    ## sensedoc3_wear_end_date dttm (6): ethica_start_date, ethica_end_date,
    ## sensedoc1_wear_start_date, sen...
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

## Ethica test accounts

List of test accounts used by our research team to test the Ethica app.
These will be flagged later.

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

### Rename columns

``` r
skt_w2 <- rename(skt_w2, sd_id_1 = sensedoc1_id,
                ethica_start = ethica_start_date, 
                ethica_end = ethica_end_date,
                sd_start_1 = sensedoc1_wear_start_date,
                sd_end_1 = sensedoc1_wear_end_date,
                sd_id_2 = sensedoc2_id,
                sd_start_2 = sensedoc2_wear_start_date,
                sd_end_2 = sensedoc2_wear_end_date)
```

### Flag Ethica test

Here we create a 0/1 flag for Ethica test accounts.

``` r
skt_w2 <- skt_w2 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

### Adding columns

Here we add the columns to have consistent columns across linkage files.

``` r
skt_w2$sd_firmware_1 <- NA
skt_w2$sd_firmware_2 <- NA
skt_w2$dropout <- NA
skt_w2$treksoft_pid <- NA
skt_w2$treksoft_uid <- NA
skt_w2$plg_id <- NA
skt_w2$wave <- 2
```

## Keeping columns

``` r
skt_w2 <- select(skt_w2, interact_id, ethica_id, sd_id_1, sd_start_1, sd_end_1, sd_id_2, sd_start_2, sd_end_2, data_disposition)
```

## Write clean csv file

``` r
write.csv(skt_w2, file = "linkage_skt_w2.csv")
```
