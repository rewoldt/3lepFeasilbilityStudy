#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

fileName = "~bburghgr/truth-ttb/mc16_13TeV.410470.PhPy8EG_A14_ttbar_hdamp258p75_nonallhad.deriv.DAOD_TRUTH1.e6337_p3401/DAOD_TRUTH1.13470208._000496.pool.root.1"
#fileName = "~bburghgr/truth-ttb/mc16_13TeV/DAOD_TRUTH1.13470217._000596.pool.root.1"

def declare_histos(histogram,name):
  for h in range(len(histogram)):
    for n in name:
      return ROOT.TH1F(str(histogram),n,50,0,500)    

f = ROOT.TFile.Open(fileName, "READONLY")
t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
print "Number of input events:", t.GetEntries()
#outputfile = ROOT.TFile.Open("histo.overlay.root", "RECREATE")
outputfile = ROOT.TFile.Open("histo.overlay.root", "UPDATE")

 ######################
 # Begin Code for ttb #
 ######################

histograms = ["MET_ttb","visiblePt_ttb","visibleMt_ttb","Mt_ttb","ossfM_ttb","ossfPt_ttb","first_ttb","second_ttb","third_ttb"]
names = ["Missing Transverse Momentum","Transverse Momentum of 3-lepton Final States","Transverse Mass of 3-leptons Final States","OSSF Dilepton Mass","OSSF Dilepton Pt","Leading Lepton P_t","SubLeading Lepton P_t","Third Leading Lepton P_t"]
for h in range(len(histograms)):
  histograms[h] = declare_histos(histograms[h],names)

for entry in xrange(t.GetEntries()):
  t.GetEntry(entry)
  p = t.TruthParticles
  met = t.MET_Truth.at(0)
  jet = t.AntiKt4TruthDressedWZJets
  lepvector = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
  metvector = ROOT.TLorentzVector(0,0,0,0)
  metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)
  mu = t.TruthMuons
  el = t.TruthElectrons

  leps = []
  for m in mu:
    leps.append(m)
  for e in el:
    leps.append(e)

  leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt()))    
  if len(leps) < 3: continue
  if abs(leps[0].pdgId() + leps[1].pdgId() + leps[2].pdgId()) not in [11, 13]: continue 
  if len(set([abs(leps[0].pdgId()), abs(leps[1].pdgId()), abs(leps[2].pdgId())])) != 2: continue
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
outputfile.Write()
print "Finished"
