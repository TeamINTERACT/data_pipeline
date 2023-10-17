# Health and VERITAS questionnaire

1. **Collect**: Participants contribute data through online surveys, participation is managed by coordinators.
   
2. **Extract**: Read data from Polygon database. 
   
3. **Validate**: Remove test accounts, based on linkage file notes  
   
4. **Load**: Store data in database on Digital Research Alliance of Canada (DRAC).  

5. **Transform**: Production of the closest csv table from what we collected (create data dict, harmonize response options)

6. **Produce**: Flat CSV tables for health and VERITAS per wave, per city, where each row is a participant identified by INTERACT_ID. This also includes the Essence table, a table of key values, harmonized across cities and waves.
     + Output: csv tables for health and veritas surveys; updated essence table 
     + Data dictionary for **Health variables** is available here: https://teaminteract.ca/ressources/INTERACT_datadict.html#health_questionnaire_title
     + Data dictionary for **VERITAS variables** is available here:https://teaminteract.ca/ressources/INTERACT_datadict.html#veritas_questionnaire_title 
     + Data dictionary for **Essence variables** is available here: https://teaminteract.ca/ressources/INTERACT_datadict.html#essence_title 

7. **Describe**: Data dictionary has distribution of responses integrated for each variable 


Full processing steps are documented in the two following repos:
 - https://github.com/TeamINTERACT/treksoft_import 
 - https://github.com/TeamINTERACT/essence_table

