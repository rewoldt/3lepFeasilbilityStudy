**Charged higgs to Hplus feasibility study**

tier3 contains all files (DAOD, runcards, event generation scripts, etc):

    path: /cluster/home/amyrewoldt

AthDerivation version used to run over PythonScripts

    setupATLAS
    cd ProjectDirectory
    asetup AthDerivation,21.2.48.0, here

JupyterNotebooks on tier3
Locally run:
    ssh -N -f -L localhost:8000:localhost:8000 usrname@master.tier3-atlas.uta.edu
On tier3 (must install miniconda first)
    source miniconda/bin/activate
    jupyter notebook --port=8000 --no-browser
Copy http provided and paste into browser of choice (http should look like: http://127.0.0.1:8000/?token=d468f0e00aa7c8a9abcc15f4177a985d818d4aa639fbaf16).

csvFilesMVA primarily made by running python script
    /cluster/home/amyrewoldt/21.2.48/run/MVA_3lep_v3.py
