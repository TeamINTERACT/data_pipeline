Wave 4 Saskatoon Linkage
================
Zoé Poirier Stephens

# Saskatoon Wave 4 Linkage Files

### Read in Data

Reading in the data. These are data are relatively different from Wave 1
and 2 as we have a separate file for each of the Polygon, Ethica, and
Sensedoc data sources. We are also moving to our naming convention of
extract, validate, etc for this document. Here we are reading in two
files. No SenseDoc data was collected in Saskatoon at w4. Those fields
are in the linkage file as NA.

- `plg_participants-20250117.csv` : a download of the participant csv
  from the PLG dashboard on Jan 17 2025.
- `study-3729-export-4-participation-2025-01-17-19-41-04.csv` : a
  download of the participant csv from the Avicenna dashboard on Jan 17
  2025.

``` r
##change the work directory to where you keep your files 

setwd("I:/Benoit/OneDrive - Universite de Montreal/Documents/PROJETS/INTERACT_2016/Donnees/Wave4/Saskatoon_linkages_w4")

## read in the latest plg and eth files: download the participant csv from PLG and Ethica, use those files. 
w4_plg <- read_delim("plg_participants-20250117.csv", delim = ",", name_repair = "universal")
```

    ## New names:
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
    ## • `profile-v-1-e` -> `profile.v.1.e`
    ## • `profile-v-1-h` -> `profile.v.1.h`
    ## • `profile-v-1-v` -> `profile.v.1.v`
    ## • `profile-v-2-e` -> `profile.v.2.e`
    ## • `profile-v-2-h` -> `profile.v.2.h`
    ## • `profile-v-2-v` -> `profile.v.2.v`
    ## • `profile-v-3-e` -> `profile.v.3.e`
    ## • `profile-v-3-h` -> `profile.v.3.h`
    ## • `profile-v-3-v` -> `profile.v.3.v`
    ## • `profile-city` -> `profile.city`
    ## • `profile-hear` -> `profile.hear`
    ## • `profile-help` -> `profile.help`
    ## • `profile-moved` -> `profile.moved`
    ## • `profile-gender` -> `profile.gender`
    ## • `profile-gentri` -> `profile.gentri`
    ## • `profile-income` -> `profile.income`
    ## • `profile-hear-txt` -> `profile.hear.txt`
    ## • `profile-hear-name` -> `profile.hear.name`
    ## • `profile-last-wave` -> `profile.last.wave`
    ## • `profile-post-code` -> `profile.post.code`
    ## • `profile-birth-date` -> `profile.birth.date`
    ## • `profile-ethnicity` -> `profile.ethnicity`
    ## • `profile-sd-interest` -> `profile.sd.interest`
    ## • `profile-street-address` -> `profile.street.address`
    ## • `profile-ethica-interest` -> `profile.ethica.interest`
    ## • `profile-participant-type` -> `profile.participant.type`
    ## • `profile-primary-phone-number` -> `profile.primary.phone.number`
    ## • `profile-latest-questionnaire` -> `profile.latest.questionnaire`
    ## • `profile-secondary-phone-number` -> `profile.secondary.phone.number`
    ## • `profile-primary-phone-number-ext` -> `profile.primary.phone.number.ext`
    ## • `profile-primary-phone-number-type` -> `profile.primary.phone.number.type`
    ## • `profile-secondary-phone-number-ext` -> `profile.secondary.phone.number.ext`
    ## • `profile-street-address-complement` -> `profile.street.address.complement`
    ## • `profile-secondary-phone-number-type` ->
    ##   `profile.secondary.phone.number.type`

    ## Warning: One or more parsing issues, call `problems()` on your data frame for details,
    ## e.g.:
    ##   dat <- vroom(...)
    ##   problems(dat)

    ## Rows: 1721 Columns: 49
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ","
    ## chr  (13): id, identifier, first.name, last.name, status, preferred.locale, ...
    ## dbl  (14): study.id, total.sessions.count, started.sessions.count, completed...
    ## num   (1): profile.ethnicity
    ## lgl   (5): profile.gentri, profile.hear.txt, profile.hear.name, profile.sd.i...
    ## dttm  (5): created.at, registered.at, verified.at, first.session.activity.at...
    ## date (11): profile.v.1.e, profile.v.1.h, profile.v.1.v, profile.v.2.e, profi...
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

