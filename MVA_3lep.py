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

def find_parent(p):
	#takes a particles container and retruns a list of the child particle container
	for i in range(p.nParents()):
		if p.parent(i).pdgId() != p.pdgId():
			return [p.child(i) for i in range(p.nParents())]
		else:
			return find_parent(p.parent())

def pdg(n):
	#takes a particles container and returns the pdgId
	return n.pdgId()

def PT(n):
	#takes a particles container and returns the pdgId
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
fileName_benchmark_500 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus500_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_600 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus600_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_700 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus700_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_800 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus800_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_1000 = "/cluster/home/amyrewoldt/DAOD/3lep_benchmark_Hplus1000_slep110/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_800_fixed = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus800_slep110_Xn165_Xc120_fixed/truth1/DAOD_TRUTH1.test.pool.root"

fileName = [fileName_benchmark_500,fileName_benchmark_600,fileName_benchmark_700,fileName_benchmark_800,fileName_benchmark_1000,fileName_ttb] #,fileName_benchmark_1000_slep_110]
#fileName = [fileName_ttb] #,fileName_benchmark_1000_slep_110]
#fileName = [fileName_benchmark_800] #,fileName_benchmark_1000_slep_110]

########################################
############# Code Starts ##############
########################################

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()
  nevents = t.GetEntries()

  if '500' in fileName[file]:
    name = 'sig500-bdt.csv'
  if '600' in fileName[file]:
    name = 'sig600-bdt.csv'
  if '700' in fileName[file]:
    name = 'sig700-bdt.csv'
  if '800' in fileName[file]:
    name = 'sig800-bdt.csv'
  if '1000' in fileName[file]:
    name = 'sig1000-bdt.csv'
  if 'ttb' in fileName[file]:
    name = 'bkg-bdt.csv'

  ##========================
  print "Working on ", fileName[file]

  lepton_pt = []
  MET=[]
  MT=[]
  Mll=[]
  lepton_pt_l = []
  MET_l=[]
  MT_l=[]
  Mll_l=[]
  DR_l=[]

  for entry in xrange(9999):
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
    lepton_vector = ROOT.TLorentzVector(0,0,0,0)
    electron_vector = ROOT.TLorentzVector()
    muons_vector = ROOT.TLorentzVector()


	#=========================
    print entry*100/t.GetEntries(), "% complete."
    print "This is entry number: ", entry+1
	#=========================
	# print Met.get(1).met()
    metvector = ROOT.TLorentzVector(0,0,0,0)
    metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)

#####################################
############### BKG #################
#####################################
    '''    if '_ttb' in fileName[file]:
      for l in electrons:
        electron_list.append(l)
      for m in muons:
        muon_list.append(m)

      lepton_list = electron_list + muon_list
      print len(lepton_list)
      electron_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
      muon_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
      lepton_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))

      el_list=map(PT,electron_list)
      mu_list=map(PT,muon_list)
      lepton_list_pt= map(PT,lepton_list)

      if len(lepton_list) < 3: continue
      lepton_vector = lepton_list[0].p4() + lepton_list[1].p4() + lepton_list[2].p4()
      MT = (lepton_vector+metvector).Mt()

      for pair in [(0, 1), (0, 2), (1, 2)]:
    #      print leps[pair[0]].pdgId() + leps[pair[1]].pdgId(), leps[pair[0]].pdgId()
        if lepton_list[pair[0]].pdgId() + lepton_list[pair[1]].pdgId() != 0: continue #if these two are same flavor op sign ex: -11 +11 
        p4 = lepton_list[pair[0]].p4() + lepton_list[pair[1]].p4()
        Mll = p4.M()
        DR = lepton_list[pair[0]].p4().DeltaR(lepton_list[pair[1]].p4())
        break 

    lepton_pt_l.append(lepton_vector.Pt())
    MET_l.append(metvector.Pt())
    MT_l.append(MT)
    DR_l.append(DR)
    Mll_l.append(Mll) '''

########################################
############# Signal ###################
########################################

#    if '_background' in fileName[file]:
    for l in electrons:
      electron_list.append(l)
    for m in muons:
      muon_list.append(m)

    lepton_list = electron_list + muon_list
    print len(lepton_list)
    electron_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
    muon_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))
    lepton_list.sort(reverse = True, key=(lambda l: l.p4().Pt()))

#    if len(lepton_list) < 3: continue
#    selected_lepton_list = lepton_list
#    selected_lepton_list = selectLeptons(lepton_list)

    #el_list=map(PT,electron_list)
    #mu_list=map(PT,muon_list)
    #lepton_list_pt= map(PT,lepton_list)
    if len(lepton_list) < 3: continue
    lepton_vector = lepton_list[0].p4() + lepton_list[1].p4() + lepton_list[2].p4()
    MT = (lepton_vector+metvector).Mt()

    for pair in [(0, 1), (0, 2), (1, 2)]:
  #      print leps[pair[0]].pdgId() + leps[pair[1]].pdgId(), leps[pair[0]].pdgId()
      if lepton_list[pair[0]].pdgId() + lepton_list[pair[1]].pdgId() != 0: continue #if these two are same flavor op sign ex: -11 +11 
      p4 = lepton_list[pair[0]].p4() + lepton_list[pair[1]].p4()
      Mll = p4.M()
      DR = lepton_list[pair[0]].p4().DeltaR(lepton_list[pair[1]].p4())
      break 

#    if len(selected_lepton_list) < 3: continue
#    lepton_vector = selected_lepton_list[0].p4() + selected_lepton_list[1].p4() + selected_lepton_list[2].p4()
#    MT = (lepton_vector+metvector).Mt()

#    for pair in [(0, 1), (0, 2), (1, 2)]:
#      print leps[pair[0]].pdgId() + leps[pair[1]].pdgId(), leps[pair[0]].pdgId()
#      if selected_lepton_list[pair[0]].pdgId() + selected_lepton_list[pair[1]].pdgId() != 0: continue #if these two are same flavor op sign ex: -11 +11 
#      p4 = selected_lepton_list[pair[0]].p4() + selected_lepton_list[pair[1]].p4()
#      Mll = p4.M()
#      DR = selected_lepton_list[pair[0]].p4().DeltaR(selected_lepton_list[pair[1]].p4())
#      break

    lepton_pt_l.append(lepton_vector.Pt())
    MET_l.append(metvector.Pt())
    MT_l.append(MT)
    Mll_l.append(Mll)
    DR_l.append(DR)

  data = zip([lepton_pt_l,MET_l,MT_l,Mll_l,DR_l])
#  df = pd.DataFrame(data,columns=["lepton_pt","MET","MT","Mll"])
  with open(name, mode='w') as df:
#  with open('bkg-bdt.csv', mode='w') as df:
    df_writer = csv.writer(df, dialect='excel', delimiter=',', quoting=csv.QUOTE_NONE)
    df_writer.writerow(["","lepton_pt_l","MET_l","MT_l","Mll_l","DR_l"])
    for i in range(len(lepton_pt_l)):
      df_writer.writerow((i,lepton_pt_l[i],MET_l[i],MT_l[i],Mll_l[i],DR_l[i]))
#    writer.writerow({'lepton_pt': lepton_pt_l, 'MET': MET_l, 'MT': MT_l, 'Mll': Mll_l})
  print df
#  df.to_csv("{}.csv".format("bkgtest"))

  print "Finished" 
#  break
