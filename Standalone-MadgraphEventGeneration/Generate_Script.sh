#!/bin/bash
source ~/setup2.txt

read -p "Enter file path: ~/" filepath
cd ~/$filepath/
mkdir evgen
cd evgen
asetup 21.0.77,Athena,here

Generate_tf.py --ecmEnergy=13000. --maxEvents=-1 --runNumber=284500 --firstEvent=1 --randomSeed=123456 --outputEVNTFile=evgen.root --jobConfig=~bburghgr/cards/testlhe.py --inputGeneratorFile=../madgraph.000001.Example._00001.events.tar.gz
