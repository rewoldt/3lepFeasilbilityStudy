#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

fileName_Hplus500 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus500_slep110_Xn165_Xc120/reco/aod.merge.root"
fileName_Hplus600 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus600_slep110_Xn165_Xc120/reco/aod.merge.root"
fileName_Hplus700 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus700_slep110_Xn165_Xc120/reco/aod.merge.root"
fileName_Hplus800 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus800_slep110_Xn165_Xc120/reco/aod.merge.root"
#fileName_Hplus1000 = "/cluster/home/amyrewoldt/DAOD/3lep_benchmark_Hplus1000_slep110/reco/aod.merge.root"
fileName = [fileName_Hplus500,fileName_Hplus600,fileName_Hplus700,fileName_Hplus800]

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

def pdgId(p):
  if type(p) == ROOT.xAOD.Muon_v1: return -13*p.charge()
  if type(p) == ROOT.xAOD.Electron_v1: return -11*p.charge()
  assert False

def selectLeptons_reco(leps):
  first = leps[0]
  best = None
  for lep in leps[1:]:
    if pdgId(first) + pdgId(lep) != 0: continue
    if best == None: best = lep
    if first.p4().DeltaR(lep.p4()) < first.p4().DeltaR(best.p4()): best = lep
  sel = [first, best]
  for lep in leps:
    if lep in sel: continue
    sel.append(lep)
    break
  return sel

def selectLeptons(leps):
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

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()
  nevents = t.GetEntries()
  outputFile = ROOT.TFile.Open("histo.overlay.root", "UPDATE")

  DR = ROOT.TH1F("DR", "DR Between all Lepton Combinations with OSSF (excluding leps from B) in event ",71,0,5)
  MET = ROOT.TH1F("MET", "3l+MET Mt",70,0,1500)
  MET_reco = ROOT.TH1F("MET_reco", "3l+MET Mt",70,0,1500)
  MET_b4 = ROOT.TH1F("MET_b4", "3l+MET Mt",70,0,1500)
  MET_b4_reco = ROOT.TH1F("MET_b4_reco", "3l+MET Mt",70,0,1500)
  ossfM = ROOT.TH1F("ossfM", "Dilepton Mass",71,0,300)
  ossfM_b4 = ROOT.TH1F("ossfM_b4", "Dilepton Mass",71,0,300)
  ossfM_b4_reco = ROOT.TH1F("ossfM_b4_reco", "Dilepton Mass",71,0,300)
  ossfM_reco = ROOT.TH1F("ossfM_reco", "Dilepton Mass",71,0,300)

  for entry in xrange(500):
    t.GetEntry(entry)
    p = t.TruthParticles
    met = t.MET_Truth.at(0)
    jet = t.AntiKt4EMTopoJets
    bjet = t.BTagging_AntiKt4EMTopo
    lepvector = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
    lepvector_b4 = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
    lepvector_b4_reco = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
    lepvector_tr = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps    
    metvector = ROOT.TLorentzVector(0,0,0,0)
    metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)
    mu_tr = t.MuonTruthParticles
    el_tr = t.egammaTruthParticles
    mu = t.Muons
    el = t.Electrons
    leps = []
    leps_tr = []
    B = []
    leps_DR = []
    leps_DR_tr = []
    leps_b4_DR = []
    leps_b4reco_DR = []
    B_jets = []
    leps_new = []
    leps_new_tr = []

#BODY
#truth B
    for pp in p:
      if pp.absPdgId() not in [511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]: continue
      B.append(pp)

    for j in jet:
      for b in B:
        if j.p4().DeltaR(b.p4()) > .4: continue
        B_jets.append(j)
        DR.Fill(j.p4().DeltaR(b.p4()))

