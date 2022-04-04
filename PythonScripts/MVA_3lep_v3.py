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

def get_children(particle):
  list = []
  for i in range(particle.nChildren()):
#    print "parent: ", particle.pdgId(), ", child particle: ", particle.child(i).pdgId(), ", mass: ", particle.child(i).m(), ", pt: ", particle.child(i).pt(), "\n"
    if particle.child(i).nChildren() == 0:
      if particle.child(i).absPdgId() in [11,13]:
        list.append(particle.child(i))
    else:
      list += get_children(particle.child(i))
  return list

def pdg(n):
	#takes a particles container and returns the pdgId
	return n.pdgId()

def PT(n):
	#takes a particles container and returns the pt
	return n.p4().Pt()

def selectLeptons(leps):
  # assume the list is already sorted to start with highest pT
  first = leps[0]
  best = None
  for lep in leps[1:]:
    if first.pdgId() + lep.pdgId() != 0: continue
    if best == None: best = lep
    if first.p4().DeltaR(lep.p4()) < first.p4().DeltaR(best.p4()): best = lep
  sel = [first, best] if best else [first]
  for lep in leps:
    if lep in sel: continue
    sel.append(lep)
    break
  return sel

#################################
######### Opening File ##########
#################################

fileName_ttb = "/cluster/home/bburghgr/truth-ttb/mc16_13TeV.410470.PhPy8EG_A14_ttbar_hdamp258p75_nonallhad.deriv.DAOD_TRUTH1.e6337_p3401/DAOD_TRUTH1.13470208._000496.pool.root.1"
#fileName_benchmark_500 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus500_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
#fileName_benchmark_600 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus600_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
#fileName_benchmark_700 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus700_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
#fileName_benchmark_800 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus800_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
#fileName_benchmark_1000 = "/cluster/home/amyrewoldt/DAOD/3lep_benchmark_Hplus1000_slep110/truth1/DAOD_TRUTH1.aod.pool.root"
#fileName_benchmark_800_fixed = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus800_slep110_Xn165_Xc120_fixed/truth1/DAOD_TRUTH1.test.pool.root"
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
    name = 'sig500-allvar-btag-extended-dataset.csv'
  if '600' in fileName[file]:
    name = 'sig600-allvar-btag-extended-dataset.csv'
  if '700' in fileName[file]:
    name = 'sig700-allvar-btag-extended-dataset.csv'
  if '800' in fileName[file]:
    name = 'sig800-allvar-btag-extended-dataset.csv'
  if '1000' in fileName[file]:
    name = 'sig1000-allvar-btag-extended-dataset.csv'
  if 'ttb' in fileName[file]:
    name = 'bkg-allvar-btag-extended-dataset.csv'

  ##========================
  print "Working on ", fileName[file]

#  DR = []
#  Mll = []
  lepton1_pt = []
  lepton2_pt = []
  lepton3_pt = []
  lepton1_eta = []
  lepton2_eta = []
  lepton3_eta = []
  lepton1_phi = []
  lepton2_phi = []
  lepton3_phi = []
  lepton1_flavor = []
  lepton2_flavor = []
  lepton3_flavor = []
  lepton1_charge = []
  lepton2_charge = []
  lepton3_charge = []
  MET=[]
  MET_phi = []
  visible_pt = []
  dilep_DR = []
  dilep_mass = [] 
  transverse_mass = []
  counter_3lep = 0
  counter_ossf = 0
  counter = 0

#  for entry in xrange(1000):
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
    leps_neu = []
    leps_ch = []
    selected_lepton_list = []
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

#    leps = electron_list + muon_list
    lepton_list = electron_list + muon_list
#    print len(lepton_list)
    electron_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
    muon_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
#    leps.sort(reverse = True, key=(lambda l: l.p4().Pt()))
    lepton_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
      
#    if len(leps) < 3: continue
    if len(lepton_list) < 3: continue
#    counter_3lep += 1
#    if len(lepton_list) < 3: continue
#    lepton_list = selectLeptons(leps)
    if abs(lepton_list[0].pdgId() + lepton_list[1].pdgId() + lepton_list[2].pdgId()) not in [11,13]: continue
