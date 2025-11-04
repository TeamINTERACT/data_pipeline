-- mtl 1 min
alter table top_sd4.top_1min_mtl
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd4.top_1min_mtl
	set in_cma = true
from (select geom from aoi.cma where city_id = 'mtl') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd4.top_1min_mtl
	set in_city = true
from (select geom from aoi.study_area where city_id = 'mtl') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- mtl 1 sec
alter table top_sd4.top_1sec_mtl
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd4.top_1sec_mtl
	set in_cma = true
from (select geom from aoi.cma where city_id = 'mtl') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd4.top_1sec_mtl
	set in_city = true
from (select geom from aoi.study_area where city_id = 'mtl') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- vic 1 min
alter table top_sd4.top_1min_vic
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd4.top_1min_vic
	set in_cma = true
from (select geom from aoi.cma where city_id = 'vic') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd4.top_1min_vic
	set in_city = true
from (select geom from aoi.study_area where city_id = 'vic') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- vic 1 sec
alter table top_sd4.top_1sec_vic
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd4.top_1sec_vic
	set in_cma = true
from (select geom from aoi.cma where city_id = 'vic') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd4.top_1sec_vic
	set in_city = true
from (select geom from aoi.study_area where city_id = 'vic') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