``` r
w4_eth <- read_delim("study-3729-export-4-participation-2025-01-17-19-41-04.csv", delim = ",", name_repair = "universal")
```

    ## New names:
    ## Rows: 43 Columns: 14
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (6): Participant.Type, First.Name, Last.Name, Email.Address, Devices, S... dbl
    ## (3): ID, Status, In.Operation lgl (1): Label dttm (4): Participant.Joined.Date,
    ## Start.Time, End.Time, Last.Recorded.Data....
    ## ℹ Use `spec()` to retrieve the full column specification for this data. ℹ
    ## Specify the column types or set `show_col_types = FALSE` to quiet this message.
    ## • `Participant Joined Date` -> `Participant.Joined.Date`
    ## • `Start Time` -> `Start.Time`
    ## • `End Time` -> `End.Time`
    ## • `Last Recorded Data Time` -> `Last.Recorded.Data.Time`
    ## • `In Operation` -> `In.Operation`
    ## • `Participant Type` -> `Participant.Type`
    ## • `First Name` -> `First.Name`
    ## • `Last Name` -> `Last.Name`
    ## • `Email Address` -> `Email.Address`
    ## • `Session Stats` -> `Session.Stats`

### Validate

For the linkage file: only keep ids of people who have done eli

``` r
w4_plg <- filter(w4_plg, completed.sessions.count >= 1) 
```

### Rename columns

``` r
w4_plg <- rename(w4_plg, 
                 interact_id = study.id,
                 email = identifier, 
                 plg_id = id)

w4_eth <- rename(w4_eth, 
                  ethica_start = Start.Time, 
                  ethica_end = End.Time, 
                  email = Email.Address, 
                  ethica_id = ID)
```

``` r
w4_plg <- select(w4_plg, interact_id, email, plg_id, status)
```

## Flag deactivated accounts, dropped_out accounts.

Polygon dashboard is how coordinators tracked drop out participants. A
drop out on Ethica, is just understood as a drop from that study
activity.

(Nota: PLG has different labels to designate a drop out. The plg status
‘deactivated’ is renamed to dropped out here)

How coordinators used the two statuses at w4:

- Désinscrit : Unsubscribed from e-mailings for the Wave. Can contact in
  future recruitment years.

- Désactivé : Account deactivated – no longer an INTERACT participant.
  Do not contact in future years. Includes spam accounts, those no
  longer living in a study city (or otherwise ineligible), people
  without valid contact information (e.g., unresponsive, undeliverable
  email, or invalid phone number), and those requesting to withdraw from
  the study.

``` r
w4_plg$dropout <- ifelse(w4_plg$status=="deactivated", 1, 0)

## join PLG with Ethica 

skt_w4 <- full_join(w4_plg, w4_eth, by= "email") 
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
skt_w4 <- skt_w4 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 
```

## add 1 if test accounts

If you used a test account add the email here:

``` r
# skt_w4$test[skt_w4$email== "##"] <- 1  
```

### Fix unmatched ethica users

``` r
skt_w4 <- skt_w4 |>
  filter(!(ethica_id %in% c(7324)))

skt_w4[skt_w4$interact_id == "302541389" & !is.na(skt_w4$interact_id),"ethica_id"] <- 7324
```

### Adding columns

Here we add the columns to have consistent columns across linkage files.

``` r
skt_w4$data_disposition <- NA
skt_w4$treksoft_pid <- NA
skt_w4$treksoft_uid <- NA
skt_w4$spam_participant <- 0 # No spam participant in Saskatoon
skt_w4$wave <- 4

## adding the sd fields as empty
skt_w4$sd_id_1  <- NA
skt_w4$sd_firmware_1  <- NA
skt_w4$sd_start_1  <- NA
skt_w4$sd_end_1  <- NA
skt_w4$sd_id_2  <- NA
skt_w4$sd_firmware_2  <- NA
skt_w4$sd_start_2  <- NA
skt_w4$sd_end_2  <- NA

skt_w4$interact_id <- as.numeric(skt_w4$interact_id)

skt_w4$treksoft_pid <- as.numeric(skt_w4$treksoft_pid)
skt_w4$treksoft_uid <- as.numeric(skt_w4$treksoft_uid)
```

### Selecting variables

``` r
skt_w4 <- select(skt_w4, interact_id, treksoft_pid, treksoft_uid, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, data_disposition, plg_id, dropout, wave, test, spam_participant)
```

## Write clean csv file

``` r
write.csv(skt_w4, file = "linkage_skt_w4.csv")
```
