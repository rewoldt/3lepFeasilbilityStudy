#!/usr/bin/env python2.7
# Set up ROOT and RootCore:
import numpy
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

fileName_1 = "/cluster/home/amyrewoldt/susy_test/aod160/DAOD_TRUTH1.test.pool.root"
#fileName_1 = "/cluster/home/bburghgr/truth-3lep-grid/truth1/300/DAOD_TRUTH1.test.pool.root" 
#fileName_2 = "/cluster/home/bburghgr/truth-3lep-grid/truth1/400/DAOD_TRUTH1.test.pool.root"
#fileName_3 = "/cluster/home/bburghgr/truth-3lep-grid/truth1/500/DAOD_TRUTH1.test.pool.root"
#fileName_4 = "/cluster/home/bburghgr/truth-3lep-grid/truth1/1000/DAOD_TRUTH1.test.pool.root"
#fileName_1 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_25/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_2 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_50/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_3 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_100/evgen/DAOD_TRUTH1.test.pool.root"
#fileName_4 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_200/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_5 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_400/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_1 = "/cluster/home/amyrewoldt/DAOD/HeavyHiggs25spl/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_2 = "/cluster/home/amyrewoldt/DAOD/HeavyHiggs50spl/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_3 = "/cluster/home/amyrewoldt/DAOD/HeavyHiggs100spl/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_4 = "/cluster/home/amyrewoldt/DAOD/HeavyHiggs200spl/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_5 = "/cluster/home/amyrewoldt/DAOD/HeavyHiggs400Split/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_1 = "/cluster/home/amyrewoldt/DAOD/fixed_neuspl_25/25/DAOD_TRUTH1.test.pool.root"
#fileName_2 = "/cluster/home/amyrewoldt/DAOD/fixed_neuspl_50/50/DAOD_TRUTH1.test.pool.root"
#fileName_3 = "/cluster/home/amyrewoldt/DAOD/fixed_neuspl_100/100/DAOD_TRUTH1.test.pool.root"
#fileName_4 = "/cluster/home/amyrewoldt/DAOD/fixed_neuspl_200/200/DAOD_TRUTH1.test.pool.root"
#fileName_5 = "/cluster/home/amyrewoldt/DAOD/fixed_neuspl_400/400/DAOD_TRUTH1.test.pool.root"
#fileName_1 = "/cluster/home/amyrewoldt/DAOD/CloserHiggsMassFile/Heavy/DAOD_TRUTH1.test.pool.root"

def declare_histos(histogram,name):
  for h in range(len(histogram)):
    for n in name:
      return ROOT.TH1F(str(histogram[:-5])+"_"+str(file)+"_3lep",n,50,0,1000)    

fileName = [fileName_1]#,fileName_2,fileName_3,fileName_4,fileName_5]
#fileName = [fileName_1,fileName_2,fileName_3,fileName_4,fileName_5]
for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()
  #outputfile = ROOT.TFile.Open("histo.root", "UPDATE")
  outputFile = ROOT.TFile.Open("histos.truthparticles.root", "UPDATE")

 ###################################
 # Begin Code for H+ TO 3LEP + MET #
 ###################################

  histograms = ["MET_3lep","visiblePt_3lep","visibleMt_3lep","Mt_3lep","ossfM_3lep","ossfPt_3lep","first_3lep","second_3lep","third_3lep","higgs_mass","neu_mass","ch_mass","lep1_mass","lep2_mass","lep3_mass"]
  names = ["Missing Transverse Momentum","Transverse Momentum of 3-lepton Final States","Transverse Mass of 3-leptons Final States","OSSF Dilepton Mass","OSSF Dilepton Pt","Leading Lepton P_t","SubLeading Lepton P_t","Third Leading Lepton P_t","mass of higgs","neu_mass","ch_mass","lep1_mass","lep2_mass","lep3_mass"]
  for h in range(len(histograms)):
    histograms[h] = declare_histos(histograms[h],names)
    
  counter_SDeVE = 0
  counter_first = 0
  counter_second = 0
  counter_third = 0
  counter_ossf = 0

  for entry in xrange(t.GetEntries()):
    t.GetEntry(entry)
    p = t.TruthParticles
    met = t.MET_Truth.at(0)
