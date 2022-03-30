#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )
ROOT.gStyle.SetOptStat(1)
import math

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

fileName_ttb = "/cluster/home/bburghgr/truth-ttb/mc16_13TeV.410470.PhPy8EG_A14_ttbar_hdamp258p75_nonallhad.deriv.DAOD_TRUTH1.e6337_p3401/DAOD_TRUTH1.13470208._000496.pool.root.1"
fileName_1 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus500_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_2 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus600_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_3 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus700_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_4 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus800_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_0 = "/cluster/home/amyrewoldt/DAOD/3lep_benchmark_Hplus1000_slep110/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_5 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_25/truth1/DAOD_TRUTH1.test.pool.root"
fileName_6 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_50/truth1/DAOD_TRUTH1.test.pool.root"
fileName_7 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_100/evgen/DAOD_TRUTH1.test.pool.root"
fileName_8 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_200/truth1/DAOD_TRUTH1.test.pool.root"
fileName = [fileName_1,fileName_2,fileName_3,fileName_4,fileName_0]

def mllmax(m_neu,m_slep,m_lsp):
  mllmax = sqrt((pow(m_neu,2)-pow(m_slep,2))*(pow(m_slep,2)-pow(m_lsp,2))/pow(m_slep,2))
  return mllmax

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

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
#  print "Number of input events:", t.GetEntries()
  n = t.GetEntries()
  outputFile = ROOT.TFile.Open("histo.root", "UPDATE")

  event_counter = 0
  counter_total = 0
  counter_matched = 0
  counter_ch_matched = 0
  counter_not_wb = 0
  counter_all_leps = 0
  counter_pair = 0

  DR = ROOT.TH1F("DR", "DR Between all Lepton Combinations",71,0,5)
  DR_leading = ROOT.TH1F("DR_leading","DR Between Leading Lep and Any Other Lepton",71,0,5)
  DR_Hplus = ROOT.TH1F("DR_Hplus","DR Between Leading Lep and Any Other Lepton",71,0,5)
  DR_neu = ROOT.TH1F("DR_neu","DR Between Leptons from 2nd Neutralino ",71,0,5)
  DR_ch = ROOT.TH1F("DR_ch","DR Between Both Leptons from Neutralino and Lepton from Chargino ",71,0,5)
  DR_leading_selection = ROOT.TH1F("DR_leading_selection", "DR Between Leading Lepton (from H+) and Leptons (2nd, 3rd leading) w/ OSSF",71,0,5)
  DR_selection = ROOT.TH1F("DR_selection", "DR Between Leading Lep and Any Other Lepton", 71,0,5)
  DR_leading_Hplus = ROOT.TH1F("DR_leading_Hplus", "DR Between Leading Lep and Any Other Lepton", 71,0,5)
  DR_W = ROOT.TH1F("DR_W", "DR Between all electrons/muons and taus's in Event", 71,0,10)

  for entry in xrange(5000):
    event_counter += 1
#    print "Event Number: ", event_counter
    t.GetEntry(entry)
    p = t.TruthParticles
    met = t.MET_Truth.at(0)
#    jet = t.AntiKt4TruthJets
    lepvector = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
    metvector = ROOT.TLorentzVector(0,0,0,0)
    metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)
    mu = t.TruthMuons
    el = t.TruthElectrons

    leps_neu = []
    leps_ch = []
    leps = []
    leps_Hplus = []
    leps_all = []
    leps_matched = []
    leps_ch_matched = []
    B = []
    leps_DR = []

    for pp in p:
      if pp.absPdgId() not in [511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]: continue
      B.append(pp)

    for pp in p:
      if abs(pp.pdgId()) != 1000023: continue
      m_neu = pp.m()
      leps_neu += get_children(pp)
      break
    for pp in p:
      m_ch = pp.m()
      if abs(pp.pdgId()) != 1000024: continue
      leps_ch += get_children(pp)
      break
    leps_Hplus = leps_neu + leps_ch

    for l in el:
      leps.append(l)
    for m in mu:
      leps.append(m)

    #DR between all lep combinations in event and DR between leading and other leps
    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt())) 
    if leps[0].pdgId() + leps[1].pdgId() == 0:
      DR.Fill(leps[0].p4().DeltaR(leps[1].p4()))
      DR_leading.Fill(leps[0].p4().DeltaR(leps[1].p4()))
    if leps[0].pdgId() + leps[2].pdgId() == 0:
      DR.Fill(leps[0].p4().DeltaR(leps[2].p4()))
      DR_leading.Fill(leps[0].p4().DeltaR(leps[2].p4()))
    if leps[1].pdgId() + leps[2].pdgId() == 0:
      DR.Fill(leps[1].p4().DeltaR(leps[2].p4()))
    
    for b in B:
      for l in leps:
        if b.p4().DeltaR(l.p4()) < .4:
          leps.remove(l)

    leps_Hplus = sorted(leps_Hplus, reverse = True, key=(lambda l: l.p4().Pt())) 
    leps_neu = sorted(leps_neu, reverse = True, key=(lambda l: l.p4().Pt())) 
    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt())) 
