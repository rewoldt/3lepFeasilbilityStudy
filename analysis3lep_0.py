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
fileName_benchmark_500 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus500_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_600 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus600_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_700 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus700_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_800 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus800_slep110_Xn165_Xc120/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_1000 = "/cluster/home/amyrewoldt/DAOD/3lep_benchmark_Hplus1000_slep110/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_benchmark_1000_slep_110 = "/cluster/home/amyrewoldt/3lep_benchmark_Hplus1000_slep110/truth1/DAOD_TRUTH1.aod.pool.root"
fileName_summer_Dm_25 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_25/truth1/DAOD_TRUTH1.test.pool.root"
fileName_summer_Dm_50 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_50/truth1/DAOD_TRUTH1.test.pool.root"
fileName_summer_Dm_100 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_100/evgen/DAOD_TRUTH1.test.pool.root"
fileName_summer_Dm_200 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_200/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_1 = "/cluster/home/amyrewoldt/3lep_benchmark_Hplus800/truth1/DAOD_TRUTH1.test.pool.root"
#fileName_4 = "/cluster/home/amyrewoldt/3lep_benchmark_Hplus2000/truth1/DAOD_TRUTH1.aod.pool.root"
#fileName = [fileName_benchmark_500,fileName_benchmark_600,fileName_benchmark_700,fileName_benchmark_800,fileName_benchmark_1000,fileName_benchmark_1000_slep_110,fileName_summer_Dm_25,fileName_summer_Dm_50,fileName_summer_Dm_100,fileName_summer_Dm_200,fileName_ttb]
fileName = [fileName_benchmark_500,fileName_benchmark_600,fileName_benchmark_700,fileName_benchmark_800,fileName_benchmark_1000,fileName_ttb]#,fileName_benchmark_1000_slep_110]
#fileName = [fileName_benchmark_700,fileName_benchmark_800,fileName_benchmark_1000]

def declare_histos(histogram,name):
  for h in range(len(histogram)):
    for n in name:
      if '_ttbar' in fileName[file]:
        return ROOT.TH1F(str(histogram[:-5])+"_"+str(file)+"_ttb",name,71,0,300)
      else:
        return ROOT.TH1F(str(histogram[:-5])+"_"+str(file)+"_3lep",name,71,0,300)    
   
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

#def getParents(particle):
#  parents_list = []
#  if particle.absPdgId() not in [11,13]: continue
#  for i in range(particle.nParents()):
#    print "parent: ", particle.pdgId(), ", child particle: ", particle.child(i).pdgId(), ", mass: ", particle.child(i).m(), ", pt: ", particle.child(i).pt(), "\n"
#    print particle.parent(i).nParents() == 0:
#    if particle.parent(i).nParent() == 0:
#        parents_list.append(particle.parent(i))
#    else:
#      parents_list += getParents(particle.parent(i))
#  return list

def mllmax(m_neu,m_slep,m_lsp):
  mllmax = (pow(m_neu,2)-pow(m_slep,2))*(pow(m_slep,2)-pow(m_lsp,2))/pow(m_slep,2)
  return math.sqrt(mllmax)

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
  outputFile = ROOT.TFile.Open("histo.overlay.root", "UPDATE")
  #outputfile = ROOT.TFile.Open("histo.root", "UPDATE")

 ###################################
 # Begin Code for H+ TO 3LEP + MET #
 ###################################

  histograms = ["MET_3lep","visiblePt_3lep","visibleMt_3lep","Mt_3lep","ossfM_3lep","ossfPt_3lep","first_3lep","second_3lep","third_3lep"]
  names = ["Missing Transverse Momentum","Transverse Momentum of 3-lepton Final States","Visible Mass of 3-leptons in Final State","Transverse Mass + MET","OSSF Dilepton Mass","OSSF Dilepton Pt","Leading Lepton P_t","SubLeading Lepton P_t","Third Leading Lepton P_t"]
  for h in range(len(histograms)):
    histograms[h] = declare_histos(histograms[h],names[h])

#  MET = ROOT.TH1F("MET", "3l+MET Mt",71,0,1500)
#  MET_new = ROOT.TH1F("MET_new", "3l+MET Mt",71,0,1500)
#  MET_SUSY = ROOT.TH1F("MET_SUSY", "3l+MET Mt",71,0,1500)
#  MET_b4 = ROOT.TH1F("MET_b4", "3l+MET Mt",71,0,1500)
#  ossfM_3lep = ROOT.TH1F("ossfM_3lep", "Dilepton Mass",71,0,150)
#  ossfM_b4removal_3lep = ROOT.TH1F("ossfM_b4removal_3lep", "Dilepton Mass",71,0,150)
#  ossfM_neu_3lep = ROOT.TH1F("ossfM_neu_3lep", "Dilepton Mass",71,0,150)
#  ossfM_R_3lep = ROOT.TH1F("ossfM_R_3lep", "Dilepton Mass",71,0,150)
#  mllmax_hist = ROOT.TH1F("mllmax_hist", "Dilepton Mass",71,0,150)
  counter_ch_matched = 0
  event_counter = 0

