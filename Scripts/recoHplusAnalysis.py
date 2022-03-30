#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

fileName_1 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_25/aod/aod.root"
fileName_2 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_50/aod/aod.root"
fileName_3 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_100/aod/aod.root"
fileName_4 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_200/aod/aod.root"
fileName_5 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_400/aod/aod.root"
#fileName_ttb = "~bburghgr/truth-ttb/mc16_13TeV.410470.PhPy8EG_A14_ttbar_hdamp258p75_nonallhad.deriv.DAOD_TRUTH1.e6337_p3401/DAOD_TRUTH1.13470208._000496.pool.root.1"
fileName = [fileName_1,fileName_2,fileName_3,fileName_4]

def pdgId(p):
  if type(p) == ROOT.xAOD.Muon_v1: return -13*p.charge()
  if type(p) == ROOT.xAOD.Electron_v1: return -11*p.charge()
  assert False

def declare_histos(histograms,name):
  for h in range(len(histograms)):
    for n in name:
      return ROOT.TH1F(str(histograms[:-5])+"_"+str(file)+"_3lep",n,50,0,1000)    

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()
  nevents = t.GetEntries()
  outputFile = ROOT.TFile.Open("histo.overlay.root", "UPDATE")
  histograms = ["MET_3lep","visiblePt_3lep","visibleMt_3lep","Mt_3lep","ossfM_3lep","ossfPt_3lep","first_3lep","second_3lep","third_3lep"]
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
    mu_tr = t.MuonTruthParticles
    el_tr = t.egammaTruthParticles
    mu = t.Muons
    el = t.Electrons

    leps_tr = []
    leps = []
    for m in mu_tr:
      leps_tr.append(m)
    for e in el_tr:
      leps_tr.append(e)    

    for m in mu:
      if m.quality() != 1: continue
      if m.pt() < 5000: continue
      if abs(m.eta()) > 2.47: continue
      leps.append(m)
    for e in el:
      if e.passSelection("LHMedium"):
        if e.pt() < 5000: continue
        if abs(e.eta()) > 2.47: continue
        leps.append(e)

    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt()))
    leps_tr = sorted(leps_tr, reverse = True, key=(lambda l: l.p4().Pt()))
    if len(leps) < 3: continue
    if abs(sum(map(pdgId, leps[:3]))) not in [11,13]: continue
    if len(set([abs(pdgId(leps[0])), abs(pdgId(leps[1])), abs(pdgId(leps[2]))])) != 2: continue #two same flavor

    lepvector = leps[0].p4() + leps[1].p4() + leps[2].p4()
    histograms[0].Fill(metvector.Pt()/1000) #PT FROM MET 3LEP
    histograms[1].Fill(lepvector.Pt()/1000) #mass of 3 leptons in decay chain
    histograms[2].Fill(lepvector.M()/1000) #mass of 3 leptons in decay chain
    histograms[3].Fill((lepvector + metvector).Mt()/1000)
    histograms[6].Fill(leps[0].p4().Pt()/1000)
    histograms[7].Fill(leps[1].p4().Pt()/1000)
    histograms[8].Fill(leps[2].p4().Pt()/1000)
 
    for pair in [(0, 1), (0, 2), (1, 2)]:
      if pdgId(leps[pair[0]]) + pdgId(leps[pair[1]]) == 0:
        p4 = leps[pair[0]].p4() + leps[pair[1]].p4()
      histograms[4].Fill(p4.M()/1000)
      histograms[5].Fill(p4.Pt()/1000)
      break

  canvas = ROOT.TCanvas()
  outputFile.Write()
print "Finished"