#    counter_total += 1
#    if len(leps_Hplus) < 3: continue
#    matched = False
#    for l in leps_ch:
#      print leps_Hplus[1].p4().DeltaR(l.p4())
#      if leps_Hplus[0].p4().DeltaR(l.p4()) < .05: matched = True
#    if matched:
#      leps_ch_matched.append(leps_Hplus[0])
#    if len(leps_ch_matched) == 1:
#      counter_ch_matched += 1 #x for binomial

    if len(leps) < 3: continue #3 or more leps
    leps = leps[:3]
#    if abs(leps[0].pdgId() + leps[1].pdgId() + leps[2].pdgId()) not in [11, 13]: continue #same flavor, opposite sign, and one of either flavor
#    if len(set([abs(leps[0].pdgId()), abs(leps[1].pdgId()), abs(leps[2].pdgId())])) != 2: continue #2 ossf, one of different flavor

#DR between the two leps from neutralino
    if leps_neu[0].pdgId() + leps_neu[1].pdgId() == 0:
      DR_neu.Fill(leps_neu[0].p4().DeltaR(leps_neu[1].p4()))

#DR between two leps from the neutralino and the one from the chargino
    if leps_neu[0].pdgId() + leps_ch[0].pdgId() == 0:
      DR_ch.Fill(leps_neu[0].p4().DeltaR(leps_ch[0].p4()))
    if leps_neu[1].pdgId() + leps_ch[0].pdgId() == 0:
      DR_ch.Fill(leps_neu[1].p4().DeltaR(leps_ch[0].p4()))

#DR between all the leps from H+ combinations
    if leps_Hplus[0].pdgId() + leps_Hplus[1].pdgId() == 0:
      DR_Hplus.Fill(leps_Hplus[0].p4().DeltaR(leps_Hplus[1].p4()))
      DR_leading_Hplus.Fill(leps_Hplus[0].p4().DeltaR(leps_Hplus[1].p4()))
    if leps_Hplus[0].pdgId() + leps_Hplus[2].pdgId() == 0:
      DR_Hplus.Fill(leps_Hplus[0].p4().DeltaR(leps_Hplus[2].p4()))
      DR_leading_Hplus.Fill(leps_Hplus[0].p4().DeltaR(leps_Hplus[2].p4()))
    if leps_Hplus[1].pdgId() + leps_Hplus[2].pdgId() == 0:
      DR_Hplus.Fill(leps_Hplus[1].p4().DeltaR(leps_Hplus[2].p4()))

#DR between all lep combinations in event
    if leps[0].pdgId() + leps[1].pdgId() == 0:
      DR_selection.Fill(leps[0].p4().DeltaR(leps[1].p4()))
      DR_leading_selection.Fill(leps[0].p4().DeltaR(leps[1].p4()))
    if leps[0].pdgId() + leps[2].pdgId() == 0:
      DR_selection.Fill(leps[0].p4().DeltaR(leps[2].p4()))
      DR_leading_selection.Fill(leps[0].p4().DeltaR(leps[2].p4()))
    if leps[1].pdgId() + leps[2].pdgId() == 0:
      DR_selection.Fill(leps[1].p4().DeltaR(leps[2].p4()))

  canvas = ROOT.TCanvas()
  legend = ROOT.TLegend(0.65,0.65,.981,0.78)
  legend2 = ROOT.TLegend(0.65,0.65,.981,0.78)
  if file == 0:
    legend.AddEntry(DR_Hplus, "Benchmark: m_{H+}=500GeV")
    legend2.AddEntry(DR_W, "Benchmark: m_{H+}=500GeV")
  if file == 1:
    legend.AddEntry(DR_Hplus, "Benchmark: m_{H+}=600GeV")
    legend2.AddEntry(DR_W, "Benchmark: m_{H+}=600GeV")
  if file == 2:
    legend.AddEntry(DR_Hplus, "Benchmark: m_{H+}=700GeV")
    legend2.AddEntry(DR_W, "Benchmark: m_{H+}=700GeV")
  if file == 3:
    legend.AddEntry(DR_Hplus, "Benchmark: m_{H+}=800GeV")
    legend2.AddEntry(DR_W, "Benchmark: m_{H+}=800GeV")
  if file == 4:
    legend.AddEntry(DR_Hplus, "Benchmark: m_{H+}=1000GeV")
  legend.AddEntry(DR, "Before Removal")
  legend.AddEntry(DR_selection, "After Removal")
  legend.AddEntry(DR_Hplus, "From H+")
  DR_Hplus.Draw("HIST")
  DR.Draw("HIST SAME")
  DR_selection.Draw("HIST SAME")
  DR.SetLineColor(2)
  DR_Hplus.SetLineColor(6)
  legend.Draw()
  canvas.Print("./plots/DR_check"+str(file)+".png")

  DR_leading_Hplus.Draw("HIST")
  DR_leading.Draw("HIST SAME")
  DR_leading_selection.Draw("HIST SAME")
  DR_leading.SetLineColor(2)
  DR_leading_Hplus.SetLineColor(6)
  legend.Draw()
  canvas.Print("./plots/DR_check_leading"+str(file)+".png")

  DR_W.Draw("HIST")
  legend2.Draw()
  canvas.Print("./plots/DR_check_W"+str(file)+".png")

  outputFile.Write()
print "Finished"