#    jet = t.AntiKt4TruthDressedWZJets
    lepvector = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all childreninos
    metvector = ROOT.TLorentzVector(0,0,0,0)
    metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)

    def get_children(particle):
      if particle.absPdgId() in [11,13]: 
        return [particle]
      else: 
        list = []
        for i in range(particle.nChildren()):
          list += get_children(particle.child(i))
        return list

    def get_mother(particle):
      if particle.absPdgId() in [1000023,1000024]: 
        return particle
      elif particle.nParents() != 1: 
        return None
      else:
        return get_mother(particle.parent())

    ch_childreninos = []
    neu_childreninos = []

    for pp in p:
      if abs(pp.pdgId()) != 37: continue
      histograms[9].Fill(pp.m()/1000)
      for i in range(pp.nChildren()):
        if abs(pp.child(i).pdgId()) == 1000023:
          neu_childreninos += get_children(pp.child(i))
          histograms[10].Fill(pp.child(i).m()/1000)
        if pp.child(i).absPdgId() == 1000024:
          ch_childreninos += get_children(pp.child(i))
          histograms[11].Fill(pp.child(i).m()/1000)

    childreninos = neu_childreninos + ch_childreninos
    childreninos = sorted(childreninos, reverse = True, key=(lambda l: l.p4().Pt()))  
  
#    if childreninos[0] in neu_childreninos:
#      if get_mother(childreninos[0]).absPdgId() != 1000023: continue
#      counter_first += 1
#    if childreninos[1] in neu_childreninos:
#      if get_mother(childreninos[0]).absPdgId() != 1000023: continue
#      counter_second += 1
#    if childreninos[2] in neu_childreninos:
#      if get_mother(childreninos[0]).absPdgId() != 1000023: continue
#      counter_third += 1
  
    if len(childreninos) < 3: continue    
#    lepvector = childreninos[0].p4() + childreninos[1].p4() + childreninos[2].p4()
#    histograms[0].Fill(metvector.Pt()/1000) #PT FROM MET 3LEP
#    histograms[1].Fill(lepvector.Pt()/1000) #mass of 3 leptons in decay chain
#    histograms[2].Fill(lepvector.M()/1000) #mass of 3 leptons in decay chain
#    histograms[3].Fill((lepvector + metvector).Mt()/1000)
#    histograms[6].Fill(childreninos[0].p4().Pt()/1000)
#    histograms[7].Fill(childreninos[1].p4().Pt()/1000)
#    histograms[8].Fill(childreninos[2].p4().Pt()/1000)
#    histograms[12].Fill(childreninos[0].p4().Pt()/1000)
#    histograms[13].Fill(childreninos[1].p4().Pt()/1000)
#    histograms[14].Fill(childreninos[2].p4().Pt()/1000)
#    mother_0 = get_mother(childreninos[0])
#    mother_1 = get_mother(childreninos[1])
  
#    for pair in [(0, 1), (0, 2), (1, 2)]:
#      if childreninos[pair[0]].pdgId() + childreninos[pair[1]].pdgId() == 0: continue #skip events with ossf
#      if childreninos[0].absPdgId() == childreninos[1].absPdgId() == childreninos[2].absPdgId():
#        third = [i for i in [0, 1, 2] if i not in pair][0]
#        if childreninos[pair[0]] in neu_childreninos and childreninos[third] in neu_childreninos:
#          counter_ossf += 1
#        else:
#          counter_SDeVE += 1
#        p4 = neu_childreninos[0].p4() + neu_childreninos[1].p4()
#        histograms[4].Fill(p4.M()/1000)
#        histograms[5].Fill(p4.Pt()/1000)
#        break

#  print counter_first, counter_second, counter_third, float(counter_ossf)/(counter_ossf + counter_SDeVE)
  canvas = ROOT.TCanvas()
  outputFile.Write()
print "Finished"
