#!/usr/bin/env python2.7

# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

fileName_1 = "/cluster/home/amyrewoldt/DAOD/3lep_750Hplus25Split/aod/aod.root"
fileName_2 = "/cluster/home/amyrewoldt/DAOD/3lep_750Hplus50Split/aod/aod.root"
fileName_3 = "/cluster/home/amyrewoldt/DAOD/3lep_750Hplus100Split/aod/aod.root"
fileName_4 = "/cluster/home/amyrewoldt/DAOD/3lep_750Hplus200Split/aod/aod.root"
fileName_5 = "/cluster/home/amyrewoldt/DAOD/3lep_Hplus_xn_400/truth1/DAOD_TRUTH1.test.pool.root"
fileName = [fileName_1,fileName_2,fileName_3,fileName_4]

def get_mother(particle):
  if abs(particle.pdgId()) in [1000023,1000024]: 
    return particle
  elif particle.nParents() != 1: 
    return None
  else:
    return get_mother(particle.parent())

def truth_matching(list, list_tr,counter):
  l = list[i]
  truth_matched = []
#  for l in list:
  for k in list_tr:
    if pdgId(l) == k.pdgId():
      if l.p4().DeltaR(k.p4()) < .05:
        truth_matched.append(k)
        counter += 1
  return counter, truth_matched

def pdgId(p):
  if type(p) == ROOT.xAOD.Muon_v1: return -13*p.charge()
  if type(p) == ROOT.xAOD.Electron_v1: return -11*p.charge()
  assert False

for file in range(len(fileName)):
  f = ROOT.TFile.Open(fileName[file], "READONLY")
  t = ROOT.xAOD.MakeTransientTree(f, "CollectionTree")
  print "Number of input events:", t.GetEntries()

 ###################################
 # Begin Code for H+ TO 3LEP + MET #
 ###################################

  counter_neu = 0
  c = 0
  total = 0
  total_2 = 0
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
#      if m.quality() != 2: continue
      if m.pt() < 5000: continue
      if abs(m.eta()) > 2.7: continue
      leps.append(m)
    for e in el:
#      if e.passSelection("LHLoose"):
        if e.pt() < 5000: continue
        if abs(e.eta()) > 2.47: continue
        leps.append(e)
    
    leps = sorted(leps, reverse = True, key=(lambda l: l.p4().Pt()))
    leps_tr = sorted(leps_tr, reverse = True, key=(lambda l: l.p4().Pt()))
    if len(leps) < 3: continue
    if abs(sum(map(pdgId, leps[:3]))) not in [11,13]: continue
    if len(set([abs(pdgId(leps[0])), abs(pdgId(leps[1])), abs(pdgId(leps[2]))])) != 2: continue #two same flavor

    for pair in [(0, 1), (0, 2), (1, 2)]:
      if pdgId(leps[pair[0]]) + pdgId(leps[pair[1]]) == 0:
        p4 = leps[pair[0]].p4() + leps[pair[1]].p4()
        for i in pair:
          c,truth_matched = truth_matching(leps,leps_tr,c)
        total += 2
        break

    for tr in truth_matched:
      mother = get_mother(tr)
      if mother == None: continue
      total_2 += 1
      if abs(mother.pdgId()) == 1000023:
        counter_neu += 1
#        print mother.pdgId()

  print counter_neu, total, c, float(c)/total*100, counter_neu, total_2, float(counter_neu)/(total_2)*100
print "Finished"
