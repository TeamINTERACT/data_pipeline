Wave 1 Victoria Linkage
================
Daniel Fuller

# Victoria Wave 1 Linkage Files

### Read in Data

Reading in the data. Here we are reading in two files

- `linkage_for_ingest_vic_w1.csv` which is our main file
- `lut_vic.csv` which is a look up table for looking up previous
  versions of the health and VERITAS ID variables. These will not be
  used after Wave 1.

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
#setwd("C:/Users/zoepo/Documents/Data/Linkages")

vic_w1 <- read_delim("linkage_for_ingest_vic_w1.csv", delim = ";")
```

    ## Rows: 327 Columns: 15
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## chr (7): Sensedoc participant ID, dates, ethica_id, sd_start_2, sd_end_2, da...
    ## dbl (6): interact_id, treksoft_id, sd_id_1, sd_firmware_1, sd_id_2, sd_firmw...
    ## lgl (2): d, e
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
lut_vic <- read_delim("lut_vic.csv", delim = ",")
```

    ## Rows: 309 Columns: 4
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ","
    ## chr (1): ethica_id
    ## dbl (3): interact_id, treksoft_pid, treksoft_uid
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

### Fix dates

Linkage file used by Jeff is very messy. First step is to standardize
dates

``` r
vic_w1 <- separate(vic_w1, col = dates, into = c("sd_start_1_messy", "sd_end_1_messy"), sep = "-")
vic_w1 <- rename(vic_w1, 
                sd_start_2_messy = sd_start_2,
                sd_end_2_messy = sd_end_2)
```

Fixing the start dates for SenseDoc

``` r
vic_w1$sd_start_1 <- parse_date_time(vic_w1$sd_start_1_messy, orders = c("md", "dm"))
year(vic_w1$sd_start_1) <- 2017


vic_w1$sd_start_2 <- parse_date_time(vic_w1$sd_start_2_messy, orders = c("dmy"))
```

Fixing the end dates for SenseDoc

``` r
vic_w1$sd_end_1 <- parse_date_time(vic_w1$sd_end_1_messy, orders = c("mdy", "dmy", "md", "dm"))

vic_w1$sd_end_2 <- parse_date_time(vic_w1$sd_end_2_messy, orders = c("dmy"))
```

Spot checked text dates with parsed dates

``` r
date_review <- select(vic_w1, sd_start_1_messy, sd_end_1_messy, sd_start_1, sd_end_1)

date_review <- select(vic_w1, sd_start_2_messy, sd_end_2_messy, sd_start_2, sd_end_2)
```

Looks good. Looks good for sd_id_2 too.

## Join LUT with vic_w1

Join Benoit’s LUT and check if IDs match \#309 records

``` r
vic_w1 <- full_join(vic_w1, lut_vic, by="interact_id")
vic_w1$match <- ifelse(vic_w1$treksoft_pid == vic_w1$treksoft_id, "yes", "no")
table(vic_w1$match)
```

    ## 
    ## yes 
    ## 309

Complete match on PID confirmed

### Harmonize Columns

``` r
vic_w1 <- rename(vic_w1, ethica_id = ethica_id.x)
```

Remove text notes in Ethica id and Sensedoc ID field

``` r
non_numeric <- grepl("[^0-9]", vic_w1$ethica_id)
vic_w1$ethica_id[non_numeric] <- NA
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
vic_w1 <- vic_w1 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

### Adding columns

``` r
vic_w1$plg_id <- NA
vic_w1$dropout <- NA
vic_w1$spam_participant <- NA
vic_w1$wave <- 1

# vic_w1$sd_end_2 <- as.Date(vic_w1$sd_end_2)
# vic_w1$sd_start_2 <- as.Date(vic_w1$sd_start_2)

vic_w1$treksoft_pid <- as.numeric(vic_w1$treksoft_pid)
vic_w1$treksoft_uid <- as.numeric(vic_w1$treksoft_uid)
```

### Selecting variables

``` r
vic_w1 <- select(vic_w1, interact_id, treksoft_pid, treksoft_uid, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, data_disposition, plg_id, dropout, wave, test, spam_participant)
```

### Write clean file

``` r
write.csv(vic_w1, file= "linkage_vic_w1.csv")
```