#    counter_ossf += 1
    lepton1_pt.append(lepton_list[0].p4().Pt())
    lepton2_pt.append(lepton_list[1].p4().Pt())
    lepton3_pt.append(lepton_list[2].p4().Pt())
    lepton1_eta.append(lepton_list[0].eta())
    lepton2_eta.append(lepton_list[1].eta())
    lepton3_eta.append(lepton_list[2].eta())
    lepton1_phi.append(lepton_list[0].phi())
    lepton2_phi.append(lepton_list[1].phi())
    lepton3_phi.append(lepton_list[2].phi())
    lepton1_charge.append(lepton_list[0].pdgId()/lepton_list[0].absPdgId())
    lepton2_charge.append(lepton_list[1].pdgId()/lepton_list[1].absPdgId())
    lepton3_charge.append(lepton_list[2].pdgId()/lepton_list[2].absPdgId())

    lepton1_flavor.append(lepton_list[0].absPdgId())
    lepton2_flavor.append(lepton_list[1].absPdgId())
    lepton3_flavor.append(lepton_list[2].absPdgId())

    lepton_vector = lepton_list[0].p4() + lepton_list[1].p4() + lepton_list[2].p4()
    MET.append(metvector.Pt())
    MET_phi.append(metvector.Phi())
    visible_pt.append(lepton_vector.Pt())
    transverse_mass.append((lepton_vector+metvector).Mt())

    Mll = None
    DR = None
    for pair in [(0, 1), (0, 2), (1, 2)]:
#        print leps[pair[0]].pdgId() + leps[pair[1]].pdgId(), leps[pair[0]].pdgId()
      if lepton_list[pair[0]].pdgId() + lepton_list[pair[1]].pdgId() != 0: continue #if these two are same flavor op sign ex: -11 +11 
      p4 = lepton_list[pair[0]].p4() + lepton_list[pair[1]].p4()
      Mll = p4.M()
      DR = lepton_list[pair[0]].p4().DeltaR(lepton_list[pair[1]].p4())
      break
    dilep_mass.append(Mll)
    dilep_DR.append(DR)

#  print counter, counter_3lep, counter_ossf, float(counter_3lep)/counter, float(counter_ossf)/counter
  data = zip([lepton1_pt,lepton2_pt,lepton3_pt,lepton1_eta,lepton2_eta,lepton3_eta,lepton1_phi,lepton2_phi,lepton3_phi,MET,MET_phi,lepton1_flavor, lepton2_flavor, lepton3_flavor,lepton1_charge,lepton2_charge,lepton3_charge,visible_pt,transverse_mass,dilep_mass,dilep_DR])
  with open(name, mode='w') as df:
#  with open('bkg-high-low-var.csv', mode='w') as df:
    df_writer = csv.writer(df, dialect='excel', delimiter=',', quoting=csv.QUOTE_NONE)
    df_writer.writerow(["","lepton1_pt","lepton2_pt","lepton3_pt","lepton1_eta","lepton2_eta","lepton3_eta","lepton1_phi","lepton2_phi","lepton3_phi","MET","MET_phi","lepton1_flavor", "lepton2_flavor", "lepton3_flavor","lepton1_charge","lepton2_charge","lepton3_charge","visible_pt","transverse_mass","dilep_mass","dilep_DR"])
    for i in range(len(lepton1_pt)):
      df_writer.writerow((i,lepton1_pt[i],lepton2_pt[i],lepton3_pt[i],lepton1_eta[i],lepton2_eta[i],lepton3_eta[i],lepton1_phi[i],lepton2_phi[i],lepton3_phi[i],MET[i],MET_phi[i],lepton1_flavor[i], lepton2_flavor[i], lepton3_flavor[i],lepton1_charge[i],lepton2_charge[i],lepton3_charge[i],visible_pt[i],transverse_mass[i],dilep_mass[i],dilep_DR[i]))
  print df

  print "Finished"
