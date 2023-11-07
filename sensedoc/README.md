# SenseDoc Data Pipeline

1. **Collect**: Participants are given SenseDocs, hip-worn devices that store gps and acc data onto the device. They are asked to wear the devices when not sleeping, for 10 consecutive days. Devices should be charged daily. Coordinators deliver and retrieve devices.
   
2. **Extract**: Data is pulled from the individual devices by research coordinators, using an extraction tool (SenseAnalytics) provided by MobySens. This extraction includes the proprietary raw data files, and a SQLite3 DB file (and given a .sdb extension). Our migration process preserves those raw data files, but the ingest process is built against the SDB files. Coordinators name each folder with `{INTERACT_ID}_{SD_ID}`, zip the folder and place it on Compute Canada in the Incoming Data folder for their city and wave.
   
3. **Validate**: A python script (`sensedoc/ETL/validate.py`) checks list of folder names against matches in linkage file. Folder names `{INTERACT_ID}_{SD_ID}` must match a record of INTERACT_ID and SD_ID in the linkage file. In some cases, directories need to be reorganized into unique `{INTERACT_ID}_{SD_ID}` pairs with that name. Records which fail validation are flagged for follow up.

   + OUTPUT: Data is backed up to nearline

   ```
   ===== VALIDATING Montreal | Wave 1 =====
   [11/07/2023 10:48:19] ERROR: No matching sdb file found in folder <montreal/wave_01/sensedoc/401303680_50> but other sdb file(s) found:
         SD50fw2099_20181023_102943_rtc1.sdb
   [11/07/2023 10:48:19] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401627014_188>
   [11/07/2023 10:48:19] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401751741_51>
   [11/07/2023 10:48:19] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401679813_146>
   ===== VALIDATING Montreal | Wave 2 =====
   ===== VALIDATING Montreal | Wave 3 =====
   [11/07/2023 10:48:19] ERROR: Unable to find directory <montreal/wave_03/sensedoc/401952301_23>
   ===== VALIDATING Saskatoon | Wave 1 =====
   [11/07/2023 10:48:20] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302610266_367>
   [11/07/2023 10:48:20] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302923081_367>
   [11/07/2023 10:48:20] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302273130_375>
   [11/07/2023 10:48:20] ERROR: No matching sdb file found in folder <saskatoon/wave_01/sensedoc/302394560_408> but other sdb file(s) found:
         SD375fw2099_20190201_114043.sdb
   ===== VALIDATING Saskatoon | Wave 2 =====
   [11/07/2023 10:48:20] ERROR: Unable to find directory <saskatoon/wave_02/sensedoc/302955394_383>
   ===== VALIDATING Saskatoon | Wave 3 =====
   ===== VALIDATING Vancouver | Wave 1 =====
   ===== VALIDATING Vancouver | Wave 2 =====
   ===== VALIDATING Vancouver | Wave 3 =====
   [11/07/2023 10:48:20] ERROR: Unable to find directory <vancouver/wave_03/sensedoc/203064043_324>
   ===== VALIDATING Victoria | Wave 1 =====
   [11/07/2023 10:48:20] ERROR: Unable to find directory <victoria/wave_01/sensedoc/101158091_23>
   [11/07/2023 10:48:20] ERROR: Unable to find directory <victoria/wave_01/sensedoc/101891218_111>
   ===== VALIDATING Victoria | Wave 2 =====
   [11/07/2023 10:48:20] ERROR: No matching sdb file found in folder <victoria/wave_02/sensedoc/101439815_403> but other sdb file(s) found:
         SD403fw2106_20190621_152858.sdb-ignoreme
         SD403fw2106_20190621_152858_rtc1.sdb
   ===== VALIDATING Victoria | Wave 3 =====
   [11/07/2023 10:48:20] ERROR: No sdb file found in folder <victoria/wave_03/sensedoc/101435597_445>
   [11/07/2023 10:48:20] ERROR: Unable to find directory <victoria/wave_03/sensedoc/101798447_476>
   [11/07/2023 10:48:20] ERROR: Unable to find directory <victoria/wave_03/sensedoc/101847191_405>
   [11/07/2023 10:48:20] ERROR: No sdb file found in folder <victoria/wave_03/sensedoc/101888460_379>
   City      | Wave   |   Expected PIDs with SD |   Found PIDs with SD | Status
   -----------+--------+-------------------------+----------------------+------------------
   Montreal  | Wave 1 |                     163 |                  159 | Missing SD files
   Montreal  | Wave 2 |                      45 |                   45 | OK
   Montreal  | Wave 3 |                      55 |                   54 | Missing SD files
   Saskatoon | Wave 1 |                     112 |                  108 | Missing SD files
   Saskatoon | Wave 2 |                      32 |                   31 | Missing SD files
   Saskatoon | Wave 3 |                      10 |                   10 | OK
   Vancouver | Wave 1 |                     152 |                  152 | OK
   Vancouver | Wave 2 |                       0 |                    0 | OK
   Vancouver | Wave 3 |                      73 |                   72 | Missing SD files
   Victoria  | Wave 1 |                     155 |                  153 | Missing SD files
   Victoria  | Wave 2 |                     130 |                  129 | Missing SD files
   Victoria  | Wave 3 |                      89 |                   85 | Missing SD files
   ==== SECOND STEP VALIDATION ====
   The following sdb files have been found in </home/btcrchum/projects/def-dfuller/interact/data_archive> with no match in linkage files:
   1. victoria/wave_02/sensedoc/101564348_481/SD481fw2106_20191010_100530.sdb
   2. victoria/wave_02/sensedoc/101550026_416/SD416fw0000_20191022_114225.sdb
   3. victoria/wave_02/sensedoc/101201381_391/SD391fw2099_20190825_120725.sdb
   4. victoria/wave_02/sensedoc/102265934_412/SD412fw2106_20191010_093030.sdb
   5. victoria/wave_01/sensedoc/101624715_72/SD72fw2091_20170928_070350.sdb
   6. victoria/wave_01/sensedoc/101996732_147/SD147fw2090_20170926_064535.sdb
   7. victoria/wave_01/sensedoc/101202069_109/SD109fw2091_20171009_131328.sdb
   8. victoria/wave_01/sensedoc/101518271_36/SD36fw2096_20171020_090635.sdb
   9. victoria/wave_01/sensedoc/101423098_96/SD96fw2090_20171005_120106.sdb
   10. victoria/wave_01/sensedoc/101891218_123/SD123fw2096_20171115_132347.sdb
   11. victoria/wave_01/sensedoc/101165382_300/SD300fw2091_20171005_094531.sdb
   12. victoria/wave_01/sensedoc/101710208_59/SD54567fw2090_20171103_100128.sdb
   13. victoria/wave_01/sensedoc/101310422_72/SD72fw2091_20171115_135820.sdb
   14. victoria/wave_01/sensedoc/101869520_162/SD162fw2075_20171010_133531.sdb
   15. victoria/wave_01/sensedoc/101372253_36/SD36fw2096_20171101_080756.sdb
   16. victoria/wave_03/sensedoc/101798447_000/SDfw_20211101_144043.sdb
   17. victoria/wave_03/sensedoc/101888460_379/101888460_379/SDfw_20210621_100951.sdb
   18. victoria/wave_03/sensedoc/101888460_379/101888460_358/SD358fw2099_20210608_131927.sdb
   19. victoria/wave_03/sensedoc/101435597_445/101435597_374/SD374fw2110_20210531_171912.sdb
   20. victoria/wave_03/sensedoc/101435597_445/101435597_445/SDfw_20210621_103435.sdb
   21. saskatoon/wave_02/sensedoc/302515834_403/SD403fw2106_20210422_121457.sdb
   22. saskatoon/wave_02/sensedoc/303583054_492/SD492fw_20210408_114050.sdb
   23. saskatoon/wave_01/sensedoc/302411013_412/412_302411013_V2/SD412fw2106_20181107_160306.sdb
   24. saskatoon/wave_01/sensedoc/302756755_373/2/SDfw_20190418_153725.sdb
   25. saskatoon/wave_01/sensedoc/302898812_453/453_302898812_V2/SD453fw2106_20181106_175007.sdb
   26. saskatoon/wave_01/sensedoc/302531549_466/2/SDfw_20190107_155831.sdb
   27. saskatoon/wave_01/sensedoc/302328670_369/369 V2/SD369fw2099_20181128_121846.sdb
   28. saskatoon/wave_01/sensedoc/302394560_408/SD375fw2099_20190201_114043.sdb
   29. saskatoon/wave_01/sensedoc/302319371_403/SD403fw2106_20181029_125305.sdb
   30. saskatoon/wave_01/sensedoc/302394520_470/SD470fw2106_20210519_103623.sdb
   31. montreal/wave_02/sensedoc/402312216_280/investigate.sdb
   32. montreal/wave_01/sensedoc/401184984_112/SD112fw2106_20180924_164958.sdb
   33. vancouver/wave_02/sensedoc/202340607_393/SD393fw2099_20210123_103742.sdb
   34. vancouver/wave_02/sensedoc/201591592_427/SD427fw2106_20201102_151243.sdb
   35. vancouver/wave_02/sensedoc/201299366_392/SD392fw2110_20201217_143729.sdb
   36. vancouver/wave_02/sensedoc/201661659_439/SD439fw2106_20201207_120426.sdb
   37. vancouver/wave_02/sensedoc/201598406_473/SD473fw2106_20201113_133837.sdb
   38. vancouver/wave_02/sensedoc/201993762_455/SD455fw2106_20201102_165249.sdb
   39. vancouver/wave_02/sensedoc/201894756_441/SD441fw_20210401_170124.sdb
   40. vancouver/wave_02/sensedoc/201221004_495/SD495fw2106_20201224_185008.sdb
   41. vancouver/wave_02/sensedoc/202722540_404/SD404fw2106_20201218_172341.sdb
   42. vancouver/wave_02/sensedoc/201089691_356/SD356fw2099_20201204_190255.sdb
   43. vancouver/wave_02/sensedoc/201771612_415/SD415fw2106_20201123_145817.sdb
   44. vancouver/wave_02/sensedoc/201375419_374/SD374fw_20210216_120621.sdb
   45. vancouver/wave_02/sensedoc/201185322_443/SD443fw2106_20201128_125420.sdb
   46. vancouver/wave_02/sensedoc/202370401_449/SD449fw2106_20201224_150941.sdb
   47. vancouver/wave_02/sensedoc/201355341_407/SD407fw2106_20210220_114306.sdb
   48. vancouver/wave_02/sensedoc/201541156_358/SD358fw2099_20210217_125821.sdb
   49. vancouver/wave_02/sensedoc/201398316_462/SD462fw2110_20210120_151745.sdb
   50. vancouver/wave_02/sensedoc/202786503_369/SD369fw2099_20210302_153914.sdb
   51. vancouver/wave_02/sensedoc/201501554_406/SD406fw2106_20201123_142441.sdb
   52. vancouver/wave_02/sensedoc/202806934_443/SD443fw2106_20201223_173841.sdb
   53. vancouver/wave_02/sensedoc/201577173_346/SD346fw2099_20201221_151058.sdb
   54. vancouver/wave_02/sensedoc/201929826_466/SD466fw2106_20210302_151216.sdb
   55. vancouver/wave_02/sensedoc/201207268_373/SD373fw2099_20210217_133808.sdb
   56. vancouver/wave_02/sensedoc/201670130_358/SD358fw2099_20201208_184211.sdb
   57. vancouver/wave_02/sensedoc/202938759_447/SD447fw2106_20210220_113017.sdb
   58. vancouver/wave_02/sensedoc/201133626_493/SD493fw2106_20201119_162901.sdb
   59. vancouver/wave_02/sensedoc/201320546_417/SD417fw_20210216_114847.sdb
   60. vancouver/wave_02/sensedoc/201259654_369/SD369fw2099_20201201_165105.sdb
   61. vancouver/wave_02/sensedoc/201206867_366/SD366fw2110_20201222_172400.sdb
   62. vancouver/wave_02/sensedoc/202258511_427/SD427fw2106_20210109_102431.sdb
   63. vancouver/wave_02/sensedoc/201481781_493/SD493fw2106_20210116_102623.sdb
   64. vancouver/wave_02/sensedoc/201660846_357/SD357fw2099_20201218_141724.sdb
   65. vancouver/wave_02/sensedoc/201354715_495/SD495fw2106_20201206_174458.sdb
   66. vancouver/wave_02/sensedoc/202613433_443/SD443fw2106_20210223_151603.sdb
   67. vancouver/wave_02/sensedoc/201917306_476/SD476fw2106_20210223_152951.sdb
   68. vancouver/wave_02/sensedoc/202768654_313/SD313fw2099_20210210_123154.sdb
   69. vancouver/wave_02/sensedoc/201085786_373/SD373fw2099_20201130_103723.sdb
   70. vancouver/wave_02/sensedoc/201470524_379/SD379fw2099_20201027_103328.sdb
   71. vancouver/wave_02/sensedoc/202315896_366/SD366fw2110_20210220_111156.sdb
   72. vancouver/wave_02/sensedoc/202177481_363/SD363fw2106_20201123_171534.sdb
   73. vancouver/wave_02/sensedoc/201375419_444/SD444fw2106_20201124_140448.sdb
   74. vancouver/wave_02/sensedoc/202764990_357/SD357fw2099_20210129_111342.sdb
   75. vancouver/wave_02/sensedoc/202141573_473/SD473fw2106_20201223_141740.sdb
   76. vancouver/wave_02/sensedoc/201289762_406/SD406fw2106_20210206_105251.sdb
   77. vancouver/wave_02/sensedoc/201732023_363/SD363fw2106_20190924_061300.sdb
   78. vancouver/wave_02/sensedoc/201328108_405/SD405fw2106_20210116_095640.sdb
   79. vancouver/wave_02/sensedoc/201221004_415/SD415fw2106_20210123_110332.sdb
   80. vancouver/wave_02/sensedoc/201801387_482/SD482fw2110_20201223_135652.sdb
   81. vancouver/wave_02/sensedoc/202987910_459/SD459fw2106_20201217_162915.sdb
   82. vancouver/wave_02/sensedoc/201544209_420/SD420fw2106_20201119_150011.sdb
   83. vancouver/wave_02/sensedoc/201005131_405/SD405fw2106_20201125_143400.sdb
   84. vancouver/wave_02/sensedoc/201657731_447/SD447fw2106_20201123_120159.sdb
   85. vancouver/wave_02/sensedoc/201629908_406/SD406fw2106_20201222_145319.sdb
   86. vancouver/wave_02/sensedoc/201564666_486/SD486fw2106_20201224_145750.sdb
   87. vancouver/wave_02/sensedoc/201459922_392/SD392fw2110_20201129_191325.sdb
   88. vancouver/wave_02/sensedoc/201439230_486/SD486fw2106_20201125_150152.sdb
   89. vancouver/wave_02/sensedoc/202990150_494/SD494fw_20210216_133942.sdb
   90. vancouver/wave_02/sensedoc/201894756_482/SD482fw2110_20210128_103819.sdb
   91. vancouver/wave_02/sensedoc/201260516_465/SD465fw_20210401_163319.sdb
   92. vancouver/wave_02/sensedoc/202384021_445/SD445fw2106_20201203_154807.sdb
   93. vancouver/wave_02/sensedoc/202361310_476/SD476fw2106_20201223_171121.sdb
   94. vancouver/wave_02/sensedoc/201980293_473/SD473fw2106_20210223_150244.sdb
   95. vancouver/wave_02/sensedoc/201347508_393/SD393fw2099_20201204_115718.sdb
   96. vancouver/wave_02/sensedoc/202790885_459/SD459fw2106_20210217_131934.sdb
   97. vancouver/wave_02/sensedoc/201140482_375/SD375fw2110_20201001_163229.sdb
   98. vancouver/wave_02/sensedoc/201589206_486/SD486fw2106_20210210_124553.sdb
   99. vancouver/wave_02/sensedoc/201943028_466/SD466fw2106_20201119_134443.sdb
   100. vancouver/wave_02/sensedoc/202144658_420/SD420fw2106_20210302_155541.sdb
   101. vancouver/wave_02/sensedoc/201050305_415/SD415fw2106_20201222_092527.sdb
   102. vancouver/wave_02/sensedoc/201760141_465/SD465fw2106_20201223_164412.sdb
   103. vancouver/wave_02/sensedoc/201759149_441/SD441fw2106_20201204_102622.sdb
   104. vancouver/wave_02/sensedoc/201260516_439/SD439fw2106_20210206_101929.sdb
   105. vancouver/wave_02/sensedoc/201356556_379/SD379fw2099_20210123_101211.sdb
   106. vancouver/wave_02/sensedoc/201501658_465/SD465fw2106_20201123_110611.sdb
   107. vancouver/wave_02/sensedoc/202786503_346/SD346fw_20210401_153652.sdb
   108. vancouver/wave_02/sensedoc/201260516_404/SD404fw_20210401_162919.sdb
   109. vancouver/wave_02/sensedoc/201243705_373/SD373fw2099_20201223_130357.sdb
   110. vancouver/wave_02/sensedoc/202634537_407/SD407fw2106_20201222_183530.sdb
   111. vancouver/wave_02/sensedoc/202675492_392/SD392fw2110_20210206_103311.sdb
   112. vancouver/wave_02/sensedoc/201219100_482/SD482fw2110_20201120_110706.sdb
   113. vancouver/wave_02/sensedoc/201781641_491/SD491fw2106_20201129_134740.sdb
   114. vancouver/wave_02/sensedoc/201233360_358/SD358fw2099_20201224_143714.sdb
   115. vancouver/wave_02/sensedoc/201296599_409/SD409fw2106_20201105_152204.sdb
   116. vancouver/wave_02/sensedoc/201550524_366/SD366fw2110_20201120_160745.sdb
   117. vancouver/wave_02/sensedoc/201804678_488/SD488fw2106_20201130_123843.sdb
   118. vancouver/wave_02/sensedoc/201547240_313/SD313fw2099_20201009_010748.sdb
   119. vancouver/wave_02/sensedoc/202599618_367/SD367fw2099_20210120_145115.sdb
   120. vancouver/wave_02/sensedoc/201084620_475/SD475fw2106_20200930_111430.sdb
   121. vancouver/wave_02/sensedoc/201906036_367/SD367fw2099_20201203_144432.sdb
   122. vancouver/wave_02/sensedoc/201298606_426/SD426fw2106_20201102_160330.sdb
   123. vancouver/wave_03/sensedoc/201210287_349/SD349fw2110_20221011_113814.sdb
   124. vancouver/wave_03/sensedoc/203712476_451/SD451fw2106_20221001_115057.sdb
   125. vancouver/wave_03/sensedoc/201501554_312/SD312fw2099_20220716_124824.sdb
   126. vancouver/wave_03/sensedoc/202662394_401/SD401fw2110_20220910_111205.sdb
   127. vancouver/wave_03/sensedoc/202116714_403/SD403fw2106_20220903_104635.sdb
   128. vancouver/wave_03/sensedoc/203659654_324/SD324fw2099_20220903_105938.sdb
   129. vancouver/wave_03/sensedoc/201989693_319/SD319fw2099_20221105_132556.sdb
   ```
   
