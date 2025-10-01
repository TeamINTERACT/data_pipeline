Wave 4 Victoria Linkage
================
Zoé Poirier Stephens

# Victoria Wave 4 Linkage Files

### Read in Data

Reading in the data.

- `plg_participants-20241219.csv` : a download of the participant csv
  from the PLG dashboard on Dec 19th
- `avicenna_study-3729-export-3-participation-2024-12-16-15-01-34.csv` :
  a download of the participant csv from the Avicenna dashboard on Dec
  16th
- `INT-VIC-SD-Participant-Tracking-W4-VIC.csv` : the sensedoc tracking
  document.

``` r
#setwd("/Users/dlf545/Documents/ForDan_Linkages_072023")
setwd("I:/Benoit/OneDrive - Universite de Montreal/Documents/PROJETS/INTERACT_2016/Donnees/Wave4/Victoria_linkages_w4")

w4_plg <- read_delim("plg_participants-20241219.csv", delim = ",", name_repair = "universal")
```

    ## New names:
    ## Rows: 1051 Columns: 49
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (15): id, identifier, first.name, last.name, study.id, status, preferre... dbl
    ## (15): total.sessions.count, started.sessions.count, completed.sessions.... num
    ## (1): profile.ethnicity lgl (2): profile.gentri, profile.hear.txt dttm (5):
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
w4_eth <- read_delim("avicenna_study-3729-export-3-participation-2024-12-16-15-01-34.csv", delim = ",", name_repair = "universal")
```

    ## New names:
    ## Rows: 87 Columns: 14
    ## ── Column specification
    ## ──────────────────────────────────────────────────────── Delimiter: "," chr
    ## (7): Last.Recorded.Data.Time, Participant.Type, First.Name, Last.Name, ... dbl
    ## (3): ID, Status, In.Operation lgl (2): Participant.Joined.Date, Label dttm (2):
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
w4_sd <- read_delim("INT-VIC-SD-Participant-Tracking-W4-VIC.csv", delim = ";", name_repair = "universal") ### need this file
```

    ## Rows: 124 Columns: 9
    ## ── Column specification ────────────────────────────────────────────────────────
    ## Delimiter: ";"
    ## chr (4): sd_start_1, sd_end_1, sd_start_2, sd_end_2
    ## dbl (5): interact_id, sd_id_1, sd_firmware_1, sd_id_2, sd_firmware_2
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




## Manually changing an email on Avicenna/ Ethica: One participant had a different email used on Avicenna than PLG. I'm putting the plg one here to make the ##link.
#101435597  plg email: andersonk@camosun.bc.ca  avicenna email: andersonk@camosun.ca 

w4_eth$email[w4_eth$email == "andersonk@camosun.ca"] <- "andersonk@camosun.bc.ca"


## join PLG with Ethica 

w4_plg <- full_join(w4_plg, w4_eth, by= "email") 

## join SD to PLG+Ethica

w4_sd$interact_id <- as.character(w4_sd$interact_id)

vic_w4 <- full_join(w4_plg, w4_sd, by= "interact_id")
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

vic_w4 <- vic_w4 %>%
  mutate(test = ifelse(ethica_id %in% ethica_tests, 1, 0)) 

#remove zoe's test
vic_w4$test[vic_w4$interact_id== "104000942"] <- 1  

vic_w4$test[vic_w4$ethica_id == 27847] <- 1  
```

### Flag spam accounts

On 23 July 2024, we identified 27 participant accounts suspected of
being frequently created to capitalize on the refer-a-friend \$10
incentive bonus. These accounts were contacted by email (Notice of
Unusual Activity Detected in Study Participation) and deactivated
(‘Désactivé’ in PLG platform). We will exclude these from the final
datasets. They are flagged in the linkage table.

``` r
## list of spam
fake<- c(104030009, 104543458, 104032188, 104047801,    104049993,  104050642, 104050030,   104050133,  104051112, 104051095,   104052211,  104052337, 104052557,   104052626,  104053609, 104052770,   104054492,  104054668, 104056687,   104061358,  104058872, 104062632,   104683291,  104046054, 104049914, 104051789,    104056594
)


##flag fake participants from vic_w4

vic_w4 <- vic_w4 %>%
  mutate(spam_participant = ifelse(interact_id %in% fake, 1, 0)) 
```

### Fix unmatched ethica users

``` r
vic_w4 <- vic_w4 |>
  filter(!(ethica_id %in% c(101033)))
  
vic_w4[vic_w4$interact_id == "101435597" & !is.na(vic_w4$interact_id),"ethica_id"] <- 101033
```

### Adding columns

``` r
vic_w4$treksoft_pid <- NA
vic_w4$treksoft_uid <- NA
vic_w4$data_disposition <- NA

vic_w4$wave <- 4

vic_w4$treksoft_pid <- as.numeric(vic_w4$treksoft_pid)
vic_w4$treksoft_uid <- as.numeric(vic_w4$treksoft_uid)
```

### Selecting variables

``` r
vic_w4 <- select(vic_w4, interact_id, treksoft_pid, treksoft_uid, ethica_id, sd_id_1, sd_firmware_1, sd_start_1, sd_end_1, sd_id_2, sd_firmware_2, sd_start_2, sd_end_2, data_disposition, plg_id, dropout, wave, test, spam_participant)
```

### Write clean file

``` r
write.csv(vic_w4, file= "linkage_vic_w4.csv")
```
