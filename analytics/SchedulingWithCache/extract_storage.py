rucio list-rse-usage MWT2_UC_LOCALGROUPDISK
4191372904 

proddblock	       	
mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.merge.EVNT.e7033_e5984_tid15939621_00

jobname	       	
mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.e7033_e5984_s3126.4154464775

destinationdblock	       
mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.HITS.e7033_e5984_s3126_tid16122552_00

16122552
taskname	       	
mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.e7033_e5984_s3126

rucio list-dataset-replicas "mc16_13TeV:mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.HITS.e7033_e5984_s3126_tid16122552_00"

rucio list-parent-dids "mc16_13TeV:mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.HITS.e7033_e5984_s3126_tid16122552_00"     12:27
+----------------------------------------------------------------------------------------------------------+--------------+
| SCOPE:NAME                                                                                               | [DID TYPE]   |
|----------------------------------------------------------------------------------------------------------+--------------|
| mc16_13TeV:mc16_13TeV.366029.Sh_221_NN30NNLO_Znunu_PTV100_140_MJJ0_500_CVetoBVeto.simul.HITS.e7033_s3126 | CONTAINER    |
+----------------------------------------------------------------------------------------------------------+--------------+


pid:4190454489
rucio list-parent-dids mc16_13TeV:EVNT.12959107._000303.pool.root.1                                                                                        12:58
+--------------------------------------------------------------------------------------------------------------+--------------+
| SCOPE:NAME                                                                                                   | [DID TYPE]   |
|--------------------------------------------------------------------------------------------------------------+--------------|
| mc16_13TeV:mc16_13TeV.364351.Sherpa_224_NNPDF30NNLO_Diphoton_myy_50_90.merge.EVNT.e6452_e5984_tid12959107_00 | DATASET      |
| panda:panda.16555277.12.24.EVNT.21976074-4b10-4e47-af5c-6de09c91f34e_dis4190454467                           | DATASET      |
| panda:panda.16555277.12.24.EVNT.31312b10-d4dd-4450-be34-0efc7b4fea61_dis4190454493                           | DATASET      |
| panda:panda.16555277.12.24.EVNT.dae88869-4cab-4d18-9d34-8989bb2475c4_dis4190454518                           | DATASET      |
+--------------------------------------------------------------------------------------------------------------+--------------+

input comes from job proddblock
mc16_13TeV:mc16_13TeV.364351.Sherpa_224_NNPDF30NNLO_Diphoton_myy_50_90.merge.EVNT.e6452_e5984_tid12959107_00

* loop over tasks (status:done AND tasktype:prod)
    * get "creationdate" 
    * get all jobs of this task (taskid:16357413 AND jobstatus:finished)
        * get time they took, nfiles processed, cores

some jobs will have 0 input files but will need to be processed.