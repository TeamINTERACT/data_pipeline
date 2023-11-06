# SenseDoc Data Pipeline

1. **Collect**: Participants are given SenseDocs, hip-worn devices that store gps and acc data onto the device. They are asked to wear the devices when not sleeping, for 10 consecutive days. Devices should be charged daily. Coordinators deliver and retrieve devices.
   
2. **Extract**: Data is pulled from the individual devices by research coordinators, using an extraction tool (SenseAnalytics) provided by MobySens. This extraction includes the proprietary raw data files, and a SQLite3 DB file (and given a .sdb extension). Our migration process preserves those raw data files, but the ingest process is built against the SDB files. Coordinators name each folder with `{INTERACT_ID}_{SD_ID}`, zip the folder and place it on Compute Canada in the Incoming Data folder for their city and wave.
   
3. **Validate**: A python script (`sensedoc/ETL/validate.py`) checks list of folder names against matches in linkage file. Folder names `{INTERACT_ID}_{SD_ID}` must match a record of INTERACT_ID and SD_ID in the linkage file. In some cases, directories need to be reorganized into unique `{INTERACT_ID}_{SD_ID}` pairs with that name. Records which fail validation are flagged for follow up.

   + OUTPUT: Data is backed up to nearline

   ```
   ===== VALIDATING Montreal | Wave 1 =====
[11/06/2023 07:36:06] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401627014_188>
[11/06/2023 07:36:06] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401751741_51>
[11/06/2023 07:36:06] ERROR: Unable to find directory <montreal/wave_01/sensedoc/401679813_146>
===== VALIDATING Montreal | Wave 2 =====
===== VALIDATING Montreal | Wave 3 =====
[11/06/2023 07:36:06] ERROR: Unable to find directory <montreal/wave_03/sensedoc/401952301_23>
===== VALIDATING Saskatoon | Wave 1 =====
[11/06/2023 07:36:06] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302610266_367>
[11/06/2023 07:36:07] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302923081_367>
[11/06/2023 07:36:07] ERROR: Unable to find directory <saskatoon/wave_01/sensedoc/302273130_375>
[11/06/2023 07:36:07] ERROR: No matching sdb file found in folder <saskatoon/wave_01/sensedoc/302394560_408> but other sdb file(s) found:
        SD375fw2099_20190201_114043.sdb
===== VALIDATING Saskatoon | Wave 2 =====
[11/06/2023 07:36:07] ERROR: Unable to find directory <saskatoon/wave_02/sensedoc/302955394_383>
===== VALIDATING Saskatoon | Wave 3 =====
===== VALIDATING Vancouver | Wave 1 =====
===== VALIDATING Vancouver | Wave 2 =====
===== VALIDATING Vancouver | Wave 3 =====
[11/06/2023 07:36:07] ERROR: Unable to find directory <vancouver/wave_03/sensedoc/203064043_324>
===== VALIDATING Victoria | Wave 1 =====
[11/06/2023 07:36:07] ERROR: Unable to find directory <victoria/wave_01/sensedoc/101158091_23>
[11/06/2023 07:36:07] ERROR: Unable to find directory <victoria/wave_01/sensedoc/101891218_111>
===== VALIDATING Victoria | Wave 2 =====
===== VALIDATING Victoria | Wave 3 =====
[11/06/2023 07:36:07] ERROR: No sdb file found in folder <victoria/wave_03/sensedoc/101435597_445>
[11/06/2023 07:36:07] ERROR: Unable to find directory <victoria/wave_03/sensedoc/101798447_476>
[11/06/2023 07:36:07] ERROR: Unable to find directory <victoria/wave_03/sensedoc/101847191_405>
[11/06/2023 07:36:07] ERROR: No sdb file found in folder <victoria/wave_03/sensedoc/101888460_379>
         City    Wave Expected PIDs with SD Found PIDs with SD            Status
0    Montreal  Wave 1                   163                160  Missing SD files
1    Montreal  Wave 2                    45                 45                OK
2    Montreal  Wave 3                    55                 54  Missing SD files
3   Saskatoon  Wave 1                   112                108  Missing SD files
4   Saskatoon  Wave 2                    32                 31  Missing SD files
5   Saskatoon  Wave 3                    10                 10                OK
6   Vancouver  Wave 1                   152                152                OK
7   Vancouver  Wave 2                     0                  0                OK
8   Vancouver  Wave 3                    73                 72  Missing SD files
9    Victoria  Wave 1                   155                153  Missing SD files
10   Victoria  Wave 2                   130                130                OK
11   Victoria  Wave 3                    89                 85  Missing SD files
==== SECOND STEP VALIDATION ====
The following sdb files have been found in </home/btcrchum/projects/def-dfuller/interact/data_archive> with no match in linkage files:
1. victoria/wave_02/sensedoc/102696608_464/SD464fw2106_20191126_112429.sdb
2. victoria/wave_02/sensedoc/102322976_401/SD401fw2106_20190825_151806.sdb
3. victoria/wave_02/sensedoc/101564348_481/SD481fw2106_20191010_100530.sdb
4. victoria/wave_02/sensedoc/101011680_484/SD484fw2106_20190802_145612.sdb
5. victoria/wave_02/sensedoc/101996732_399/SD399fw2099_20190710_170252.sdb
6. victoria/wave_02/sensedoc/102471126_399/SD399fw2099_20190902_092817.sdb
7. victoria/wave_02/sensedoc/102498628_358/SD358fw2099_20191024_142313.sdb
8. victoria/wave_02/sensedoc/101550026_416/SD416fw0000_20191022_114225.sdb
9. victoria/wave_02/sensedoc/101201381_391/SD391fw2099_20190825_120725.sdb
10. victoria/wave_02/sensedoc/102265934_412/SD412fw2106_20191010_093030.sdb
11. victoria/wave_02/sensedoc/102481129_406/SD406fw2106_20191113_143625.sdb
12. victoria/wave_02/sensedoc/102504895_379/SD379fw2099_20190704_191615.sdb
13. victoria/wave_02/sensedoc/101761435_350/SD350fw0000_20191211_150825.sdb
14. victoria/wave_02/sensedoc/101680398_391/SD391fw2099_20190630_135123.sdb
15. victoria/wave_01/sensedoc/101624715_72/SD72fw2091_20170928_070350.sdb
16. victoria/wave_01/sensedoc/101172402_36/SD36fw2090_20170805_125532.sdb
17. victoria/wave_01/sensedoc/101996732_147/SD147fw2090_20170926_064535.sdb
18. victoria/wave_01/sensedoc/101202069_109/SD109fw2091_20171009_131328.sdb
19. victoria/wave_01/sensedoc/101518271_36/SD36fw2096_20171020_090635.sdb
20. victoria/wave_01/sensedoc/101423098_96/SD96fw2090_20171005_120106.sdb
21. victoria/wave_01/sensedoc/101891218_123/SD123fw2096_20171115_132347.sdb
22. victoria/wave_01/sensedoc/101553232_188/SD188fw2096_20171016_133248.sdb
23. victoria/wave_01/sensedoc/101165382_300/SD300fw2091_20171005_094531.sdb
24. victoria/wave_01/sensedoc/101853385_51/SD51fw2090_20170708_181827.sdb
25. victoria/wave_01/sensedoc/101219235_158/SD158fw2075_20170921_205914.sdb
26. victoria/wave_01/sensedoc/101710208_59/SD54567fw2090_20171103_100128.sdb
27. victoria/wave_01/sensedoc/101710208_59/SD59fw2096_20171123_121214.sdb
28. victoria/wave_01/sensedoc/101310422_72/SD72fw2091_20171115_135820.sdb
29. victoria/wave_01/sensedoc/101869520_162/SD162fw2075_20171010_133531.sdb
30. victoria/wave_01/sensedoc/101976403_72/SD72fw2091_20170922_123843.sdb
31. victoria/wave_01/sensedoc/101372253_36/SD36fw2096_20171101_080756.sdb
32. victoria/wave_01/sensedoc/101555830_214/SD214fw2090_20170723_202303.sdb
33. victoria/wave_01/sensedoc/101002187_109/SD109fw2091_20170903_141604.sdb
34. victoria/wave_01/sensedoc/101761435_17/SD17fw2096_20171027_134412.sdb
35. victoria/wave_01/sensedoc/101446496_300/SD300fw2091_20170804_134758.sdb
36. victoria/wave_01/sensedoc/101201381_123/SD123fw2096_20171101_160639.sdb
37. victoria/wave_03/sensedoc/101798447_000/SDfw_20211101_144043.sdb
38. victoria/wave_03/sensedoc/101888460_379/101888460_379/SDfw_20210621_100951.sdb
39. victoria/wave_03/sensedoc/101888460_379/101888460_358/SD358fw2099_20210608_131927.sdb
40. victoria/wave_03/sensedoc/101285500_407/SD407fw2106_20210701_193857.sdb
41. victoria/wave_03/sensedoc/101452903_466/SD466fw_20210521_012024.sdb
42. victoria/wave_03/sensedoc/102475434_443/SD443fw2106_20210608_134301.sdb
43. victoria/wave_03/sensedoc/101435597_445/101435597_374/SD374fw2110_20210531_171912.sdb
44. victoria/wave_03/sensedoc/101435597_445/101435597_445/SDfw_20210621_103435.sdb
45. saskatoon/wave_02/sensedoc/303606448_399/SD399fw2099_20210408_095933.sdb
46. saskatoon/wave_02/sensedoc/303344149_490/SD490fw2106_20210414_151241.sdb
47. saskatoon/wave_02/sensedoc/302515834_403/SD403fw2106_20210422_121457.sdb
48. saskatoon/wave_02/sensedoc/303105656_349/SD349fw2110_20210503_141136.sdb
49. saskatoon/wave_02/sensedoc/303583054_492/SD492fw_20210408_114050.sdb
50. saskatoon/wave_02/sensedoc/303304799_481/SD481fw2106_20210407_145433.sdb
51. saskatoon/wave_01/sensedoc/302411013_412/412_302411013_V2/SD412fw2106_20181107_160306.sdb
52. saskatoon/wave_01/sensedoc/302756755_373/2/SDfw_20190418_153725.sdb
53. saskatoon/wave_01/sensedoc/302898812_453/453_302898812_V2/SD453fw2106_20181106_175007.sdb
54. saskatoon/wave_01/sensedoc/302531549_466/2/SDfw_20190107_155831.sdb
55. saskatoon/wave_01/sensedoc/302168600_459/SD459fw2106_20190107_105240.sdb
56. saskatoon/wave_01/sensedoc/302328670_369/369 V2/SD369fw2099_20181128_121846.sdb
57. saskatoon/wave_01/sensedoc/302731380_491/SD491fw2106_20190213_143800.sdb
58. saskatoon/wave_01/sensedoc/302394560_408/SD375fw2099_20190201_114043.sdb
59. saskatoon/wave_01/sensedoc/302865628_393/SD393fw2099_20190523_154018.sdb
60. saskatoon/wave_01/sensedoc/302319371_403/SD403fw2106_20181029_125305.sdb
61. saskatoon/wave_01/sensedoc/302434238_379/SD379fw2099_20181105_115958.sdb
62. saskatoon/wave_01/sensedoc/302168848_393/SD393fw2099_20181123_153931.sdb
63. saskatoon/wave_01/sensedoc/302394520_470/SD470fw2106_20210519_103623.sdb
64. montreal/wave_02/sensedoc/402312216_280/investigate.sdb
65. montreal/wave_02/sensedoc/402141286_293/SD293fw2106_20201120_145009.sdb
66. montreal/wave_02/sensedoc/401809607_49/SD49fw2106_20201120_103824.sdb
67. montreal/wave_02/sensedoc/401341482_117/SD117fw2106_20210216_094539.sdb
68. montreal/wave_02/sensedoc/401342134_241/SD241fw0000_20010101_000000.sdb
69. montreal/wave_02/sensedoc/402958700_166/SD166fw2106_20210224_164314.sdb
70. montreal/wave_02/sensedoc/402495712_36/SD36fw2106_20201120_165446.sdb
71. montreal/wave_02/sensedoc/402577721_23/SD23fw2106_20210219_150125.sdb
72. montreal/wave_02/sensedoc/401272178_60/SD60fw2106_20201120_124137.sdb
73. montreal/wave_02/sensedoc/402178963_253/SD253fw2106_20210224_110405.sdb
74. montreal/wave_02/sensedoc/401556493_204/SD204fw2106_20210428_191230.sdb
75. montreal/wave_01/sensedoc/401213122_77/SD77fw2098_20180813_120016.sdb
76. montreal/wave_01/sensedoc/401143038_253/SD253fw2099_20180921_171833.sdb
77. montreal/wave_01/sensedoc/401493283_63/SD63fw2098_20180824_094629.sdb
78. montreal/wave_01/sensedoc/401719979_49/SD49fw2098_20180911_103248.sdb
79. montreal/wave_01/sensedoc/401630460_256/SD256fw2098_20180827_151446.sdb
80. montreal/wave_01/sensedoc/401102101_60/SD60fw2106_20190121_111110.sdb
81. montreal/wave_01/sensedoc/401664309_59/SD59fw2098_20180814_110921.sdb
82. montreal/wave_01/sensedoc/401876240_121/SD121fw2106_20190107_152346.sdb
83. montreal/wave_01/sensedoc/401919451_189/SD189fw2106_20190122_143559.sdb
84. montreal/wave_01/sensedoc/401184984_112/SD112fw2106_20180924_164958.sdb
85. montreal/wave_01/sensedoc/401206271_192/SD192fw2106_20190213_132134.sdb
86. montreal/wave_01/sensedoc/401998921_77/SD77fw2098_20181217_205427.sdb
87. montreal/wave_01/sensedoc/401639662_268/SD268fw2098_20180816_145356.sdb
88. montreal/wave_01/sensedoc/401462227_169/SD169fw2099_20181108_110835.sdb
89. montreal/wave_03/sensedoc/401750427_17/SD17fw2106_20221222_110512.sdb
90. montreal/wave_03/sensedoc/402141286_50/SD50fw2106_20230127_150246.sdb
91. montreal/wave_03/sensedoc/403835859_109/SD109fw_20230518_171521.sdb
92. vancouver/wave_02/sensedoc/202340607_393/SD393fw2099_20210123_103742.sdb
93. vancouver/wave_02/sensedoc/201591592_427/SD427fw2106_20201102_151243.sdb
94. vancouver/wave_02/sensedoc/201299366_392/SD392fw2110_20201217_143729.sdb
95. vancouver/wave_02/sensedoc/201661659_439/SD439fw2106_20201207_120426.sdb
96. vancouver/wave_02/sensedoc/201598406_473/SD473fw2106_20201113_133837.sdb
97. vancouver/wave_02/sensedoc/201993762_455/SD455fw2106_20201102_165249.sdb
98. vancouver/wave_02/sensedoc/201894756_441/SD441fw_20210401_170124.sdb
99. vancouver/wave_02/sensedoc/201221004_495/SD495fw2106_20201224_185008.sdb
100. vancouver/wave_02/sensedoc/202722540_404/SD404fw2106_20201218_172341.sdb
101. vancouver/wave_02/sensedoc/201089691_356/SD356fw2099_20201204_190255.sdb
102. vancouver/wave_02/sensedoc/201771612_415/SD415fw2106_20201123_145817.sdb
103. vancouver/wave_02/sensedoc/201375419_374/SD374fw_20210216_120621.sdb
104. vancouver/wave_02/sensedoc/201185322_443/SD443fw2106_20201128_125420.sdb
105. vancouver/wave_02/sensedoc/202370401_449/SD449fw2106_20201224_150941.sdb
106. vancouver/wave_02/sensedoc/201355341_407/SD407fw2106_20210220_114306.sdb
107. vancouver/wave_02/sensedoc/201541156_358/SD358fw2099_20210217_125821.sdb
108. vancouver/wave_02/sensedoc/201398316_462/SD462fw2110_20210120_151745.sdb
109. vancouver/wave_02/sensedoc/202786503_369/SD369fw2099_20210302_153914.sdb
110. vancouver/wave_02/sensedoc/201501554_406/SD406fw2106_20201123_142441.sdb
111. vancouver/wave_02/sensedoc/202806934_443/SD443fw2106_20201223_173841.sdb
112. vancouver/wave_02/sensedoc/201577173_346/SD346fw2099_20201221_151058.sdb
113. vancouver/wave_02/sensedoc/201929826_466/SD466fw2106_20210302_151216.sdb
114. vancouver/wave_02/sensedoc/201207268_373/SD373fw2099_20210217_133808.sdb
115. vancouver/wave_02/sensedoc/201670130_358/SD358fw2099_20201208_184211.sdb
116. vancouver/wave_02/sensedoc/202938759_447/SD447fw2106_20210220_113017.sdb
117. vancouver/wave_02/sensedoc/201133626_493/SD493fw2106_20201119_162901.sdb
118. vancouver/wave_02/sensedoc/201320546_417/SD417fw_20210216_114847.sdb
119. vancouver/wave_02/sensedoc/201259654_369/SD369fw2099_20201201_165105.sdb
120. vancouver/wave_02/sensedoc/201206867_366/SD366fw2110_20201222_172400.sdb
121. vancouver/wave_02/sensedoc/202258511_427/SD427fw2106_20210109_102431.sdb
122. vancouver/wave_02/sensedoc/201481781_493/SD493fw2106_20210116_102623.sdb
123. vancouver/wave_02/sensedoc/201660846_357/SD357fw2099_20201218_141724.sdb
124. vancouver/wave_02/sensedoc/201354715_495/SD495fw2106_20201206_174458.sdb
125. vancouver/wave_02/sensedoc/202613433_443/SD443fw2106_20210223_151603.sdb
126. vancouver/wave_02/sensedoc/201917306_476/SD476fw2106_20210223_152951.sdb
127. vancouver/wave_02/sensedoc/202768654_313/SD313fw2099_20210210_123154.sdb
128. vancouver/wave_02/sensedoc/201085786_373/SD373fw2099_20201130_103723.sdb
129. vancouver/wave_02/sensedoc/201470524_379/SD379fw2099_20201027_103328.sdb
130. vancouver/wave_02/sensedoc/202315896_366/SD366fw2110_20210220_111156.sdb
131. vancouver/wave_02/sensedoc/202177481_363/SD363fw2106_20201123_171534.sdb
132. vancouver/wave_02/sensedoc/201375419_444/SD444fw2106_20201124_140448.sdb
133. vancouver/wave_02/sensedoc/202764990_357/SD357fw2099_20210129_111342.sdb
134. vancouver/wave_02/sensedoc/202141573_473/SD473fw2106_20201223_141740.sdb
135. vancouver/wave_02/sensedoc/201289762_406/SD406fw2106_20210206_105251.sdb
136. vancouver/wave_02/sensedoc/201732023_363/SD363fw2106_20190924_061300.sdb
137. vancouver/wave_02/sensedoc/201328108_405/SD405fw2106_20210116_095640.sdb
138. vancouver/wave_02/sensedoc/201221004_415/SD415fw2106_20210123_110332.sdb
139. vancouver/wave_02/sensedoc/201801387_482/SD482fw2110_20201223_135652.sdb
140. vancouver/wave_02/sensedoc/202987910_459/SD459fw2106_20201217_162915.sdb
141. vancouver/wave_02/sensedoc/201544209_420/SD420fw2106_20201119_150011.sdb
142. vancouver/wave_02/sensedoc/201005131_405/SD405fw2106_20201125_143400.sdb
143. vancouver/wave_02/sensedoc/201657731_447/SD447fw2106_20201123_120159.sdb
144. vancouver/wave_02/sensedoc/201629908_406/SD406fw2106_20201222_145319.sdb
145. vancouver/wave_02/sensedoc/201564666_486/SD486fw2106_20201224_145750.sdb
146. vancouver/wave_02/sensedoc/201459922_392/SD392fw2110_20201129_191325.sdb
147. vancouver/wave_02/sensedoc/201439230_486/SD486fw2106_20201125_150152.sdb
148. vancouver/wave_02/sensedoc/202990150_494/SD494fw_20210216_133942.sdb
149. vancouver/wave_02/sensedoc/201894756_482/SD482fw2110_20210128_103819.sdb
150. vancouver/wave_02/sensedoc/201260516_465/SD465fw_20210401_163319.sdb
151. vancouver/wave_02/sensedoc/202384021_445/SD445fw2106_20201203_154807.sdb
152. vancouver/wave_02/sensedoc/202361310_476/SD476fw2106_20201223_171121.sdb
153. vancouver/wave_02/sensedoc/201980293_473/SD473fw2106_20210223_150244.sdb
154. vancouver/wave_02/sensedoc/201347508_393/SD393fw2099_20201204_115718.sdb
155. vancouver/wave_02/sensedoc/202790885_459/SD459fw2106_20210217_131934.sdb
156. vancouver/wave_02/sensedoc/201140482_375/SD375fw2110_20201001_163229.sdb
157. vancouver/wave_02/sensedoc/201589206_486/SD486fw2106_20210210_124553.sdb
158. vancouver/wave_02/sensedoc/201943028_466/SD466fw2106_20201119_134443.sdb
159. vancouver/wave_02/sensedoc/202144658_420/SD420fw2106_20210302_155541.sdb
160. vancouver/wave_02/sensedoc/201050305_415/SD415fw2106_20201222_092527.sdb
161. vancouver/wave_02/sensedoc/201760141_465/SD465fw2106_20201223_164412.sdb
162. vancouver/wave_02/sensedoc/201759149_441/SD441fw2106_20201204_102622.sdb
163. vancouver/wave_02/sensedoc/201260516_439/SD439fw2106_20210206_101929.sdb
164. vancouver/wave_02/sensedoc/201356556_379/SD379fw2099_20210123_101211.sdb
165. vancouver/wave_02/sensedoc/201501658_465/SD465fw2106_20201123_110611.sdb
166. vancouver/wave_02/sensedoc/202786503_346/SD346fw_20210401_153652.sdb
167. vancouver/wave_02/sensedoc/201260516_404/SD404fw_20210401_162919.sdb
168. vancouver/wave_02/sensedoc/201243705_373/SD373fw2099_20201223_130357.sdb
169. vancouver/wave_02/sensedoc/202634537_407/SD407fw2106_20201222_183530.sdb
170. vancouver/wave_02/sensedoc/202675492_392/SD392fw2110_20210206_103311.sdb
171. vancouver/wave_02/sensedoc/201219100_482/SD482fw2110_20201120_110706.sdb
172. vancouver/wave_02/sensedoc/201781641_491/SD491fw2106_20201129_134740.sdb
173. vancouver/wave_02/sensedoc/201233360_358/SD358fw2099_20201224_143714.sdb
174. vancouver/wave_02/sensedoc/201296599_409/SD409fw2106_20201105_152204.sdb
175. vancouver/wave_02/sensedoc/201550524_366/SD366fw2110_20201120_160745.sdb
176. vancouver/wave_02/sensedoc/201804678_488/SD488fw2106_20201130_123843.sdb
177. vancouver/wave_02/sensedoc/201547240_313/SD313fw2099_20201009_010748.sdb
178. vancouver/wave_02/sensedoc/202599618_367/SD367fw2099_20210120_145115.sdb
179. vancouver/wave_02/sensedoc/201084620_475/SD475fw2106_20200930_111430.sdb
180. vancouver/wave_02/sensedoc/201906036_367/SD367fw2099_20201203_144432.sdb
181. vancouver/wave_02/sensedoc/201298606_426/SD426fw2106_20201102_160330.sdb
182. vancouver/wave_01/sensedoc/201440082_420/SD420fw2106_20180914_153235.sdb
183. vancouver/wave_01/sensedoc/201784517_490/SD490fw2106_20180607_100245.sdb
184. vancouver/wave_01/sensedoc/201595427_495/SD495fw2106_20180928_140105.sdb
185. vancouver/wave_01/sensedoc/201585258_445/SD445fw2106_20180918_093610.sdb
186. vancouver/wave_01/sensedoc/201943028_486/SD486fw2106_20181109_103850.sdb
187. vancouver/wave_01/sensedoc/201822987_441/SD441fw2106_20181012_170306.sdb
188. vancouver/wave_01/sensedoc/201177837_465/SD465fw2106_20180919_102744.sdb
189. vancouver/wave_01/sensedoc/201210287_478/SD478fw2106_20190124_114811.sdb
190. vancouver/wave_01/sensedoc/201591592_492/SD492fw2106_20180515_141702.sdb
191. vancouver/wave_01/sensedoc/201890309_474/SD474fw2106_20181026_101133.sdb
192. vancouver/wave_03/sensedoc/203410011_423/SD423fw2106_20220924_122836.sdb
193. vancouver/wave_03/sensedoc/201760141_428/SD428fw2106_20220806_114415.sdb
194. vancouver/wave_03/sensedoc/201808807_484/SD484fw2110_20220903_100455.sdb
195. vancouver/wave_03/sensedoc/201210287_349/SD349fw2110_20221011_113814.sdb
196. vancouver/wave_03/sensedoc/202258511_349/SD349fw2110_20220709_122719.sdb
197. vancouver/wave_03/sensedoc/203712476_451/SD451fw2106_20221001_115057.sdb
198. vancouver/wave_03/sensedoc/201047893_319/SD319fw2099_20220827_113512.sdb
199. vancouver/wave_03/sensedoc/201185322_484/SD484fw2110_20220709_110034.sdb
200. vancouver/wave_03/sensedoc/201501554_312/SD312fw2099_20220716_124824.sdb
201. vancouver/wave_03/sensedoc/201298606_328/SD328fw2099_20220808_204519.sdb
202. vancouver/wave_03/sensedoc/202662394_401/SD401fw2110_20220910_111205.sdb
203. vancouver/wave_03/sensedoc/201084620_399/SD399fw2099_20221022_103851.sdb
204. vancouver/wave_03/sensedoc/203549113_434/SD434fw2106_20221105_124918.sdb
205. vancouver/wave_03/sensedoc/202116714_403/SD403fw2106_20220903_104635.sdb
206. vancouver/wave_03/sensedoc/203659654_324/SD324fw2099_20220903_105938.sdb
207. vancouver/wave_03/sensedoc/203842375_451/SD451fw2106_20220808_202543.sdb
208. vancouver/wave_03/sensedoc/201989693_319/SD319fw2099_20221105_132556.sdb
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
   

