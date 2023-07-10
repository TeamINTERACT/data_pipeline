# INTERACT Data Pipeline
The INTerventions, Equity, Research, and Action in Cities Team (INTERACT ) is a pan-Canadian collaboration of scientists, urban planners, public health practitioners, community partners, and members of the public, uncovering how the design of our cities is shaping the health and well-being of all Canadians. Since 2017, INTERACT has collected data from cohorts in 4 Canadian cities: Victoria, Vancouver, Saskatoon and Montreal. 

## Data collected
Participants provide data via these sources:  

- Participation meta-data: For each data source, participants are assigned an ID. These are tracked through the city's linkage file (one linkage file per city, eper wave)
- Surveys (Polygon): The health questionnaire features questions on INTERACT’s key health outcomes (physical activity, social connectedness, and well-being), mobility, socio-demographic data, and neighbourhood; VERITAS (Visualisation, Evaluation and Recording of Itineraries and Activity Spaces) is a map-based survey that aims to collect data to help understand the complex interactions between daily mobility, social networks, and urban environments. These questions are asked across all sites.
- SenseDoc: The SenseDoc is a research grade multisensor device used for mobility (GPS) and physical activity (accelerometer) tracking. These data are collected continuously and allow us to measure location-based physical activity and infer transportation mode.
- Ethica: Ethica is a research-grade smartphone app used for mobility and physical activity tracking. These data are collected in a 1-in-5 duty cycle (1 minute active, 4 minutes idle). It collects: 1) GPS; 2) WiFi signals; 3) Activity recognition; 4) Pedometer; 5) Battery; 6) Accelerometer data; 7) responses to surveys, called ecological momentary assessment (EMA- Questions are different from city to city). 

See Folders for each data source. 
## Pipeline
![INTERACT data flow-Page-1 drawio](https://github.com/TeamINTERACT/migrate_archive_ingest_digest/assets/48290593/1e459533-74ee-4e2c-942d-29013f293dcd)


### Steps
* **Collect**: Data is collected from participants
* **Extract**: Data is imported from original data source and moved to Compute Canada
   * BACKUP
* **Validate**: Data is verified to ensure correct format and meta data. Any data issue is flagged to the research team and fixed at this step before continuing through the pipeline. If corrections occur, data is backed up to nearline, replacing the previous back-up. 
* **Load**: Data is loaded by developer. 
* **Transform**: Data is cleaned or transformed as needed.
  * OUTPUT: Elite files (flat tables of intermediary files for expert members of team)
* **Produce**: Data is outputed as flat tables used by larger research team. For SD and Ethica, these are the Tables of Power. 
  * OUTPUT: Create csvs of Polygon surveys or ToP, for SenseDoc or Ethica
* **Describe**: Data is described with summary statitsics to help check data is as expected.

Each data source follows theses pipeline steps. Details can be found in their respective folders (**link?**)