#reconstructed leps
    for mt in mu_tr:
      leps_tr.append(mt)
      for m in mu:
        if m.p4().DeltaR(mt.p4()) > .05: continue
        leps.append(m)
    for et in el_tr:
      leps_tr.append(et)
      for e in el:
        if e.p4().DeltaR(et.p4()) > .05: continue
        leps.append(e)

    leps_tr = sorted(leps_tr, reverse = True, key=(lambda l: l.p4().Pt()))
    if len(leps_tr) < 3: continue
    lepvector_b4 = leps_tr[0].p4() + leps_tr[1].p4() + leps_tr[2].p4()
    if leps_tr[0].p4().DeltaR(leps_tr[1].p4()) < leps_tr[0].p4().DeltaR(leps_tr[2].p4()):
      if leps_tr[0].pdgId() + leps_tr[1].pdgId() != 0: continue
      leps_b4_DR.append(leps_tr[0])
      leps_b4_DR.append(leps_tr[1])
    else:
      if leps_tr[0].pdgId() + leps_tr[2].pdgId() != 0: continue
      leps_b4_DR.append(leps_tr[0])
      leps_b4_DR.append(leps_tr[2])
    p4_b4 = leps_b4_DR[0].p4() + leps_b4_DR[1].p4()
    ossfM_b4.Fill(p4_b4.M()/1000)
    MET_b4.Fill((lepvector_b4 + metvector).Mt()/1000)

    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt())) 
    if len(leps) < 3: continue
    lepvector_b4_reco = leps[0].p4() + leps[1].p4() + leps[2].p4()
    if leps[0].p4().DeltaR(leps[1].p4()) < leps[0].p4().DeltaR(leps[2].p4()):
      if pdgId(leps[0]) + pdgId(leps[1]) != 0: continue
      leps_b4reco_DR.append(leps[0])
      leps_b4reco_DR.append(leps[1])
    else:
      if pdgId(leps[0]) + pdgId(leps[2]) != 0: continue
      leps_b4reco_DR.append(leps[0])
      leps_b4reco_DR.append(leps[2])
    p4_b4_reco = leps_b4reco_DR[0].p4() + leps_b4reco_DR[1].p4()
    ossfM_b4_reco.Fill(p4_b4_reco.M()/1000)
    MET_b4_reco.Fill((lepvector_b4_reco + metvector).Mt()/1000)

    for b in B_jets:
      for l in leps_tr:
        if l.p4().DeltaR(b.p4()) > .4: continue
        leps_tr.remove(l)

    for b in B_jets:
      for l in leps:
        if l.p4().DeltaR(b.p4()) > .4: continue
        leps.remove(l)

    if len(leps_tr) < 3: continue
    leps_new_tr += selectLeptons(leps_tr)
    if None in leps_new_tr: continue
    if len(leps_new_tr) < 3: continue
    lepvector_tr = leps_new_tr[0].p4() + leps_new_tr[1].p4() + leps_new_tr[2].p4()
    if leps_tr[0].pdgId() + leps_tr[1].pdgId() == 0:
      leps_DR_tr.append(leps_tr[0])
      leps_DR_tr.append(leps_tr[1])
    else:
      leps_DR_tr.append(leps_tr[0])
      leps_DR_tr.append(leps_tr[2])
    p4_tr = leps_DR_tr[0].p4() + leps_DR_tr[1].p4()
    ossfM.Fill(p4_tr.M()/1000)
    MET.Fill((lepvector_tr + metvector).Mt()/1000) #met and pt_vis

    if len(leps) < 3: continue 
    leps_new += selectLeptons_reco(leps)
    if None in leps_new: continue
    if len(leps_new) < 3: continue
    lepvector = leps_new[0].p4() + leps_new[1].p4() + leps_new[2].p4()
    if pdgId(leps_new[0]) + pdgId(leps_new[1]) == 0:
      leps_DR.append(leps_new[0])
      leps_DR.append(leps_new[1])
    else:
      leps_DR.append(leps_new[0])
      leps_DR.append(leps_new[2])
    p4 = leps_DR[0].p4() + leps_DR[1].p4()
    ossfM_reco.Fill(p4.M()/1000)
    MET_reco.Fill((lepvector + metvector).Mt()/1000) #met and pt_vis

  canvas = ROOT.TCanvas()
  legend = ROOT.TLegend(0.65,0.65,.981,0.78)
  legend2 = ROOT.TLegend(0.65,0.65,.981,0.78)
  if file == 0:
    legend.AddEntry(ossfM, "Benchmark: m_{H+}=500GeV")
  if file == 1:
    legend.AddEntry(ossfM, "Benchmark: m_{H+}=600GeV")
  if file == 2:
    legend.AddEntry(ossfM, "Benchmark: m_{H+}=700GeV")
  if file == 3:
    legend.AddEntry(ossfM, "Benchmark: m_{H+}=800GeV")
  if file == 0:
    legend2.AddEntry(MET, "Benchmark: m_{H+}=500GeV")
  if file == 1:
    legend2.AddEntry(MET, "Benchmark: m_{H+}=600GeV")
  if file == 2:
    legend2.AddEntry(MET, "Benchmark: m_{H+}=700GeV")
  if file == 3:
    legend2.AddEntry(MET, "Benchmark: m_{H+}=800GeV")
  DR.Draw("HIST")
  legend.Draw()
  canvas.Print("./plots/DR_"+str(file)+".png")
  legend.AddEntry(ossfM, "From Leps List (truth)")
  legend.AddEntry(ossfM_b4, "From Leps List before B Removal and selection (truth)")
  legend.AddEntry(ossfM_reco, "From Leps List (reconstruction)")
  legend.AddEntry(ossfM_b4_reco, "From Leps List before B removal and selection (reconstruction)")
  legend2.AddEntry(MET, "From Leps List (truth)")
  legend2.AddEntry(MET_b4, "From Leps List before B Removal and selection (truth)")
  legend2.AddEntry(MET_reco, "From Leps List (reconstruction)")
  legend2.AddEntry(MET_b4_reco, "From Leps List before B Removal and selection (reconstruction)")
  ROOT.gPad.SetLogy()
  MET_b4.Draw("HIST")
  MET_b4_reco.Draw("HIST SAME")
  MET_reco.Draw("HIST SAME")
  MET.Draw("HIST SAME")
  MET_b4.SetLineColor(2)
  MET_reco.SetLineColor(8)
  MET_b4_reco.SetLineColor(6)
  legend2.Draw()
  canvas.Print("./plots/MET_reco_"+str(file)+".png")
  ossfM_b4.Draw("HIST")
  ossfM_b4_reco.Draw("HIST SAME")
  ossfM.Draw("HIST SAME")
  ossfM_reco.Draw("HIST SAME")
  ossfM_b4.SetLineColor(2)
  ossfM_reco.SetLineColor(8)
  ossfM_b4_reco.SetLineColor(6)
  legend.Draw()
  canvas.Print("./plots/ossf_reco_"+str(file)+".png")
  outputFile.Write()
print "Finished"