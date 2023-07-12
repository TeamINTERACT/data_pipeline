Wave 3 Montreal Linkage
================
Daniel Fuller

# Montreal Wave 3 Linkage Files

### Read in Data

Reading in the data. These are data are relatively different from Wave 1
and 2 as we have a separate file for each of the Polygone, Ethica, and
Sensedoc data sources. We are also moving to our naming convention of
extract, validate, etc for this document. Here we are reading in three
files

-   `participants-PGDashboard_MTL_W3-20230126.csv` which is our main
    Polygon file
-   `Ethicaparticipantsw3MTL_20230126.csv` which is our main Ethica file
-   `SD-Participant-Log-MTLw3.csv` which is our main Sensedoc file

``` r
setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
w3_plg <- read_delim("participants-PGDashboard_MTL_W3-20230126.csv", delim = ";", name_repair = "universal")
```

    ## New names:
    ## Rows: 4694 Columns: 40
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: ";" chr
    ## (13): id, identifier, first.name, last.name, status, preferred.locale, ... dbl
    ## (14): study.id, total.sessions.count, started.sessions.count, completed... num
    ## (1): profile.ethnicity lgl (6): profile.sense.doc.1.id, profile.sense.doc.2.id,
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
    ## • `profile-gentri` -> `profile.gentri`
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
w3_eth <- read_delim("Ethicaparticipantsw3MTL_20230126.csv", delim = ";", name_repair = "universal")
```

    ## Rows: 174 Columns: 13
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## chr  (3): first_name, last_name, email
    ## dbl  (5): ethica_id, sessions_completed, sessions_expired, sessions_canceled...
    ## lgl  (2): label, is_dropped
    ## dttm (3): start_time, end_time, last_recorded_data
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
w3_sd <- read_delim("SD-Participant-Log-MTLw3.csv", delim = ";", name_repair = "universal")
```

    ## Rows: 56 Columns: 9
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## dbl  (3): interact_id, sd_id_1, sd_firmware_1
    ## lgl  (4): sd_id_2, sd_firmware_2, sd_start_2, sd_end_2
    ## date (2): sd_start_1, sd_end_1
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
    ## 786   3

``` r
w3_plg <- full_join(w3_plg, w3_eth, by= "email")
mtl_w3 <- full_join(w3_plg, w3_sd, by= "interact_id")
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
mtl_w3 <- mtl_w3 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

## add 1 if test accounts

``` r
mtl_w3$test[mtl_w3$email == "mikayla.salmon-beitel@umontreal.ca"] <- 1  
mtl_w3$test[mtl_w3$email == "mikayla@teaminteract.ca"] <- 1  
```

### Adding columns

Here we add the columns to have consistent columns across linkage files.

``` r
mtl_w3$data_disposition <- NA
mtl_w3$treksoft_pid <- NA
mtl_w3$treksoft_uid <- NA
mtl_w3$wave <- 3
```

## Keeping columns

``` r
mtl_w3 <- select(mtl_w3, interact_id, plg_id, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, dropout, test)
```

## Write clean csv file

``` r
write.csv(mtl_w3, file = "linkage_mtl_w3.csv")
```
