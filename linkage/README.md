# Linkages

Linkage files are critical files that contain all of the participant information to link the data across the different methods of data collection and waves of data. The code for these files is bespoke and not automated because there are often changes to the data collection process. As well, project coordinators responsible for the data collection create these files semi-manually during data collection. 

Linkage files are in the specific folders or find links to them here

| City | Wave | .Rmd file | Rendered .md file |
| ---- | ---- | ---------:| -----------------:|
| Montreal | 1 | [Click here](Montreal\wave1_montreal_linkage.Rmd) | [Click here](Montreal/wave1_montreal_linkage.md) |
| Montreal | 2 | [Click here](Montreal/wave2_montreal_linkage.Rmd) | [Click here](Montreal/wave2_montreal_linkage.md) |
| Montreal | 3 | [Click here](Montreal/wave3_montreal_linkage.Rmd) | [Click here](Montreal/wave3_montreal_linkage.md) |
| Saskatoon | 1 | [Click here](Saskatoon/wave1_saskatoon_linkage.Rmd) | [Click here](Saskatoon/wave1_saskatoon_linkage.md) |
| Saskatoon | 2 | [Click here](Saskatoon/wave2_saskatoon_linkage.Rmd) | [Click here](Saskatoon/wave2_saskatoon_linkage.md) |
| Saskatoon | 3 | [Click here](Saskatoon/wave3_saskatoon_linkage.Rmd) | [Click here](Saskatoon/wave3_saskatoon_linkage.md) |
| Vancouver | 1 | [Click here](Vancouver/wave1_vancouver_linkage.Rmd) | [Click here](Vancouver/wave1_vancouver_linkage.md) |
| Vancouver | 2 | [Click here](Vancouver/wave2_vancouver_linkage.Rmd) | [Click here](Vancouver/wave2_vancouver_linkage.md) |
| Vancouver | 3 | [Click here](Vancouver/wave3_vancouver_linkage.Rmd) | [Click here](Vancouver/wave3_vancouver_linkage.md) |
| Victoria | 1 | [Click here](Victoria/wave1_victoria_linkage.Rmd) | [Click here](Victoria/wave1_victoria_linkage.md) |
| Victoria | 2 | [Click here](Victoria/wave2_victoria_linkage.Rmd) | [Click here](Victoria/wave2_victoria_linkage.md) |
| Victoria | 3 | [Click here](Victoria/wave3_victoria_linkage.Rmd) | [Click here](Victoria/wave3_victoria_linkage.md) |

The final check for the linkage files are [here](Linkage-Check.md). This file checks the variable names and types and ensures that the data for each wave can be bound together and all of the cities and waves can be bound together.

## Variables

Linkage files contain the same fields across all waves and sites. 

`interact_id` : 9-digit integer, broken down as follows, from left to right:
1-digit to signify the city in which the user first participated 01 = Victoria, BC; 02 = Vancouver, BC; 03 = Saskatoon, SK; 04 = Montreal, QC)
2-digits to signify the wave number in which the user first participated.
6-digits randomly assigned

`treksoft_uid`: The non-unique ID assigned by Treksoft to a user. Used only in w1.

`treksoft_pid`: The non-unique ID assigned by Treksoft to a participant. Used only in w1.

`plg_id`: The unique ID assigned by Polygon who host the Health and VERITAS surveys. Only used in w3. 

`ethica_id`: Ethica participant ID, as assigned by Ethica. The ethica_id is linked to an email address, meaning a participant keeps the same ethica_id through different waves as long as they are using the same email. 

`ethica_start`: Date and time of the start of data collection using Ethica, when available. Included for information here, it does not appear in all linkage files. Most reliable information for this will be to look at dates for which we have data. 

`ethica_end`: Date and time of expected end of data collection using Ethica. A participant may have ended their participation sooner, by dropping out, deleting the app, or not activating the app. Included for information here, it does not appear in all linkage files.

`sd_id_1`: The serial number of the SenseDoc device used. 1 indicates the first device used. In rare occasions, participants wore 2 devices if the first malfunctioned. In that case, there will be entries into _2 fields.

`sd_firmware_1`: Firmware for device 1

`sd_start_1`: Date of first day of SenseDoc use. Only the days between start and end inclusively should be included in datasets, since data outside of this time period could be coordinator data collected when delivering devices. If there are no dates available, include all data available. 

`sd_end_1`: Date of last full day of Sensedoc use. Participants are asked to wear the device for 10 days, though some stray from this request. There should generally be 10 days of data, but more or fewer days is possible. If there are no dates available, include all data available. 

`sd_id_2`: The id of the SenseDoc used. 2 indicates the second device used by the participant. In rare occasions, participants wore 2 devices if the first malfunctioned.

`sd_firmware_2`: Firmware for device 2

`sd_start_2`: Start wear date of device 2. See sd_start_1 for details.

`sd_end_2`: End wear date of device 2. See sd_end_1 for details.

`data_disposition`: Notes on data disposition when available from past programmer (Jeff Smith). Keeping for record of past approaches. Validation at the linkage file production stage, and other columns like test and dropout replace the need for this field. 

`test`: Rows with a 1 value indicate this is test data by a staff member and should not be included in datasets

`spam`: Rows with a 1 value indicate this is a spam participant and should not be included in datasets. This applies to Saskatoon wave 3, where invalid responses were entered by spam participants to access giftcards. 

`dropout`: Rows with a 1 value indicate the participant dropped out. **We CAN use their data**, but should not follow up with them in subsequent waves.