# declare vectors lists and counters
  for entry in xrange(nevents):
    event_counter += 1
#    print "Event Number: ", event_counter
    t.GetEntry(entry)
    p = t.TruthParticles
    met = t.MET_Truth.at(0)
#    jet = t.AntiKt4TruthJets
    lepvector = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
    lepvector_b4 = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
    lepvector_new = ROOT.TLorentzVector(0,0,0,0) #TLorentzVector for all leps
    metvector = ROOT.TLorentzVector(0,0,0,0)
    metvector.SetPtEtaPhiM(met.met(), 0, met.phi(), 0)
    mu = t.TruthMuons
    el = t.TruthElectrons
    taus = t.TruthTaus
    leps_R = []
    leps_neu = []
    leps_ch = []
    leps = []
    leps_Hplus = []
    leps_matched = []
    leps_ch_matched = []
    B = []
    W = []
    leps_DR = []
    leps_b4_DR = []
    lsp = []
    leps_new = []
    
    #find relevant particles 
    for pp in p:
      if pp.absPdgId() not in [5,511,521,531,10511,10521,513,523,10513,10523,20513,20523,515,525,10531,533,10533,20533,535,541,10541,543,10543,20543,545]: continue
      B.append(pp)
      break
    for pp in p:
      if pp.absPdgId() != 2000013: continue
      leps_R += get_children(pp)
    for pp in p:
      if abs(pp.pdgId()) != 1000023: continue
      leps_neu += get_children(pp)
      m_neu = (pp.m()/1000)
      break
    for pp in p:
      if abs(pp.pdgId()) != 1000024: continue
      leps_ch += get_children(pp)
      break
    for pp in p:
      if pp.absPdgId() != 1000022: continue
      m_lsp = (pp.m()/1000)
      lsp.append(pp)
    for pp in p:
      if pp.absPdgId() != 1000011: continue
      m_slep = (pp.m()/1000)
    leps_Hplus = leps_neu + leps_ch
#    MET_SUSY.Fill((leps_Hplus[0].p4() + leps_Hplus[1].p4() + leps_Hplus[2].p4() + lsp[0].p4() + lsp[1].p4()).Mt()/1000)
#    mllmax_hist.Fill(mllmax(m_neu, m_slep, m_lsp))
    
    for l in el:
      leps.append(l)
    for m in mu:
      leps.append(m)

    for b in B:
      for l in leps:
        if l.p4().DeltaR(b.p4()) > .4: continue
        leps.remove(l)

#    matched = False
#    for l in leps_ch:
#      if leps_Hplus[2].p4().DeltaR(l.p4()) < .05: matched = True
#    if matched:
#      leps_ch_matched.append(leps_Hplus[2])
#    if len(leps_ch_matched) == 1:
#      counter_ch_matched += 1 #x for binomial

    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt()))
    if len(leps) < 3: continue
    for b in B:
      if leps[0].p4().DeltaR(b.p4()) > 2:
        leps.remove(leps[0])
      break
    leps_new += selectLeptons(leps)
    if len(leps_new) < 3: continue
#    print len(leps_new)
#    if abs(leps[0].pdgId() + leps[1].pdgId() + leps[2].pdgId()) not in [11, 13]: continue #same flavor, opposite sign, and one of either flavor
    leps_new = leps_new[:3]
#    if len(set([abs(leps[0].pdgId()), abs(leps[1].pdgId()), abs(leps[2].pdgId())])) != 2: continue #2 ossf, one of different flavor
    histograms[6].Fill(leps_new[0].p4().Pt()/1000)
    histograms[7].Fill(leps_new[1].p4().Pt()/1000)
    histograms[8].Fill(leps_new[2].p4().Pt()/1000)

    lepvector = leps_new[0].p4() + leps_new[1].p4() + leps_new[2].p4()
    histograms[0].Fill(metvector.Pt()/1000) #PT FROM MET 3LEP
    histograms[1].Fill(lepvector.Pt()/1000) #Pt of 3 leptons
    histograms[2].Fill(lepvector.M()/1000) #mass of 3 leptons
    histograms[3].Fill((lepvector + metvector).Mt()/1000) #met and pt_vis

