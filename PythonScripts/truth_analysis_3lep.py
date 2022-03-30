#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

fileName_1 = "/cluster/home/amyrewoldt/susy_test/aod/DAOD_TRUTH1.test.pool.root"
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

fileName = [fileName_1]#,fileName_2,fileName_3,fileName_4]#,fileName_5]

def declare_histos(histogram,name):
  for h in range(len(histogram)):
    for n in name:
      return ROOT.TH1F(str(histogram[:-5])+"_"+str(file)+"_3lep",n,50,0,500)    

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()
  outputFile = ROOT.TFile.Open("histo.overlay.root", "UPDATE")
  #outputfile = ROOT.TFile.Open("histo.root", "UPDATE")

 ###################################
 # Begin Code for H+ TO 3LEP + MET #
 ###################################

  histograms = ["MET_3lep","visiblePt_3lep","visibleMt_3lep","Mt_3lep","ossfM_3lep","ossfPt_3lep","first_3lep","second_3lep","third_3lep"]
  names = ["Missing Transverse Momentum","Transverse Momentum of 3-lepton Final States","Transverse Mass of 3-leptons Final States","OSSF Dilepton Mass","OSSF Dilepton Pt","Leading Lepton P_t","SubLeading Lepton P_t","Third Leading Lepton P_t"]
  for h in range(len(histograms)):
    histograms[h] = declare_histos(histograms[h],names)

  for entry in xrange(t.GetEntries()):
    t.GetEntry(entry)
    p = t.TruthParticles
    met = t.MET_Truth.at(0)
#    jet = t.AntiKt4TruthDressedWZJets
    lepvector = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
    metvector = ROOT.TLorentzVector(0,0,0,0)
    metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)
    mu = t.TruthMuons
    el = t.TruthElectrons

    leps = []
    for m in mu:
      print m.m()
    for e in el:
      print e.m()
    
    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt()))    
    if len(leps) < 3: continue
    if abs(leps[0].pdgId() + leps[1].pdgId() + leps[2].pdgId()) not in [11, 13]: continue 
    if len(set([abs(leps[0].pdgId()), abs(leps[1].pdgId()), abs(leps[2].pdgId())])) != 2: continue
    lepvector = leps[0].p4() + leps[1].p4() + leps[2].p4()
    histograms[0].Fill(metvector.Pt()/1000) #PT FROM MET 3LEP
    histograms[1].Fill(lepvector.Pt()/1000) #mass of 3 leptons in decay chain
    histograms[2].Fill(lepvector.M()/1000) #mass of 3 leptons in decay chain
    histograms[3].Fill((lepvector + metvector).Mt()/1000)
    histograms[6].Fill(leps[0].p4().Pt()/1000)
    histograms[7].Fill(leps[1].p4().Pt()/1000)
    histograms[8].Fill(leps[2].p4().Pt()/1000)

    for pair in [(0, 1), (0, 2), (1, 2)]:
      if leps[pair[0]].pdgId() + leps[pair[1]].pdgId() == 0:
        p4 = leps[pair[0]].p4() + leps[pair[1]].p4()
        histograms[4].Fill(p4.M()/1000)
        histograms[5].Fill(p4.Pt()/1000)
        break

  canvas = ROOT.TCanvas()
  outputFile.Write()
print "Finished"
