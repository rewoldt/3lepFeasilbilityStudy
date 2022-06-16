#!/usr/bin/env python2.7

import ROOT
#import numpy as np
#import pandas as pd
import csv

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

#################################
########### Functions ###########
#################################

#################################
######### Opening File ##########
#################################

fileName_ttb = "/cluster/home/bburghgr/truth-ttb/mc16_13TeV.410470.PhPy8EG_A14_ttbar_hdamp258p75_nonallhad.deriv.DAOD_TRUTH1.e6337_p3401/DAOD_TRUTH1.13470208._000496.pool.root.1"
fileName_benchmark_500 = "/cluster/home/amyrewoldt/DAOD/3lep_500GeV_100KDataset/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_600 = "/cluster/home/amyrewoldt/DAOD/3lep_600GeV_100KDataset/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_700 = "/cluster/home/amyrewoldt/DAOD/3lep_700GeV_100KDataset/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_800 = "/cluster/home/amyrewoldt/DAOD/3lep_800GeV_100KDataset/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_1000 = "/cluster/home/amyrewoldt/DAOD/3lep_1000GeV_100KDataset/truth1/DAOD_TRUTH1.aod.pool.root"

fileName = [fileName_benchmark_500,fileName_benchmark_600,fileName_benchmark_700,fileName_benchmark_800,fileName_benchmark_1000,fileName_ttb] #,fileName_benchmark_1000_slep_110]
#fileName = [fileName_ttb] #,fileName_benchmark_1000_slep_110]
#fileName = [fileName_benchmark_800,fileName_ttb] #,fileName_benchmark_1000_slep_110]

########################################
############# Code Starts ##############
########################################

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()
  nevents = t.GetEntries()

  if '500' in fileName[file]:
    name = 'sig500-LBN.csv'
  if '600' in fileName[file]:
    name = 'sig600-LBN.csv'
  if '700' in fileName[file]:
    name = 'sig700-LBN.csv'
  if '800' in fileName[file]:
    name = 'sig800-LBN.csv'
  if '1000' in fileName[file]:
    name = 'sig1000-LBN.csv'
  if 'ttb' in fileName[file]:
    name = 'bkg-LBN.csv'

  ##========================
  print "Working on ", fileName[file]

  lepton1_px = []
  lepton1_py = []
  lepton1_pz = []
  lepton2_px = []
  lepton2_py = []
  lepton2_pz = []
  lepton3_px = []
  lepton3_py = []
  lepton3_pz = []
  lepton1_E = []
  lepton2_E = []
  lepton3_E = []
  MET_px=[]
  MET_py=[]
  MET_pz=[]
  MET_E=[]

  for entry in xrange(nevents):
    t.GetEntry(entry)
    taus = t.TruthTaus
    bsm = t.TruthBSM
    neturino = t.TruthNeutrinos
    met = t.MET_Truth.at(0)
    jets = t.AntiKt4TruthDressedWZJets
    top = t.TruthTop
    bosons = t.TruthBoson
    muons = t.TruthMuons
    electrons = t.TruthElectrons
    p = t.TruthParticles
    lepton_list = []
    muon_list = []
    electron_list = []
    B_list = []
    lepton_vector = ROOT.TLorentzVector(0,0,0,0)
    electron_vector = ROOT.TLorentzVector()
    muons_vector = ROOT.TLorentzVector()


	#=========================
 #   print entry*100/t.GetEntries(), "% complete."
 #   print "This is entry number: ", entry+1
	#=========================
	# print Met.get(1).met()
    metvector = ROOT.TLorentzVector(0,0,0,0)
    metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)

    for pp in p:
      if pp.absPdgId() != 5: continue
      B_list.append(pp)

    for b in B_list:
      for l in electrons:
        if l.p4().DeltaR(b.p4()) > .4:
          electron_list.append(l)
      for m in muons:
        if m.p4().DeltaR(b.p4()) > .4:
          muon_list.append(m)
      break
 
    lepton_list = electron_list + muon_list
#    print len(lepton_list)
    electron_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
    muon_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
    lepton_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
    
    if len(lepton_list) < 3: continue
    if abs(lepton_list[0].pdgId() + lepton_list[1].pdgId() + lepton_list[2].pdgId()) not in [11,13]: continue
    lepton1_px.append(lepton_list[0].px())
    lepton1_py.append(lepton_list[0].py())
    lepton1_pz.append(lepton_list[0].pz())
    lepton2_px.append(lepton_list[1].px())
    lepton2_py.append(lepton_list[1].py())
    lepton2_pz.append(lepton_list[1].pz())
    lepton3_px.append(lepton_list[2].px())
    lepton3_py.append(lepton_list[2].py())
    lepton3_pz.append(lepton_list[2].pz())
    lepton1_E.append(lepton_list[0].p4().E())
    lepton2_E.append(lepton_list[1].p4().E())
    lepton3_E.append(lepton_list[2].p4().E())
    metpz = 0
    MET_E.append(metvector.Pt())
    MET_px.append(metvector.Px())
    MET_py.append(metvector.Py())
    MET_pz.append(0)
    #MET_phi.append(metvector.Phi())
    #visible_pt.append(lepton_vector.Pt())
    #transverse_mass.append((lepton_vector+metvector).Mt())


  data = zip([lepton1_E,lepton1_px,lepton1_py,lepton1_pz,lepton2_E,lepton2_px,lepton2_py,lepton2_pz,lepton3_E,lepton3_px,lepton3_py,lepton3_pz,MET_E,MET_px,MET_py,MET_pz])
  with open(name, mode='w') as df:
#  with open('bkg-high-low-var.csv', mode='w') as df:
    df_writer = csv.writer(df, dialect='excel', delimiter=',', quoting=csv.QUOTE_NONE)
    df_writer.writerow(["","lepton1_E","lepton1_px","lepton1_py","lepton1_pz","lepton2_E","lepton2_px","lepton2_py","lepton2_pz","lepton3_E","lepton3_px","lepton3_py","lepton3_pz","MET_E","MET_px","MET_py","MET_pz"])
    for i in range(len(lepton1_px)): 
      df_writer.writerow((i,lepton1_E[i],lepton1_px[i],lepton1_py[i],lepton1_pz[i],lepton2_E[i],lepton2_px[i],lepton2_py[i],lepton2_pz[i],lepton3_E[i],lepton3_px[i],lepton3_py[i],lepton3_pz[i],MET_E[i],MET_px[i],MET_py[i],MET_pz[i]))
  print df

  print "Finished"
