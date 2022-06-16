#!/bin/bash
read -p "Enter Directory Name:" dirname

mkdir ~/DAOD/$dirname/merged
cd ~/DAOD/$dirname/merged
cat ~/DAOD/pbs2.sh > merge_and_mkaod.txt
echo "cd ~/DAOD/$dirname/merged" >> merge_and_mkaod.txt
echo 'asetup 21.0.77,Athena,here' >> merge_and_mkaod.txt
echo "HITSMerge_tf.py --outputHITSFile hits.merge.root --inputHITSFile ../hits_*/hits.root" >> merge_and_mkaod.txt
chmod +x merge_and_mkaod.txt

qsub ~/DAOD/$dirname/merged/merge_and_mkaod.txt | tee jobID.txt

