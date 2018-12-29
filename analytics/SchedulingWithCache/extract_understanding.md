# Generaly working Rucio commands

rucio list-rse-usage MWT2_UC_LOCALGROUPDISK
4191372904 

rucio list-dataset-replicas "mc16_13TeV:mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.HITS.e7033_e5984_s3126_tid16122552_00"

rucio list-parent-dids "mc16_13TeV:mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.HITS.e7033_e5984_s3126_tid16122552_00"
+----------------------------------------------------------------------------------------------------------+--------------+
| SCOPE:NAME                                                                                               | [DID TYPE]   |
|----------------------------------------------------------------------------------------------------------+--------------|
| mc16_13TeV:mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.HITS.e7033_s3126 | CONTAINER    |
+----------------------------------------------------------------------------------------------------------+

rucio list-parent-dids mc16_13TeV:EVNT.12959107._000303.pool.root.1                                              +--------------------------------------------------------------------------------------------------------------
| SCOPE:NAME                                                                                                   | [DID TYPE]   |
|--------------------------------------------------------------------------------------------------------------
| mc16_13TeV:mc16_13TeV.364351.Sherpa_224_NNPDF30NNLO_Diphoton_myy_50_90.merge.EVNT.e6452_e5984_tid12959107_00 | DATASET      |
| panda:panda.16555277.12.24.EVNT.21976074-4b10-4e47-af5c-6de09c91f34e_dis4190454467                           | DATASET      |
| panda:panda.16555277.12.24.EVNT.31312b10-d4dd-4450-be34-0efc7b4fea61_dis4190454493                           | DATASET      |
| panda:panda.16555277.12.24.EVNT.dae88869-4cab-4d18-9d34-8989bb2475c4_dis4190454518                           | DATASET      |
+--------------------------------------------------------------------------------------------------------------



proddblock	       	
mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.merge.EVNT.e7033_e5984_tid15939621_00

jobname	       	
mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.e7033_e5984_s3126.4154464775

destinationdblock	       
mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.HITS.e7033_e5984_s3126_tid16122552_00

16122552
taskname	       	
mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.e7033_e5984_s3126



pid:4190454489

input comes from job proddblock
mc16_13TeV:mc16_13TeV.364351.Sherpa_224_NNPDF30NNLO_Diphoton_myy_50_90.merge.EVNT.e6452_e5984_tid12959107_00

* loop over tasks (status:done AND tasktype:prod)
    * get "creationdate" 
    * get all jobs of this task (taskid:16357413 AND jobstatus:finished)
        * get time they took, nfiles processed, cores

some jobs will have 0 input files but will need to be processed.



jobs: 28179
processing_type
deriv           13223
digit               3
eventIndex       2342
evgen            2274
merge            5823
overlay            75
pile             2362
recon              24
reprocessing     1430
simul             623

globaly unique datasets: 19039

unique datasets per processing_type
deriv           6607
digit              3
eventIndex      2342
evgen            186
merge           5776
overlay           75
pile            2261
recon             24
reprocessing    1405
simul            616

mean values (per task). cores and inputfiles are summs over jobs.
                      jobs cores   inputfiles
processing_type
deriv                   61   449          824
digit                  268   268          268
eventIndex              12    12          106
evgen                  349   349         2912
merge                   28    65          223
overlay                358   358          358
pile                   152  1160         1731
recon                  658  1803         1164
reprocessing           246   995         1567
simul                  219  1761          221

# understanding
* overlay datasets are using input datasets with 1 file each but these can't be listed. ?