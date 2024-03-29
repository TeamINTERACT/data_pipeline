Wave 1 Saskatoon Linkage
================
Daniel Fuller

# Saskatoon Wave 1 Linkage Files

### Read in Data

Reading in the data. Here we are reading in two files

- `linkage_for_ingest_skt_w1.csv` which is our main file
- `lut_skt.csv` which is a look up table for looking up previous
  versions of the health and VERITAS ID variables. These will not be
  used after Wave 1.

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
#setwd("C:/Users/zoepo/Documents/Data/Linkages")

skt <- read_delim("linkage_for_ingest_skt_w1.csv", delim = ";")
```

    ## Rows: 401 Columns: 14
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## chr  (2): notes, data_disposition
    ## dbl  (4): interact_id, ethica_id, sd_id_1, sd_id_2
    ## lgl  (4): sd_firmware_1, sd_firmware_2, test, dropout
    ## date (4): sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
lut_skt <- read_delim("lut_skt.csv", delim = ",")
```

    ## Rows: 403 Columns: 4
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ","
    ## chr (1): ethica_id
    ## dbl (3): interact_id, treksoft_pid, treksoft_uid
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
skt_w1 <- full_join(skt, lut_skt, by="interact_id")
```

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
                  "5399","3962", "29609")
```

### Rename ethica

``` r
skt_w1 <- rename(skt_w1, ethica_id = ethica_id.x)
```

### Flag Ethica test

Here we create a 0/1 flag for Ethica test accounts.

``` r
skt_w1 <- skt_w1 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

### Adding columns

Here we add the columns

- `plg_id`: This is a ID column that will supersede the `treksoft_pid`
  and `treksoft_uid`. Note that the company Treksoft and Polygone are
  the same, they just changed names during the study period.
- `wave`: The wave ID for the study.

``` r
skt_w1$plg_id <- NA
skt_w1$spam_participant <- NA
skt_w1$wave <- 1
```

### Add treksoft IDs

Here we are adding the Treksoft (Health and VERITAS) IDs to the data.
These are `treksoft_pid` and `treksoft_uid`.

``` r
skt_w1 <- select(skt_w1, interact_id, treksoft_pid, treksoft_uid, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, data_disposition, dropout, test, plg_id, spam_participant, wave)
```

## Write clean csv file

``` r
write.csv(skt_w1, file = "linkage_skt_w1.csv")
```
