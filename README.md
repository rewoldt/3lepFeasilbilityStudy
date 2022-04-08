# Charged Higgs to Hplus feasibility study

tier3 contains all files (DAOD, runcards, event generation scripts, etc)
    path: /cluster/home/amyrewoldt

## Versioning
### AthDerivation version used to run over PythonScripts

    setupATLAS
    cd ProjectDirectory
    asetup AthDerivation,21.2.48.0, here

*csvFilesMVA primarily made by running python script*

    /cluster/home/amyrewoldt/21.2.48/run/MVA_3lep_v3.py


### Standalone Event Generation Using Madgraph 2.7.3

	wget https://launchpad.net/mg5amcnlo/2.0/2.7.x/+download/MG5_aMC_v2.7.3.tar.gz
	gunzip MG5_aMC_v2.7.3.tar.gz
	cd MG5_aMC_v2_7_3
	wget https://gitlab.cern.ch/arewoldt/3lep-analysis/-/blob/master/Standalone-MadgraphEventGeneration/proc_card_mg5_3lep.dat
	./bin proc_card_mg5_3lep.dat
There should be a directory *mssm_3lep* after completion of this step. This directory should be set up to run mssm 3lep process. 
To generate events:
	./bin/generate_events
To create DAOD use script Generate_Script.sh (clone from Standalone-MadgraphEventGenerationi directory). Make sure to change the setup script to either setupATLAS or path to your own setup script. For DAOD'si run:
	./Generate.sh

### OTFR Event Generation

## JupyterNotebooks on tier3
### Setup Instructions
[HERE](https://gitlab.cern.ch/arewoldt/3lep-analysis/-/blob/master/JupyterNotebooks/Jupyter-notebook-tier3-setup.pdf)
### After setup
Locally run:

    ssh -N -f -L localhost:8000:localhost:8000 usrname@master.tier3-atlas.uta.edu
On tier3
    source miniconda/bin/activate
    jupyter notebook --port=8000 --no-browser
Copy http provided and paste into browser of choice (http should look like: *http://127.0.0.1:8000/?token=d468f0e00aa7c8a9abcc15f4177a985d818d4aa639fbaf16*).

