#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )
ROOT.gStyle.SetOptStat(0)
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
  return_list = []
  for i in range(particle.nChildren()):
#    print "parent: ", particle.pdgId(), ", child particle: ", particle.child(i).pdgId(), ", mass: ", particle.child(i).m(), ", pt: ", particle.child(i).pt(), "\n"
    if particle.child(i).nChildren() == 0:
      if particle.child(i).absPdgId() in [11,13]:
        return_list.append(particle.child(i))
    else:
      return_list += get_children(particle.child(i))
  return return_list

def getParents(particle):
  return_list = []
  for i in range(particle.nParents()):
    if particle.parent(i).pdgId() != particle.pdgId():
      return_list.append(particle.parent(i))
    else:
      return_list += getParents(particle.parent(i))
  return return_list

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

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()
  nevents = t.GetEntries()
  outputFile = ROOT.TFile.Open("histo.root", "UPDATE")

 ###################################
 # Begin Code for H+ TO 3LEP + MET #
 ###################################
  event_counter = 0 
  counter_total = 0
  counter_matched = 0
  counter_B = 0
  counter_W = 0
  counter_other = 0

  DR_leadingHvH = ROOT.TH1F("DR_leadingHvH", "DR between Leading Leptons",60,0,10)
  DR_leadingHvB = ROOT.TH1F("DR_leadingHvB", "DR between Leading Leptons",60,0,10)
  DR_leadingHvW = ROOT.TH1F("DR_leadingHvW", "DR between Leading Leptons",60,0,10)
  DR_subleadingvleadingHvH = ROOT.TH1F("DR_subleadingvleadingHvH", "DR between Leading Lepton (H+) & Subleading Lepton",61,0,7)
  DR_subleadingvleadingHvB = ROOT.TH1F("DR_subleadingvleadingHvB", "DR between Leading Lepton (H+) & Subleading Lepton",43,0,7)
  DR_subleadingvleadingHvW = ROOT.TH1F("DR_subleadingvleadingHvW", "DR between Leading Lepton (H+) & Subleading Lepton",43,0,7)
  DR_thirdvleadingHvH = ROOT.TH1F("DR_thirdvleadingHvH", "DR between Leading Lepton (H+) & Third",61,0,7)
  DR_thirdvleadingHvB = ROOT.TH1F("DR_thirdvleadingHvB", "DR between Leading Lepton (H+) & Third",43,0,7)
  DR_thirdvleadingHvW = ROOT.TH1F("DR_thirdvleadingHvW", "DR between Leading Lepton (H+) & Third",43,0,7)
  DR_BvslepfromW = ROOT.TH1F("DR_thirdvleadingHvW", "DR Overlay",120,0,10)
  DR_Hplus = ROOT.TH1F("DR_Hplus", "DR Overlay", 120,0,10)

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
    leps_matched = []
    B = []
    leps_all = []
    leps_notHplus =  []
    parent_first = []
    parent_second = []
    parent_third = []
    leading_B = []
    leading_W = []
    leading_H = []
    subleading_B = []
    subleading_W = []
    subleading_H = []
    third_B = []
    third_W = []
    third_H = []
    lep_from_W = []
    test = []

    for pp in p:
      if pp.absPdgId() != 5: continue
      B.append(pp)
    for pp in p:
      leps_all += get_children(pp)
      break
    for l in el:
      leps.append(l)
    for m in mu:
      leps.append(m)

    for pp in p:
      if abs(pp.pdgId()) != 1000023: continue
      leps_neu += get_children(pp)
      break
    for pp in p:
      if abs(pp.pdgId()) != 1000024: continue
      leps_ch += get_children(pp)
      break
    leps_Hplus = leps_neu + leps_ch

