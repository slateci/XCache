# Simulating XCache on historical data

## Rucio Traces

Rucio runs a REST API that collects data from diffent clients requesting the data.
This can be a user trying to download a file or dataset or Pilot trying to get path to data.
Records are described [here](https://twiki.cern.ch/twiki/bin/view/PanDA/PilotRucioTraces).

To destinguish type of access one uses field "eventType". The most important are:
* get_sm - production job input download
* get_sm_a - analysis job input download
* put_sm - production job output upload
* put_sm_a - analysis job output upload   

## Results

* understanding formats, simulation of single site [slides](https://docs.google.com/presentation/d/1pDKLF4Yxztf2dNZNUetcwWqaUD0Gigv2TVe7NbNsxGc/edit?usp=sharing).
* understanding multilayer cache, throughput needed, simulation of US network [slides](https://docs.google.com/presentation/d/1Z77OTskVHxywhdbNu9bY4jYRnc7eG-DZn7Hu0w6dhZA/edit?usp=sharing).
* simulation of cache optimized job scheduling.

# AB testing
* effect on jobs wall times
* effect on tasks turn-around times 
