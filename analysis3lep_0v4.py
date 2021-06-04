#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )
ROOT.gStyle.SetOptStat(1)
import math

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

#define DAOD files and put them in list
fileName_ttb = "/cluster/home/bburghgr/truth-ttb/mc16_13TeV.410470.PhPy8EG_A14_ttbar_hdamp258p75_nonallhad.deriv.DAOD_TRUTH1.e6337_p3401/DAOD_TRUTH1.13470208._000496.pool.root.1"
fileName_benchmark_500 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus500_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_600 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus600_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_700 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus700_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_800 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus800_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_1000 = "/cluster/home/amyrewoldt/DAOD/3lep_benchmark_Hplus1000_slep110/truth1/DAOD_TRUTH1.aod.pool.root"
fileName = [fileName_benchmark_500,fileName_benchmark_600,fileName_benchmark_700,fileName_benchmark_800,fileName_benchmark_1000]

#Function to follow decay chain to final product which are electrons or muons
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
  print "Number of input events:", t.GetEntries()
  nevents = t.GetEntries()
  outputFile = ROOT.TFile.Open("histo.overlay.root", "UPDATE")

 ###################################
 # Begin Code for H+ TO 3LEP + MET #
 ###################################

#Declare histograms
  MET = ROOT.TH1F("MET", "3l+MET Mt",71,0,1500)
  MET_b4 = ROOT.TH1F("MET_b4", "3l+MET Mt",71,0,1500)
  MET_new = ROOT.TH1F("MET_new", "3l+MET Mt",71,0,1500)
  ossfM_3lep = ROOT.TH1F("ossfM_3lep", "Dilepton Mass",71,0,300)
  ossfM_b4removal_3lep = ROOT.TH1F("ossfM_b4removal_3lep", "Dilepton Mass",71,0,300)
  ossfM_new_3lep = ROOT.TH1F("ossfM_new_3lep", "Dilepton Mass",71,0,300)
  event_counter = 0

#Loop through events
  for entry in xrange(5000):
    event_counter += 1
#    print "Event Number: ", event_counter
    t.GetEntry(entry)
    p = t.TruthParticles
    met = t.MET_Truth.at(0)
    lepvector = ROOT.TLorentzVector(0,0,0,0)
    lepvector_b4 = ROOT.TLorentzVector(0,0,0,0)
    lepvector_new = ROOT.TLorentzVector(0,0,0,0)
    metvector = ROOT.TLorentzVector(0,0,0,0)
    metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)
    mu = t.TruthMuons
    el = t.TruthElectrons
    leps_neu = []
    leps_ch = []
    leps = []
    leps_Hplus = []
    B = []
    leps_DR = []
    leps_b4_DR = []

    for pp in p:
      if pp.absPdgId() not in [5,511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]: continue
      B.append(pp)
    for l in el:
      leps.append(l)
    for m in mu:
      leps.append(m)

    for b in B:
      for l in leps:
        if l.p4().DeltaR(b.p4()) < .4:
          leps.remove(l)

    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt()))
    if len(leps) < 3: continue
    lepvector = leps[0].p4() + leps[1].p4() + leps[2].p4()
    MET.Fill((lepvector + metvector).Mt()/1000)
    if leps[0].p4().DeltaR(leps[1].p4()) < leps[0].p4().DeltaR(leps[2].p4()):
      if leps[0].pdgId() + leps[1].pdgId() != 0: continue
      leps_DR.append(leps[0])
      leps_DR.append(leps[1])
    else:
      if leps[0].pdgId() + leps[2].pdgId() != 0: continue
      leps_DR.append(leps[0])
      leps_DR.append(leps[2])
    p4 = leps_DR[0].p4() + leps_DR[1].p4()
    ossfM_3lep.Fill(p4.M()/1000)

  canvas = ROOT.TCanvas()
  legend = ROOT.TLegend(0.65,0.65,.981,0.78)
  if file == 0:
    legend.AddEntry(ossfM_3lep, "Benchmark: m_{H+}=500GeV")
  if file == 1:
    legend.AddEntry(ossfM_3lep, "Benchmark: m_{H+}=600GeV")
  if file == 2:
    legend.AddEntry(ossfM_3lep, "Benchmark: m_{H+}=700GeV")
  if file == 3:
    legend.AddEntry(ossfM_3lep, "Benchmark: m_{H+}=800GeV")
  if file == 4:
    legend.AddEntry(ossfM_3lep, "Benchmark: m_{H+}=1000GeV")
  ossfM_3lep.Draw("HIST")
  legend.Draw()
  canvas.Print("./plots/mllmax_"+str(file)+".png")
  MET.Draw("HIST")
  legend.Draw()
  canvas.Print("./plots/MET_"+str(file)+".png")
  outputFile.Write()
print "Finished"
