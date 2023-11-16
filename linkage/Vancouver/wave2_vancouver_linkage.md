Wave 2 Vancouver Linkage
================
Daniel Fuller

# Vancouver Wave 2 Linkage Files

### Read in Data

Reading in the data. Here we are reading in two files

- `linkage_for_ingest_van_w2.csv` which is our main file

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
#setwd("C:/Users/zoepo/Documents/Data/Linkages")

van_w2 <- read_delim("linkage_for_ingest_van_w2.csv", delim = ";")
```

    ## New names:
    ## Rows: 525 Columns: 15
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: ";" chr
    ## (4): sensedoc1_id, sensedoc2_id, sensedoc3_id, data_disposition dbl (3): ...1,
    ## interact_id, ethica_id dttm (8): ethica_start_date, ethica_end_date,
    ## sensedoc1_wear_start_date, sen...
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

### Rename variables

``` r
van_w2 <- rename(van_w2, sd_id_1 = sensedoc1_id,
                ethica_start = ethica_start_date, 
                ethica_end = ethica_end_date,
                sd_start_1 = sensedoc1_wear_start_date,
                sd_end_1 = sensedoc1_wear_end_date,
                sd_id_2 = sensedoc2_id,
                sd_start_2 = sensedoc2_wear_start_date,
                sd_end_2 = sensedoc2_wear_end_date, 
                sd_id_3 = sensedoc3_id,
                sd_start_3 = sensedoc3_wear_start_date,
                sd_end_3 = sensedoc3_wear_end_date)
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
van_w2 <- van_w2 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

### Adding columns

``` r
#van_w2$sd_firmware_1 <- NA
#van_w2$sd_firmware_2 <- NA
van_w2$dropout <- NA
van_w2$treksoft_pid <- NA
van_w2$treksoft_uid <- NA
van_w2$plg_id <- NA
van_w2$spam_participant <- NA
van_w2$wave <- 2
```

### Separate sd_id and sd_firmware

``` r
van_w2 <- separate(van_w2, col = sd_id_1, into = c("sd_id_1", "sd_firmware_1"), sep = "-")
van_w2 <- separate(van_w2, col = sd_id_2, into = c("sd_id_2", "sd_firmware_2"), sep = "-")
van_w2 <- separate(van_w2, col = sd_id_3, into = c("sd_id_3", "sd_firmware_3"), sep = "-")
```

### Make fields numeric

``` r
van_w2$sd_id_1 <- as.numeric(van_w2$sd_id_1)
van_w2$sd_id_2 <- as.numeric(van_w2$sd_id_2)
van_w2$sd_id_3 <- as.numeric(van_w2$sd_id_3)


van_w2$interact_id <- as.numeric(van_w2$interact_id)
van_w2$treksoft_pid <- as.numeric(van_w2$treksoft_pid)
van_w2$treksoft_uid <- as.numeric(van_w2$treksoft_uid)
```

### Selecting variables

``` r
van_w2 <- select(van_w2, interact_id, treksoft_pid, treksoft_uid, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, sd_id_3, sd_firmware_3, sd_start_3, sd_end_3, data_disposition, plg_id, dropout, wave, test, spam_participant)
```

### Write clean file

``` r
write.csv(van_w2, file= "linkage_van_w2.csv")
```
