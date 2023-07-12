Wave 1 Montreal Linkage
================
Daniel Fuller

# Montreal Wave 1 Linkage Files

### Read in Data

Reading in the data. Here we are reading in two files

-   `linkage_for_ingest_mtl_w1.csv` which is our main file
-   `lut_mtl.csv` which is a look up table for looking up previous
    versions of the health and VERITAS ID variables. These will not be
    used after Wave 1.

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
mtl <- read_delim("linkage_for_ingest_mtl_w1.csv", delim = ";")
```

    ## Rows: 1539 Columns: 14
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## chr  (1): data_disposition
    ## dbl  (8): interact_id, uid, ethica_id, sd_id_1, sd_firmware_1, sd_id_2, sd_f...
    ## lgl  (1): test
    ## date (4): sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
lut_mtl <- read_delim("lut_mtl.csv", delim = ",")
```

    ## Rows: 1536 Columns: 4
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ","
    ## chr (1): ethica_id
    ## dbl (3): interact_id, treksoft_pid, treksoft_uid
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

### Compare IDs between tables

``` r
mtl_w1 <- full_join(mtl, lut_mtl, by="interact_id")
mtl_w1$eth_check <- ifelse(mtl_w1$ethica_id.x == mtl_w1$ethica_id.y, "yes", "no")
table(mtl_w1$eth_check)
```

    ## 
    ##  no yes 
    ##   4 568

4 ethica IDs not in BT’s table but present in mine. Keep longer list of
mine.

``` r
mtl_w1$uid_check <- ifelse(mtl_w1$uid == mtl_w1$treksoft_uid, "yes", "no")
table(mtl_w1$uid_check)
```

    ## 
    ##  yes 
    ## 1536

all uid match

### Keeping variables

``` r
mtl_w1 <- rename(mtl_w1, 
                 ethica_id = ethica_id.x)
```

``` r
mtl_w1 <- select(mtl_w1, interact_id, treksoft_pid, treksoft_uid, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, dropout, data_disposition, test)
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
mtl_w1 <- mtl_w1 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

### Adding columns

``` r
mtl_w1$plg_id <- NA
mtl_w1$wave <- 1
```

### Write clean file

``` r
write.csv(mtl_w1, file= "linkage_mtl_w1.csv")
```
