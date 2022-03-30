#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
from ROOT import std
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

#fileName = "/cluster/home/bburghgr/truth-hstaustau/daod/DAOD_TRUTH3.test.pool.root"
fileName_ttb = "/cluster/home/bburghgr/truth-ttb/mc16_13TeV.410470.PhPy8EG_A14_ttbar_hdamp258p75_nonallhad.deriv.DAOD_TRUTH1.e6337_p3401/DAOD_TRUTH1.13470208._000496.pool.root.1"
fileName_benchmark_500 = "/cluster/home/amyrewoldt/DAOD/3lep_slep_500/truth1/DAOD_TRUTH1.test.pool.root"
fileName_benchmark_600 = "/cluster/home/amyrewoldt/DAOD/3lep_slep_600/truth1/DAOD_TRUTH1.test.pool.root"
fileName_benchmark_700 = "/cluster/home/amyrewoldt/DAOD/3lep_slep_700/truth1/DAOD_TRUTH1.test.pool.root"
fileName_benchmark_800 = "/cluster/home/amyrewoldt/DAOD/3lep_slep_800/truth1/DAOD_TRUTH1.test.pool.root"
fileName_benchmark_1000 = "/cluster/home/amyrewoldt/DAOD/3lep_benchmark_Hplus1000_slep110/truth1/DAOD_TRUTH1.aod.pool.root"
fileName = [fileName_benchmark_500,fileName_benchmark_600,fileName_benchmark_700,fileName_benchmark_800,fileName_benchmark_1000,fileName_ttb]

#Function to follow decay chain to final product which are electrons or muons

def getChildren(particle):
  lep_list = []
  for i in range(particle.nChildren()):
    if particle.child(i).nChildren() == 0:
      if particle.child(i).absPdgId() in [11,13]:
        lep_list.append(particle.child(i))
    else:
      lep_list += getChildren(particle.child(i))
  return lep_list

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()
  outF = ROOT.TFile.Open("tree.root", "UPDATE")
  outTree = ROOT.TTree("T"+str(file), "Test TTree")

# Create vectors to store tlorentzvectors
#  ROOT.vector(ROOT.TLorentzVector)() == std::vector<TLorentzVector>()
  truth_leptons = ROOT.vector(ROOT.TLorentzVector)()
  neutralino_leptons = ROOT.vector(ROOT.TLorentzVector)()
  chargino_leptons = ROOT.vector(ROOT.TLorentzVector)()
  electrons = ROOT.vector(ROOT.TLorentzVector)()
  muons = ROOT.vector(ROOT.TLorentzVector)()
  jets = ROOT.vector(ROOT.TLorentzVector)()
  mets = ROOT.vector(ROOT.TLorentzVector)()
  pdgId_el = std.vector(int)()
  pdgId_mu = std.vector(int)()
  pdgId_truth = std.vector(int)()
  pdgId_neu = std.vector(int)()
  pdgId_ch = std.vector(int)()

# Create branches
  outTree.Branch("neutralino_leptons", neutralino_leptons)
  outTree.Branch("chargino_leptons", chargino_leptons)
  outTree.Branch("truth_leptons", truth_leptons)
  outTree.Branch("electrons_", electrons)
  outTree.Branch("muons_", muons)
  outTree.Branch("jets", jets)
  outTree.Branch("mets", mets)
  outTree.Branch("pdgId_el", pdgId_el)
  outTree.Branch("pdgId_mu", pdgId_mu)
  outTree.Branch("pdgId_truth", pdgId_truth)
  outTree.Branch("pdgId_neu", pdgId_neu)
  outTree.Branch("pdgId_ch", pdgId_ch)

  for entry in xrange(t.GetEntries()):
    t.GetEntry(entry)
    inTruth = t.TruthParticles
    inElectrons = t.TruthElectrons
    inMuons = t.TruthMuons
    inJets = t.AntiKt4TruthDressedWZJets
    inMets = t.MET_Truth
    neutralino_leptons.clear()
    chargino_leptons.clear()
    truth_leptons.clear()
    muons.clear()
    electrons.clear()
    jets.clear()
    mets.clear()
    pdgId_el.clear()
    pdgId_mu.clear()
    pdgId_truth.clear()
    pdgId_neu.clear()
    pdgId_ch.clear()
    neutralino_leps = []
    chargino_leps = []
    leps = []
    B = []

#   Do cuts and overlap removal here 
    for pp in inTruth:
      if pp.absPdgId() not in [5,511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]: continue
      B.append(pp)
      break
    for pp in inTruth:
      if pp.absPdgId() != 1000023: continue
      neutralino_leps += getChildren(pp)
      break
    for pp in inTruth:
      if pp.absPdgId() != 1000024: continue
      chargino_leps += getChildren(pp)
      break
    leps = chargino_leps + neutralino_leps
    for neu in neutralino_leps:
      neutralino_leptons.push_back(neu.p4())
      pdgId_neu.push_back(neu.pdgId())
    for ch in chargino_leps:
      chargino_leptons.push_back(ch.p4())
      pdgId_ch.push_back(ch.pdgId())
    for lep in leps:
      truth_leptons.push_back(lep.p4())
      pdgId_truth.push_back(lep.pdgId())

    for jet in inJets: jets.push_back(jet.p4())
    for met in inMets:
      mp4 = ROOT.TLorentzVector()
      mp4.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)
      mets.push_back(mp4)
    for el in inElectrons:
      for b in B:
        if b.p4().DeltaR(el.p4()) < .4: continue
        electrons.push_back(el.p4())
        pdgId_el.push_back(el.pdgId())
    for mu in inMuons:
      for b in B:
        if b.p4().DeltaR(mu.p4()) < .4: continue
        muons.push_back(mu.p4())
        pdgId_mu.push_back(mu.pdgId())
    outTree.Fill()
    print "DEBUG: Event", entry, "electrons:", len(electrons), "muons:", len(muons), "jets:", len(jets), "mets:", len(mets), "truth_leptons", len(truth_leptons), "pdgId", len(pdgId_el), len(pdgId_mu), len(pdgId_truth)
  outF.Write()
  outF.Close()
print "Finished"