4. **Load**: Developer creates one csv per participant/wave/sensor, file name includes INTERACT_ID. The result is a folder per sensor, per city, each with a csv file per participant with data and INTERACT_ID

5. **Transform**: Data is cleaned to remove invalid or corrupt records. Records outside of wear date window are removed (`sd_start_1`; `sd_end_1`/ `sd_start_2`; `sd_end_2`). Since the device is always recording when on, some movement data from the coordinator delivering or retrieving the device may be collected. To filter the data properly, the participant provides wear dates. These wear dates are in the linkage file. Dates are recorded for each SenseDoc worn by a participant. It is possible that a participant missed a day or days within the wear dates. Filtering by date ensures we don’t use coordinator data recorded on the device during delivery /recovery. If there are no wear dates, all records are kept.
   Illegal coordinates, coordinates that cannot correspond to any location on earth, are removed. There are two filters : one for (0,0,0) which is a GPS error condition (technically a spot off the coast of Nigeria, but one seldom visited); one which removes points which require movement faster than 300 km/h to reach. These pop up from satellite errors.
      + OUTPUT: Data is exported as Elite (intermediary) files to Project
      + Data dictionary for **SenseDoc variables** is available here: https://teaminteract.ca/ressources/INTERACT_datadict.html#sensedoc_title 

6. **Produce**: Create Tables of Power (ToP) by a) adding columns; and b) aggregating by epoch. The variables used in the Table of Power will evolve, as the team develops new metrics, important that this code can be easily adapted to integrate more metrics. 
The following columns are added : `INTERACT_ID`, `activity_levels`, `city_id`, `in_city` (flag whether data was collected within CMA), `sumary_count`, `count_x`, `count_y`, `count_z`, `device worn`. See description in GitHub TOP readme and Data Dictionary. 
Data is aggregated by epoch: Three ToPs are created per city per wave: 1 second, 1 minute, 5 minutes.  
    + OUTPUT: 1 table of power per city, per wave per epoch (3/city/wave)
    + Data dictionary for **TOP variables for SenseDoc** is available here: https://teaminteract.ca/ressources/INTERACT_datadict.html#top_title 

7. **Describe**: Create summary statistics:
      + date ranges
      + number of days of data per participant
      + min, max, SD distributions
      + GPS locations
   

