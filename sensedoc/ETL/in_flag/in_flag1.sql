/*-- mtl 1 min
alter table top_sd.top_1min_mtl
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd.top_1min_mtl
	set in_cma = true
from (select geom from aoi.cma where city_id = 'mtl') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd.top_1min_mtl
	set in_city = true
from (select geom from aoi.study_area where city_id = 'mtl') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- mtl 1 sec
alter table top_sd.top_1sec_mtl
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd.top_1sec_mtl
	set in_cma = true
from (select geom from aoi.cma where city_id = 'mtl') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd.top_1sec_mtl
	set in_city = true
from (select geom from aoi.study_area where city_id = 'mtl') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- skt 1 min
alter table top_sd.top_1min_skt
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd.top_1min_skt
	set in_cma = true
from (select geom from aoi.cma where city_id = 'skt') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd.top_1min_skt
	set in_city = true
from (select geom from aoi.study_area where city_id = 'skt') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- skt 1 sec
alter table top_sd.top_1sec_skt
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd.top_1sec_skt
	set in_cma = true
from (select geom from aoi.cma where city_id = 'skt') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd.top_1sec_skt
	set in_city = true
from (select geom from aoi.study_area where city_id = 'skt') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- van 1 min
alter table top_sd.top_1min_van
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd.top_1min_van
	set in_cma = true
from (select geom from aoi.cma where city_id = 'van') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd.top_1min_van
	set in_city = true
from (select geom from aoi.study_area where city_id = 'van') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- van 1 sec
alter table top_sd.top_1sec_van
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd.top_1sec_van
	set in_cma = true
from (select geom from aoi.cma where city_id = 'van') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd.top_1sec_van
	set in_city = true
from (select geom from aoi.study_area where city_id = 'van') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- vic 1 min
alter table top_sd.top_1min_vic
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd.top_1min_vic
	set in_cma = true
from (select geom from aoi.cma where city_id = 'vic') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

update top_sd.top_1min_vic
	set in_city = true
from (select geom from aoi.study_area where city_id = 'vic') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

-- vic 1 sec
alter table top_sd.top_1sec_vic
	add column IF NOT EXISTS in_city bool default false,
	add column IF NOT EXISTS in_cma bool default false; 

update top_sd.top_1sec_vic
	set in_cma = true
from (select geom from aoi.cma where city_id = 'vic') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);
*/
update top_sd.top_1sec_vic
	set in_city = true
from (select geom from aoi.study_area where city_id = 'vic') foo 
where st_intersects(st_setsrid(st_makepoint(lon, lat), 4326), geom);