#    for b in B:
#      for l in leps:
#        if l.p4().DeltaR(b.p4()) < .4:
#          leps.remove(l)

    leps_Hplus = sorted(leps_Hplus, reverse = True, key=(lambda l: l.p4().Pt()))
    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt())) 
    leps_all = sorted(leps_all, reverse = True, key=(lambda l: l.p4().Pt()))
    if len(leps) < 3: continue
    if len(leps_all) < 3: continue
    for la in leps_all[:3]:
      for l in leps[:3]:
        if l.p4().DeltaR(la.p4()) < .05:
          test.append(la)
    test = sorted(test, reverse = True, key=(lambda l: l.p4().Pt()))
    if len(test) != 3: continue
    parent_first += getParents(test[0])
    parent_second += getParents(test[1])
    parent_third += getParents(test[2])
    all_parents = parent_first + parent_second + parent_third
    counter_total += 1

    for par in all_parents:
      if par.absPdgId() != 24: continue
      lep_from_W.append(par)
      break

    for lep in range(len(lep_from_W)):
      for b in range(len(B)):
        DR_BvslepfromW.Fill(lep_from_W[lep].p4().DeltaR(B[b].p4()))
      break

    if parent_first[0].absPdgId() in [1000024,1000023,1000011,2000013] and parent_second[0].absPdgId() in [1000024,1000023,1000011,2000013]:
      DR_subleadingvleadingHvH.Fill(test[0].p4().DeltaR(test[1].p4()))
    if parent_first[0].absPdgId() in [1000024,1000023,1000011,2000013] and parent_second[0].absPdgId() in [5,511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]:
      DR_subleadingvleadingHvB.Fill(test[0].p4().DeltaR(test[1].p4()))
    if parent_first[0].absPdgId() in [1000024,1000023,1000011,2000013] and parent_second[0].absPdgId() == 24:
      DR_subleadingvleadingHvW.Fill(test[0].p4().DeltaR(test[1].p4()))
        
    if parent_first[0].absPdgId() in [1000024,1000023,1000011,2000013] and parent_third[0].absPdgId() in [1000024,1000023,1000011,2000013]:
      DR_Hplus.Fill(test[0].p4().DeltaR(test[2].p4()))
      DR_thirdvleadingHvH.Fill(test[0].p4().DeltaR(test[2].p4()))
    if parent_first[0].absPdgId() in [1000024,1000023,1000011,2000013] and parent_third[0].absPdgId() in [5,511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]:
      DR_thirdvleadingHvB.Fill(test[0].p4().DeltaR(test[2].p4()))
    if parent_first[0].absPdgId() in [1000024,1000023,1000011,2000013] and parent_third[0].absPdgId() == 24:
      DR_thirdvleadingHvW.Fill(test[0].p4().DeltaR(test[2].p4()))
#    if parent_second[0].absPdgId() in [1000024,1000023,1000011,2000013]:
#    if parent_third[0].absPdgId() in [1000024,1000023,1000011,2000013]:
#      counter_matched += 1
#    if parent_second[0].absPdgId() in [1000024,1000023,1000011,2000013] and parent_third[0].absPdgId() in [1000024,1000023,1000011,2000013]:
#      DR_Hplus.Fill(test[1].p4().DeltaR(test[2].p4()))
    elif parent_first[0].absPdgId() in [5,511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]:
#    elif parent_second[0].absPdgId() in [5,511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]:
#    elif parent_third[0].absPdgId() in [5,511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]:
      counter_B += 1
    elif parent_first[0].absPdgId() == 24:
#    elif parent_second[0].absPdgId() == 24:
#    elif parent_third[0].absPdgId() == 24:
      counter_W += 1
    else:
      counter_other += 1

#    if len(leps) < 3: continue
#    matched = False
#    for l in leps_notHplus:
#      print "DR: ", leps[0].p4().DeltaR(l.p4())
#      if leps[0].p4().DeltaR(l.p4()) < .05: matched = True
#    if matched:
#      leps_matched.append(leps[0])
#    print len(leps_matched)
#    if len(leps_matched) == 1:
#      counter_matched += 1 #x for binomial

  canvas = ROOT.TCanvas()
