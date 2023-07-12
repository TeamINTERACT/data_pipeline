Linkage File Check
================
Daniel Fuller

## Check linkage files

This code provides some high level checks for the linkage files related
to variable names, types, appending, and working with the data.

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")

skt_w1 <- read_csv("linkage_skt_w1.csv")
```

    ## New names:
    ## Rows: 403 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (9): ...1, interact_id, treksoft_pid, treksoft_uid,
    ## ethica_id, sd_id_1,... lgl (5): sd_firmware_1, sd_firmware_2, dropout, plg_id,
    ## spam_participant date (4): sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
skt_w2 <- read_csv("linkage_skt_w2.csv")
```

    ## New names:
    ## Rows: 644 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (7): ...1, interact_id, ethica_id, sd_id_1, sd_id_2,
    ## test, wave lgl (7): treksoft_pid, treksoft_uid, sd_firmware_1, sd_firmware_2,
    ## dropout,... date (4): sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
skt_w3 <- read_csv("linkage_skt_w3.csv")
```

    ## New names:
    ## Rows: 738 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): plg_id dbl (8): ...1, interact_id, ethica_id, sd_id_1, sd_firmware_1,
    ## dropout, tes... lgl (8): treksoft_pid, treksoft_uid, sd_id_2, sd_firmware_2,
    ## sd_start_2, sd... date (2): sd_start_1, sd_end_1
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
mtl_w1 <- read_csv("linkage_mtl_w1.csv")
```

    ## New names:
    ## Rows: 1539 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (12): ...1, interact_id, treksoft_pid, treksoft_uid,
    ## ethica_id, sd_id_1... lgl (2): plg_id, spam_participant date (4): sd_start_1,
    ## sd_end_1, sd_start_2, sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
mtl_w2 <- read_csv("linkage_mtl_w2.csv")
```

    ## New names:
    ## Rows: 1868 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (6): ...1, interact_id, ethica_id, sd_id_1, test,
    ## wave lgl (10): treksoft_pid, treksoft_uid, sd_firmware_1, sd_id_2,
    ## sd_firmware_2... date (2): sd_start_1, sd_end_1
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
mtl_w3 <- read_csv("linkage_mtl_w3.csv")
```

    ## New names:
    ## Rows: 789 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): plg_id dbl (8): ...1, interact_id, ethica_id, sd_id_1, sd_firmware_1,
    ## dropout, tes... lgl (8): treksoft_pid, treksoft_uid, sd_id_2, sd_firmware_2,
    ## sd_start_2, sd... date (2): sd_start_1, sd_end_1
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
van_w1 <- read_csv("linkage_van_w1.csv")
```

    ## New names:
    ## Rows: 381 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (9): ...1, interact_id, treksoft_pid, treksoft_uid,
    ## ethica_id, sd_id_1,... lgl (7): sd_id_2, sd_firmware_2, sd_start_2, sd_end_2,
    ## plg_id, dropout, spa... date (2): sd_start_1, sd_end_1
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
van_w2 <- read_csv("linkage_van_w2.csv")
```

    ## New names:
    ## Rows: 525 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (5): ...1, interact_id, ethica_id, wave, test lgl
    ## (9): treksoft_pid, treksoft_uid, sd_id_1, sd_firmware_1, sd_id_2, sd_fi... date
    ## (4): sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
van_w3 <- read_csv("linkage_van_w3.csv")
```

    ## New names:
    ## Rows: 304 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): plg_id dbl (10): ...1, interact_id, ethica_id, sd_id_1, sd_firmware_1,
    ## sd_id_2, sd... lgl (4): treksoft_pid, treksoft_uid, data_disposition,
    ## spam_participant date (4): sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
vic_w1 <- read_csv("linkage_vic_w1.csv")
```

    ## New names:
    ## Rows: 327 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (11): ...1, interact_id, treksoft_pid, treksoft_uid,
    ## ethica_id, sd_id_1... lgl (3): plg_id, dropout, spam_participant date (4):
    ## sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
