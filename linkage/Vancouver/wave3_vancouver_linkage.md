Wave 3 Vancouver Linkage
================
Daniel Fuller

# Vancouver Wave 3 Linkage Files

### Read in Data

Reading in the data. These are data are relatively different from Wave 1
and 2 as we have a separate file for each of the Polygone, Ethica, and
Sensedoc data sources. We are also moving to our naming convention of
extract, validate, etc for this document. Here we are reading in three
files

-   `INT-YVR-W3-PLG.csv` which is our main Polygon file
-   `INT-YVR-W3-ETH.csv` which is our main Ethica file
-   `INT-YVR-W3-SD.csv` which is our main Sensedoc file

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
w3_plg <- read_delim("INT-YVR-W3-PLG.csv", delim = ";", name_repair = "universal")
```

    ## New names:
    ## Rows: 804 Columns: 39
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: ";" chr
    ## (14): id, identifier, first.name, last.name, study.id, status, preferre... dbl
    ## (11): total.sessions.count, started.sessions.count, completed.sessions.... num
    ## (1): profile.ethnicity lgl (7): profile.sense.doc.1.id, profile.sense.doc.2.id,
    ## profile.sense.doc... dttm (5): created.at, registered.at, verified.at,
    ## first.session.activity.at... date (1): profile.birth.date
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `first-name` -> `first.name`
    ## • `last-name` -> `last.name`
    ## • `study-id` -> `study.id`
    ## • `preferred-locale` -> `preferred.locale`
    ## • `created-at` -> `created.at`
    ## • `registered-at` -> `registered.at`
    ## • `verified-at` -> `verified.at`
    ## • `first-session-activity-at` -> `first.session.activity.at`
    ## • `last-session-activity-at` -> `last.session.activity.at`
    ## • `total-sessions-count` -> `total.sessions.count`
    ## • `started-sessions-count` -> `started.sessions.count`
    ## • `completed-sessions-count` -> `completed.sessions.count`
    ## • `profile-city` -> `profile.city`
    ## • `profile-hear` -> `profile.hear`
    ## • `profile-help` -> `profile.help`
    ## • `profile-gender` -> `profile.gender`
    ## • `profile-income` -> `profile.income`
    ## • `profile-post-code` -> `profile.post.code`
    ## • `profile-birth-date` -> `profile.birth.date`
    ## • `profile-ethnicity` -> `profile.ethnicity`
    ## • `profile-sense-doc-1-id` -> `profile.sense.doc.1.id`
    ## • `profile-sense-doc-2-id` -> `profile.sense.doc.2.id`
    ## • `profile-street-address` -> `profile.street.address`
    ## • `profile-participant-type` -> `profile.participant.type`
    ## • `profile-primary-phone-number` -> `profile.primary.phone.number`
    ## • `profile-participation-option` -> `profile.participation.option`
    ## • `profile-secondary-phone-number` -> `profile.secondary.phone.number`
    ## • `profile-sense-doc-1-wear-end-date` -> `profile.sense.doc.1.wear.end.date`
    ## • `profile-sense-doc-2-wear-end-date` -> `profile.sense.doc.2.wear.end.date`
    ## • `profile-primary-phone-number-ext` -> `profile.primary.phone.number.ext`
    ## • `profile-primary-phone-number-type` -> `profile.primary.phone.number.type`
    ## • `profile-sense-doc-1-wear-start-date` ->
    ##   `profile.sense.doc.1.wear.start.date`
    ## • `profile-sense-doc-2-wear-start-date` ->
    ##   `profile.sense.doc.2.wear.start.date`
    ## • `profile-secondary-phone-number-ext` -> `profile.secondary.phone.number.ext`
    ## • `profile-street-address-complement` -> `profile.street.address.complement`
    ## • `profile-secondary-phone-number-type` ->
    ##   `profile.secondary.phone.number.type`

``` r
w3_eth <- read_delim("INT-YVR-W3-ETH.csv", delim = ";", name_repair = "universal")
```

    ## Rows: 79 Columns: 13
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## chr  (5): first_name, last_name, email, label, is_dropped
    ## dbl  (5): id, sessions_completed, sessions_expired, sessions_canceled, sessi...
    ## dttm (3): start_time, end_time, last_recorded_data
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
w3_sd <- read_delim("INT-YVR-W3-SD.csv", delim = ";", name_repair = "universal")
```

    ## Rows: 73 Columns: 9
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## dbl  (5): interact_id, sd_id_1, sd_firmware_1, sd_id_2, sd_firmware_2
    ## date (4): sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

### Validate

Only keep ids of people who have done eligibility

``` r
w3_plg <- filter(w3_plg, completed.sessions.count >= 1) 
```

### Rename columns

``` r
w3_plg <- rename(w3_plg, 
                 interact_id = study.id,
                 email = identifier, 
                 plg_id = id)

w3_eth <- rename(w3_eth, 
                 ethica_id = id,
                 ethica_start = start_time, 
                 ethica_end = end_time)
```

``` r
w3_plg <- select(w3_plg, interact_id, email, plg_id, status)
```

## Remove drop outs

Only using Polygon dropped out field, not Ethica. Polygon dashboard is
how coordinators tracked drop out. A drop out on Ethica, is just
understood as a drop from that study activity.

``` r
w3_plg$dropout <- ifelse(w3_plg$status=="dropped_out", 1, 0)
table(w3_plg$dropout)
```

    ## 
    ##   0   1 
    ## 294   8

``` r
w3_plg <- full_join(w3_plg, w3_eth, by= "email")

w3_sd$interact_id <- as.character(w3_sd$interact_id)

van_w3 <- full_join(w3_plg, w3_sd, by= "interact_id")
```

### Flag Ethica test

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

Here we create a 0/1 flag for Ethica test accounts.

``` r
van_w3 <- van_w3 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

## add 1 if test accounts

``` r
van_w3$test[van_w3$email== "moreno.zanotto@gmail.com"] <- 1  
van_w3$test[van_w3$email== "vancouver@teaminteract.ca"] <- 1  
van_w3$test[van_w3$email== "joalleva@gmail.com"] <- 1  
van_w3$test[van_w3$email== "mzanotto@sfu.ca"] <- 1  
van_w3$test[van_w3$email== "vancouver+noveritas@teaminteract.ca"] <- 1  
van_w3$test[van_w3$email== "test@teaminteract.ca"] <- 1  
van_w3$test[van_w3$email== "courtneyjross@gmail.com"] <- 1  
van_w3$test[van_w3$email== "testc@testc.com"] <- 1  
van_w3$test[van_w3$email== "vancouver+moved@teaminteract.ca"] <- 1

table(van_w3$test)
```

    ## 
    ##   0   1 
    ## 297   7

### Adding columns

Here we add the columns to have consistent columns across linkage files.

``` r
van_w3$data_disposition <- NA
van_w3$treksoft_pid <- NA
van_w3$treksoft_uid <- NA
van_w3$wave <- 3
```

## Keeping columns

``` r
van_w3 <- select(van_w3, interact_id, plg_id, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, dropout, test)
```

## Write clean csv file

``` r
write.csv(van_w3, file = "linkage_van_w3.csv")
```