#    if leps_neu[0].pdgId() + leps_neu[1].pdgId() == 0:
#      p4_neu = leps_neu[0].p4() + leps_neu[1].p4()
      #print "lep1 parent pdgId:", leps_neu[0].parent().pdgId(), "lep2 parent pdgId:", leps_neu[1].parent().pdgId()
#      ossfM_neu_3lep.Fill(p4_neu.M()/1000)

#    if leps_new[0].pdgId() + leps_new[1].pdgId() == 0: 
#      leps_DR.append(leps_new[0])
#      leps_DR.append(leps_new[1])
#    elif leps_new[0].pdgId() + leps_new[2].pdgId() == 0:
#      leps_DR.append(leps_new[0])
#      leps_DR.append(leps_new[2])
#    if len(leps_DR) != 2: continue
#    p4 = leps_DR[0].p4() + leps_DR[1].p4()
#    histograms[4].Fill(p4.M()/1000)
#    histograms[5].Fill(p4.Pt()/1000)

    for pair in [(0, 1), (0, 2), (1, 2)]:
#      print leps[pair[0]].pdgId() + leps[pair[1]].pdgId(), leps[pair[0]].pdgId()
      if leps_new[pair[0]].pdgId() + leps_new[pair[1]].pdgId() == 0: #if these two are same flavor op sign ex: -11 +11 
        if leps_new[pair[0]].p4().DeltaR(leps_new[pair[1]].p4()) > 1.6: continue
        p4 = leps_new[pair[0]].p4() + leps_new[pair[1]].p4()
#        if leps[pair[0]] not in leps_neu: continue
#        counter_pair += 1 
        histograms[4].Fill(p4.M()/1000)
        histograms[5].Fill(p4.Pt()/1000)
      break 

  #P = float(counter_ch_matched)/counter_total
  #C = math.factorial(counter_total)/(math.factorial(counter_ch_matched)*math.factorial(counter_total-counter_ch_matched))
  #Error = C*pow(P,counter_ch_matched)*pow((1-P),(counter_total-counter_ch_matched))*100
  #print "Percentage of 2 ossf leps from neutralino selected via lowest DR: ", float(counter_matched)/counter_total*100, "Probability of failure: ", (1-float(counter_matched)/counter_total)*100, "\n", "Probability leading lep is from chi_1^+: ", round(P*100,1), "+-", round(Error,1)

  canvas = ROOT.TCanvas()
  '''  legend = ROOT.TLegend(0.65,0.65,.981,0.78)
  if file == 0:
    legend.AddEntry(ossfM_neu_3lep, "Benchmark: m_{H+}=500GeV")
  if file == 1:
    legend.AddEntry(ossfM_neu_3lep, "Benchmark: m_{H+}=600GeV")
  if file == 2:
    legend.AddEntry(ossfM_neu_3lep, "Benchmark: m_{H+}=700GeV")
  if file == 3:
    legend.AddEntry(ossfM_neu_3lep, "Benchmark: m_{H+}=800GeV")
  if file == 4:
    legend.AddEntry(ossfM_neu_3lep, "Benchmark: m_{H+}=1000GeV")
  legend.AddEntry(ossfM_neu_3lep, "From Decay of X_{2}^{0~} with M() > 47")
  legend.AddEntry(ossfM_R_3lep, "From Decay of mu_{R}^{~}")
  #  legend.AddEntry(ossfM_3lep, "From Leps List")
  #  legend.AddEntry(ossfM_b4removal_3lep, "From Leps List (before B removal)")
  #  legend.AddEntry(MET_new, "From Leps List (with verified OSSF)")
  #  legend.AddEntry(mllmax_hist, "Calculated m_{llmax}")
  #  mllmax_hist.Draw("HIST")
  ossfM_neu_3lep.Draw("HIST")
  ossfM_R_3lep.Draw("HIST SAME")
  #  ossfM_3lep.Draw("HIST SAME")
  #  ossfM_b4removal_3lep.Draw("HIST SAME")
  ossfM_neu_3lep.SetLineColor(6)
  ossfM_R_3lep.SetLineColor(2)
  #  ossfM_b4removal_3lep.SetLineColor(2)
  #  ROOT.gPad.SetLogx()
  legend.Draw()
  canvas.Print("./plots/mllmax_"+str(file)+".png")
  MET_SUSY.Draw("HIST")
  MET_b4.Draw("HIST SAME")
  MET.Draw("HIST SAME")
  MET_b4.SetLineColor(2)
  MET_SUSY.SetLineColor(6)
  legend.Draw()
  canvas.Print("./plots/MET_"+str(file)+".png")'''
  outputFile.Write()
print "Finished"