#  legend = ROOT.TLegend(0.65,0.65,.981,0.78)
  legend = ROOT.TLegend(.7,.7,.9,.9)
  legendmod = ROOT.TLegend(0.65,0.65,.981,0.75)
  if file == 0:
    legendmod.AddEntry(DR_leadingHvH, "Benchmark: m_{H+}=500GeV")
  if file == 1:
    legendmod.AddEntry(DR_leadingHvH, "Benchmark: m_{H+}=600GeV")
  if file == 2:
    legendmod.AddEntry(DR_leadingHvH, "Benchmark: m_{H+}=700GeV")
  if file == 3:
    legendmod.AddEntry(DR_leadingHvH, "Benchmark: m_{H+}=800GeV")
  if file == 4:
    legendmod.AddEntry(DR_leadingHvB, "Benchmark: m_{H+}=1000GeV")
  legend.AddEntry(DR_leadingHvH, "between H+ and H+")
  legend.AddEntry(DR_leadingHvB, "between H+ and B")
  legend.AddEntry(DR_leadingHvW, "between H+ and W")
  DR_leadingHvH.Draw("HIST")
  DR_leadingHvB.Draw("HIST SAME")
  DR_leadingHvW.Draw("HIST SAME")
  DR_leadingHvB.SetLineColor(2)
  DR_leadingHvW.SetLineColor(6)
  legend.Draw()
  canvas.Print("./plots/DR_leading"+str(file)+".png")

  if DR_subleadingvleadingHvH.Integral() != 0:
    DR_subleadingvleadingHvH.Scale(1/(0.064596*DR_subleadingvleadingHvH.Integral()))
  if DR_subleadingvleadingHvB.Integral() != 0:
    DR_subleadingvleadingHvB.Scale(1/(.0841*DR_subleadingvleadingHvB.Integral()))
  if DR_subleadingvleadingHvW.Integral() != 0:
    DR_subleadingvleadingHvW.Scale(1/(.10596*DR_subleadingvleadingHvW.Integral()))
  DR_subleadingvleadingHvB.Draw("HIST")
  DR_subleadingvleadingHvW.Draw("HIST SAME")
  DR_subleadingvleadingHvH.Draw("HIST SAME")
  DR_subleadingvleadingHvB.SetLineColor(2)
  DR_subleadingvleadingHvW.SetLineColor(6)
  legend.Draw()
  canvas.Print("./plots/DR_leadingvsubleading"+str(file)+".png")

  if DR_thirdvleadingHvH.Integral() != 0:
    DR_thirdvleadingHvH.Scale(1/(0.064596*DR_thirdvleadingHvH.Integral()))
  if DR_thirdvleadingHvB.Integral() != 0:
    DR_thirdvleadingHvB.Scale(1/(.0841*DR_thirdvleadingHvB.Integral()))
  if DR_thirdvleadingHvW.Integral() != 0:
    DR_thirdvleadingHvW.Scale(1/(.10596*DR_thirdvleadingHvW.Integral()))
  DR_thirdvleadingHvW.Draw("HIST")
  DR_thirdvleadingHvB.Draw("HIST SAME")
  DR_thirdvleadingHvH.Draw("HIST SAME")
  DR_thirdvleadingHvB.SetLineColor(2)
  DR_thirdvleadingHvW.SetLineColor(6)
  legend.Draw()
  canvas.Print("./plots/DR_leadingvthird"+str(file)+".png")

  legendmod.AddEntry(DR_BvslepfromW, "between leading from H+ & other 2 from H+")
  legendmod.AddEntry(DR_Hplus, "between leptons from W and B-quark")
  DR_BvslepfromW.Draw("HIST")
  DR_Hplus.Draw("HIST SAME")
  DR_Hplus.SetLineColor(2)
  DR_BvslepfromW.SetLineColor(9)
  legendmod.Draw()  
  canvas.Print("./plots/DR_BvslepfromWandHplusoverlay"+str(file)+".png")
  
  print "From H+:", round(float(counter_matched)/counter_total*100, 2), "From B:", round(float(counter_B)/counter_total*100, 2), "From W:", round(float(counter_W)/counter_total*100, 2), "From other:", round(float(counter_other)/counter_total*100, 2)
  P = float(counter_matched)/counter_total
  C = math.factorial(counter_total)/(math.factorial(counter_matched)*math.factorial(counter_total-counter_matched))
  Error = C*pow(P,counter_matched)*pow((1-P),(counter_total-counter_matched))*100
  print "Percentage 2nd highest pt lepton is from B: ", P*100, "Probability of failure: ", (1-P)*100, "\n", "Probability 2nd leading lep is from B: ", round(P*100,2), "+-", round(Error,2)
  outputFile.Write()
print "Finished"
