#!/bin/bash
source ~/setup.txt

read -p "Enter file tag:" filetag
mkdir ~/3lep_$filetag
cd ~/3lep_$filetag
read -p "Enter MG run number:" run_number
cp ~/MG5_aMC_v2_6_5/mssm_3lep/Events/$run_number/unweighted_events.lhe.gz .
gunzip unweighted_events.lhe.gz
mv unweighted_events.lhe madgraph.000001.Example._00001.events
tar cvzf madgraph.000001.Example._00001.events.tar.gz madgraph.000001.Example._00001.events

mkdir ~/3lep_$filetag/evgen
cd ~/3lep_$filetag/evgen
asetup 21.0.77,Athena,here

Generate_tf.py --ecmEnergy=13000. --maxEvents=100000 --runNumber=284500 --firstEvent=1 --randomSeed=123456 --outputEVNTFile=evgen.root --jobConfig=~bburghgr/cards/testlhe.py --inputGeneratorFile=../madgraph.000001.Example._00001.events.tar.gz

mkdir ~/3lep_$filetag/truth1
cd ~/3lep_$filetag/truth1
asetup 21.2.48.0,AthDerivation,here
Reco_tf.py --maxEvents=100000 --inputEVNTFile ../evgen/evgen.root --outputDAODFile aod.pool.root --reductionConf TRUTH1 
