/************************
ADDING METs TO WAVE 4 DATA

Ref: CROUTER, SCOTT E.1; KUFFEL, ERIN2; HAAS, JERE D.3; FRONGILLO, EDWARD A.4; BASSETT, DAVID R. JR.5. 
Refined Two-Regression Model for the ActiGraph Accelerometer. 
Medicine & Science in Sports & Exercise 42(5):p 1029-1037, 
May 2010. | DOI: 10.1249/MSS.0b013e3181c37458

http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2891855/
************************/

-- mtl
alter table top_sd4.top_1min_mtl
	add column if not exists met real;

with foo as (
	select interact_id
		,date_bin('10 seconds', utcdate, timestamp '2017-01-01') bin10s
		,count_x
	from top_sd4.top_1sec_mtl
),
bar as (
	select interact_id, bin10s
		,sum(count_x) count_x10
		,100 * stddev(count_x) / avg(nullif(count_x, 0)) cv
	from foo
	group by interact_id, bin10s
),
baz as (
	select interact_id, bin10s, count_x10
		,case
			when count_x10 <= 8 then 1
			when count_x10 > 8 and cv <= 10 then 2.294275 * (exp(0.00084679 * count_x10))
			when count_x10 > 8 and cv > 10 then 0.749395 + (0.716431 * (Ln(count_x10))) - (0.179874 * (Ln(count_x10))^2) + (0.033173 * (Ln(count_x10))^3)
		end met10
	from bar
),
qux AS (
	select interact_id, date_trunc('minute', bin10s) utcdate
		,avg(met10) met
	from baz
	group by baz.interact_id, date_trunc('minute', bin10s)
)
update top_sd4.top_1min_mtl top
	set met = qux.met
from qux
where top.interact_id = qux.interact_id and top.utcdate = qux.utcdate;

-- vic
alter table top_sd4.top_1min_vic
	add column if not exists met real;

with foo as (
	select interact_id
		,date_bin('10 seconds', utcdate, timestamp '2017-01-01') bin10s
		,count_x
	from top_sd4.top_1sec_vic
),
bar as (
	select interact_id, bin10s
		,sum(count_x) count_x10
		,100 * stddev(count_x) / avg(nullif(count_x, 0)) cv
	from foo
	group by interact_id, bin10s
),
baz as (
	select interact_id, bin10s, count_x10
		,case
			when count_x10 <= 8 then 1
			when count_x10 > 8 and cv <= 10 then 2.294275 * (exp(0.00084679 * count_x10))
			when count_x10 > 8 and cv > 10 then 0.749395 + (0.716431 * (Ln(count_x10))) - (0.179874 * (Ln(count_x10))^2) + (0.033173 * (Ln(count_x10))^3)
		end met10
	from bar
),
qux AS (
	select interact_id, date_trunc('minute', bin10s) utcdate
		,avg(met10) met
	from baz
	group by baz.interact_id, date_trunc('minute', bin10s)
)
update top_sd4.top_1min_vic top
	set met = qux.met
from qux
where top.interact_id = qux.interact_id and top.utcdate = qux.utcdate;