vic_w2 <- read_csv("linkage_vic_w2.csv")
```

    ## New names:
    ## Rows: 457 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (11): ...1, interact_id, treksoft_pid, treksoft_uid,
    ## ethica_id, sd_id_1... lgl (3): plg_id, dropout, spam_participant date (4):
    ## sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

``` r
vic_w3 <- read_csv("linkage_vic_w3.csv")
```

    ## New names:
    ## Rows: 527 Columns: 19
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (1): data_disposition dbl (9): ...1, interact_id, ethica_id, sd_id_1,
    ## sd_firmware_1, sd_id_2, sd_... lgl (5): treksoft_pid, treksoft_uid, plg_id,
    ## dropout, spam_participant dttm (1): sd_end_1 date (3): sd_start_1, sd_start_2,
    ## sd_end_2
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `` -> `...1`

All datasets have 19 variables.

## Compare column types

### Saskatoon

``` r
compare_df_cols(skt_w1, skt_w2, return = "mismatch")
```

    ##    column_name  skt_w1  skt_w2
    ## 1 treksoft_pid numeric logical
    ## 2 treksoft_uid numeric logical

``` r
compare_df_cols(skt_w1, skt_w3, return = "mismatch")
```

    ##        column_name    skt_w1    skt_w3
    ## 1 data_disposition character   logical
    ## 2          dropout   logical   numeric
    ## 3           plg_id   logical character
    ## 4         sd_end_2      Date   logical
    ## 5    sd_firmware_1   logical   numeric
    ## 6          sd_id_2   numeric   logical
    ## 7       sd_start_2      Date   logical
    ## 8     treksoft_pid   numeric   logical
    ## 9     treksoft_uid   numeric   logical

``` r
compare_df_cols(skt_w2, skt_w3, return = "mismatch")
```

    ##        column_name    skt_w2    skt_w3
    ## 1 data_disposition character   logical
    ## 2          dropout   logical   numeric
    ## 3           plg_id   logical character
    ## 4         sd_end_2      Date   logical
    ## 5    sd_firmware_1   logical   numeric
    ## 6          sd_id_2   numeric   logical
    ## 7       sd_start_2      Date   logical

``` r
skt_all_waves <- bind_rows(skt_w1, skt_w2, skt_w3)
```

`bind_rows` seems to work alright so I’m going to leave this as is. Most
of the mismatch is coming from the variables we add that are in wave 1
but not in waves 2 or 3.

### Montreal

``` r
compare_df_cols(mtl_w1, mtl_w2, return = "mismatch")
```

    ##     column_name  mtl_w1  mtl_w2
    ## 1       dropout numeric logical
    ## 2      sd_end_2    Date logical
    ## 3 sd_firmware_1 numeric logical
    ## 4 sd_firmware_2 numeric logical
    ## 5       sd_id_2 numeric logical
    ## 6    sd_start_2    Date logical
    ## 7  treksoft_pid numeric logical
    ## 8  treksoft_uid numeric logical

``` r
compare_df_cols(mtl_w1, mtl_w3, return = "mismatch")
```

    ##        column_name    mtl_w1    mtl_w3
    ## 1 data_disposition character   logical
    ## 2           plg_id   logical character
    ## 3         sd_end_2      Date   logical
    ## 4    sd_firmware_2   numeric   logical
    ## 5          sd_id_2   numeric   logical
    ## 6       sd_start_2      Date   logical
    ## 7     treksoft_pid   numeric   logical
    ## 8     treksoft_uid   numeric   logical

``` r
compare_df_cols(mtl_w2, mtl_w3, return = "mismatch")
```

    ##        column_name    mtl_w2    mtl_w3
    ## 1 data_disposition character   logical
    ## 2          dropout   logical   numeric
    ## 3           plg_id   logical character
    ## 4    sd_firmware_1   logical   numeric

``` r
mtl_all_waves <- bind_rows(mtl_w1, mtl_w2, mtl_w3)
```

I had to go back and fix the Montreal W2 linkage file because for some
reason it was writing the `sd_id_1` variable as character.

### Vancouver

``` r
compare_df_cols(van_w1, van_w2, return = "mismatch")
```

    ##     column_name  van_w1  van_w2
    ## 1      sd_end_2 logical    Date
    ## 2 sd_firmware_1 numeric logical
    ## 3       sd_id_1 numeric logical
    ## 4    sd_start_2 logical    Date
    ## 5  treksoft_pid numeric logical
    ## 6  treksoft_uid numeric logical

``` r
compare_df_cols(van_w1, van_w3, return = "mismatch")
```

    ##        column_name    van_w1    van_w3
    ## 1 data_disposition character   logical
    ## 2          dropout   logical   numeric
    ## 3           plg_id   logical character
    ## 4         sd_end_2   logical      Date
    ## 5    sd_firmware_2   logical   numeric
    ## 6          sd_id_2   logical   numeric
    ## 7       sd_start_2   logical      Date
    ## 8     treksoft_pid   numeric   logical
    ## 9     treksoft_uid   numeric   logical

``` r
compare_df_cols(van_w2, van_w3, return = "mismatch")
```

    ##        column_name    van_w2    van_w3
    ## 1 data_disposition character   logical
    ## 2          dropout   logical   numeric
    ## 3           plg_id   logical character
    ## 4    sd_firmware_1   logical   numeric
    ## 5    sd_firmware_2   logical   numeric
    ## 6          sd_id_1   logical   numeric
    ## 7          sd_id_2   logical   numeric

``` r
van_all_waves <- bind_rows(van_w1, van_w2, van_w3)
```

I had to go back and fix the Vancouver W3 linkage file because for some
reason it was writing the `sd_id_1`, `sd_id_2`, and `interact_id`
variables as character.

### Victoria

``` r
compare_df_cols(vic_w1, vic_w2, return = "mismatch")
```

    ## [1] column_name vic_w1      vic_w2     
    ## <0 rows> (or 0-length row.names)

``` r
compare_df_cols(vic_w1, vic_w3, return = "mismatch")
```

    ##    column_name  vic_w1          vic_w3
    ## 1     sd_end_1    Date POSIXct, POSIXt
    ## 2 treksoft_pid numeric         logical
    ## 3 treksoft_uid numeric         logical

``` r
compare_df_cols(vic_w2, vic_w3, return = "mismatch")
```

    ##    column_name  vic_w2          vic_w3
    ## 1     sd_end_1    Date POSIXct, POSIXt
    ## 2 treksoft_pid numeric         logical
    ## 3 treksoft_uid numeric         logical

``` r
vic_all_waves <- bind_rows(vic_w1, vic_w2, vic_w3)
```

I had to go back and fix the Victoria W1 linkage file because the
`sd_end_2`, `sd_start_2` variables were character.

### Binding everything together

``` r
compare_df_cols(skt_all_waves, mtl_all_waves, return = "mismatch")
```

    ##     column_name skt_all_waves mtl_all_waves
    ## 1 sd_firmware_2       logical       numeric

``` r
compare_df_cols(skt_all_waves, van_all_waves, return = "mismatch")
```

    ##     column_name skt_all_waves van_all_waves
    ## 1 sd_firmware_2       logical       numeric

``` r
compare_df_cols(skt_all_waves, vic_all_waves, return = "mismatch")
```

    ##     column_name skt_all_waves   vic_all_waves
    ## 1       dropout       numeric         logical
    ## 2        plg_id     character         logical
    ## 3      sd_end_1          Date POSIXct, POSIXt
    ## 4 sd_firmware_2       logical         numeric

``` r
compare_df_cols(mtl_all_waves, van_all_waves, return = "mismatch")
```

    ## [1] column_name   mtl_all_waves van_all_waves
    ## <0 rows> (or 0-length row.names)

``` r
compare_df_cols(mtl_all_waves, vic_all_waves, return = "mismatch")
```

    ##   column_name mtl_all_waves   vic_all_waves
    ## 1     dropout       numeric         logical
    ## 2      plg_id     character         logical
    ## 3    sd_end_1          Date POSIXct, POSIXt

``` r
compare_df_cols(van_all_waves, vic_all_waves, return = "mismatch")
```

    ##   column_name van_all_waves   vic_all_waves
    ## 1     dropout       numeric         logical
    ## 2      plg_id     character         logical
    ## 3    sd_end_1          Date POSIXct, POSIXt

``` r
all_waves_cities <- bind_rows(skt_all_waves, mtl_all_waves, van_all_waves, vic_all_waves)
```

Had to fix a bunch of stuff with `treksoft_pid` and `treksoft_uid` for
Vancouver and Victoria. Binding works now.
