Wave 4 Montreal Linkage
================
Zoé Poirier Stephens

# Montreal Wave 4 Linkage Files

### Read in Data

Reading in the data. These are data are relatively different from Wave 1
and 2 as we have a separate file for each of the Polygon, Ethica, and
Sensedoc data sources. We are also moving to our naming convention of
extract, validate, etc for this document. Here we are reading in three
files

- `plg_participants-20250117.csv` which is our main Polygon file
- `study-3729-export-3-participation-2025-01-17-19-32-42.csv` which is
  our main Ethica file
- `SD_tracking.csv` which is our main Sensedoc file \## FILE IS NOT
  FINAL! See Marianne in January for final table.

``` r
setwd("I:/Benoit/OneDrive - Universite de Montreal/Documents/PROJETS/INTERACT_2016/Donnees/Wave4/Montreal_linkages_w4")

w4_plg <- read_delim("plg_participants-20250117.csv", delim = ",", name_repair = "universal")
```

    ## New names:
    ## Rows: 3887 Columns: 49
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (15): id, identifier, first.name, last.name, status, preferred.locale, ... dbl
    ## (15): study.id, total.sessions.count, started.sessions.count, completed... num
    ## (1): profile.ethnicity lgl (2): profile.hear.txt, profile.sd.interest dttm (5):
    ## created.at, registered.at, verified.at, first.session.activity.at... date (11):
    ## profile.v.1.e, profile.v.1.h, profile.v.1.v, profile.v.2.e, profi...
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

``` r
w4_eth <- read_delim("study-3729-export-3-participation-2025-01-17-19-32-42.csv", delim = ",", name_repair = "universal")
```

    ## New names:
    ## Rows: 197 Columns: 14
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (7): Last.Recorded.Data.Time, Participant.Type, First.Name, Last.Name, ... dbl
    ## (3): ID, Status, In.Operation lgl (1): Label dttm (3): Participant.Joined.Date,
    ## Start.Time, End.Time
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

``` r
w4_sd <- read_delim("SD_tracking_not_final2025-02-03.csv", delim = ";", name_repair = "universal")
```

    ## Rows: 49 Columns: 9
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## chr (2): sd_start_1, sd_end_1
    ## dbl (3): interact_id, sd_id_1, sd_firmware_1
    ## lgl (4): sd_id_2, sd_firmware_2, sd_start_2, sd_end_2
    ## 
    ## ℹ Use `spec()` to retrieve the full column specification for this data.
    ## ℹ Specify the column types or set `show_col_types = FALSE` to quiet this message.

### Validate

Only keep ids of people who have done eligibility

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
w4_plg$interact_id <- as.character(w4_plg$interact_id)

w4_plg <- full_join(w4_plg, w4_eth, by= "email") 

## join SD to PLG+Ethica

w4_sd$interact_id <- as.character(w4_sd$interact_id)

mtl_w4 <- full_join(w4_plg, w4_sd, by= "interact_id")
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
mtl_w4 <- mtl_w4 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0))
```

## add 1 if test accounts

``` r
mtl_w4$test[mtl_w4$email == "testlaval@teaminteract.ca"] <- 1
```

### Flag spam accounts

We identified participant accounts suspected of being frequently created
to capitalize on the refer-a-friend \$10 incentive bonus. These accounts
were contacted by email (Notice of Unusual Activity Detected in Study
Participation). We will exclude these from the final datasets. They are
flagged in the linkage table.

``` r
## list of spam
fake<- c(404771341, 404519221, 404798627, 404528736, 404558141, 404413088, 404914946)


##flag fake participants from mtl_w4

mtl_w4 <- mtl_w4 %>%
  mutate(spam_participant = ifelse(interact_id %in% fake, 1, 0)) 
```

### Fix unmatched ethica users

``` r
mtl_w4 <- mtl_w4 |>
  filter(!(ethica_id %in% c(5733, 34388)))
  
mtl_w4[mtl_w4$interact_id == "401545947" & !is.na(mtl_w4$interact_id),"ethica_id"] <- 5733
mtl_w4[mtl_w4$interact_id == "401910133" & !is.na(mtl_w4$interact_id),"ethica_id"] <- 34388
```

### Clean orphan participants

Participant `402781880` collected Sd data but did not complete any
survey -\> discard

``` r
mtl_w4 <- mtl_w4 |>
  filter(!(interact_id %in% c("402781880")))
```

### Adding columns

Here we add the columns to have consistent columns across linkage files.

``` r
mtl_w4$data_disposition <- NA
mtl_w4$treksoft_pid <- NA
mtl_w4$treksoft_uid <- NA
mtl_w4$wave <- 4
```

### Selecting variables

``` r
mtl_w4 <- select(mtl_w4, interact_id, treksoft_pid, treksoft_uid, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, data_disposition, plg_id, dropout, wave, test, spam_participant)
```

## Write clean csv file

``` r
write.csv(mtl_w4, file = "linkage_mtl_w4.csv")
```
