#!/usr/bin/env python2.7
# Set up ROOT and RootCore:
import ROOT
ROOT.gROOT.SetBatch(True) ## prevents images from drawing in window
ROOT.gROOT.Macro( '$ROOTCOREDIR/scripts/load_packages.C' )

#ROOT.SetAtlasStyle()
#ROOT.SetAtlasLabel(0.2, 0.87, "Internal")
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(1)
# Initialize the xAOD infrastructure:
if(not ROOT.xAOD.Init().isSuccess()): print "Failed xAOD.Init()"

inputFile = ROOT.TFile.Open("histo.overlay.root", "READ")
#inputFile = ROOT.TFile.Open("histo.new.root", "READ")
outputFile = ROOT.TFile.Open("histo.test.root", "UPDATE")

########################
#Begin Code for OVERLAY#
########################
keys = inputFile.GetListOfKeys()
dictionaryNames = {}
dictionary = {}
for k in keys:
  h = k.ReadObj()
  names = k.ReadObj()
  dictionary[h] = h
  dictionaryNames[names.GetName()] = names

lum = 130E3
xsec_3lep = .00200446

def plot_and_save(sig, signal_str):
  title = sig.GetName()
  canvas = ROOT.TCanvas();
  sig.Draw("HIST E1")
  canvas.Print("./plots/"+title+".png")

def overlay_and_normalize(dict_name, bkg):
  title = bkg.GetName()
  print title
  title = title[:-4]
  canvas = ROOT.TCanvas();
  colors = [2,8,7,9,6] #,5,30,22,12,17,18]
  bkg.SetLineColor(1)
  bkg.SetFillColorAlpha(1,.90)
  bkg.SetFillStyle(3001)
  if bkg.Integral() != 0:
    bkg.Scale(1/(bkg.Integral()))
  legend = ROOT.TLegend();
#  legend = ROOT.TLegend(0.580,0.572,.981,0.78);
  legend = ROOT.TLegend(0.550,0.57,.981,0.90);
  legend.SetTextSize(.028);
#  bkg.SetTitle(title)
  legend.AddEntry(bkg,"Background(ttbar)");
  bkg.Draw("HIST")  
  for name in dict_name:
    dict_name[name].SetFillStyle(3003)
    if name [-7:] == "_0_3lep":
      if dict_name[name].Integral() != 0:
        dict_name[name].Scale(1/(dict_name[name].Integral()))
      dict_name[name].SetLineColor(2)
#      dict_name[name].SetFillColorAlpha(colors[0],.80)
      legend.AddEntry(dict_name[name],"Benchmark(m_{H+} = 500GeV)");
      dict_name[name].Draw("HIST SAME")
    if name [-7:] == "_1_3lep":
      if dict_name[name].Integral() != 0:
        dict_name[name].Scale(1/(dict_name[name].Integral()))
      dict_name[name].SetLineColor(8)
#      dict_name[name].SetFillColorAlpha(colors[1],.70)
      legend.AddEntry(dict_name[name],"Benchmark(m_{H+} = 600GeV)");
      dict_name[name].Draw("HIST SAME")
    if name [-7:] == "_2_3lep":
      if dict_name[name].Integral() != 0:
        dict_name[name].Scale(1/(dict_name[name].Integral()))
      dict_name[name].SetLineColor(7)
#      dict_name[name].SetFillColorAlpha(colors[2],.60)
      legend.AddEntry(dict_name[name],"Benchmark(m_{H+} = 700GeV)");
      dict_name[name].Draw("HIST SAME")
    if name [-7:] == "_3_3lep":
      if dict_name[name].Integral() != 0:
        dict_name[name].Scale(1/(dict_name[name].Integral()))
      dict_name[name].SetLineColor(9)
#      dict_name[name].SetFillColorAlpha(colors[3],.50)
      legend.AddEntry(dict_name[name],"Benchmark(m_{H+} = 800GeV)");
      dict_name[name].Draw("HIST SAME")
    if name [-7:] == "_4_3lep":
      if dict_name[name].Integral() != 0:
        dict_name[name].Scale(1/(dict_name[name].Integral()))
      dict_name[name].SetLineColor(6)
#      dict_name[name].SetFillColorAlpha(colors[4],.40)
      legend.AddEntry(dict_name[name],"Benchmark(m_{H+} = 1000GeV)");
      dict_name[name].Draw("HIST SAME")
  legend.Draw()
  canvas.Print("./plots/"+title+"_overlay.png")

for name in dictionaryNames:
  dictionary_sig ={}
  plot_and_save(dictionaryNames[name],"val")
  if name [-5:] != "_3lep": continue
  sig_name = [name[:-7]+"_0_3lep",name[:-7]+"_1_3lep",name[:-7]+"_2_3lep",name[:-7]+"_3_3lep",name[:-7]+"_4_3lep"]
  background_name = name[:-7]+"_5_ttb"
  if background_name not in dictionaryNames: continue
  print background_name, dictionaryNames.keys()
  for i in sig_name: 
    if i not in dictionaryNames: continue
    dictionary_sig[i] = dictionaryNames[i]
#  plot_and_save(dictionaryNames[name])
  overlay_and_normalize(dictionary_sig, dictionaryNames[background_name])
outputFile.Write()
