/* Participant 102402181 has been wrongly identified as 102482181 
in the Ethica and Sd linkage file and need to be reidentified */

begin;

-- Merging 102402181 & 102482181 into linkage file linkage.vic_w2
update linkage.vic_w2 lnk
    set ethica_id = bad.ethica_id,
        sd_id_1 = bad.sd_id_1,
        sd_firmware_1 = bad.sd_firmware_1,
        sd_start_1 = bad.sd_start_1,
        sd_end_1 = bad.sd_end_1
    from (select * from linkage.vic_w2 where interact_id = '102482181') bad
    where lnk.interact_id = '102402181';

delete from linkage.vic_w2 where interact_id = '102482181';

-- Fixing Ethica EMA
update ema2.vic
    set interact_id = 102402181
    where interact_id = 102482181;

-- Fixing SD tops
update top_sd2.top_1min_vic
    set interact_id = 102402181
    where interact_id = 102482181;

update top_sd2.top_1sec_vic
    set interact_id = 102402181
    where interact_id = 102482181;

commit;