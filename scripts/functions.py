#!/usr/bin/env python3 

import statistics
import numpy
import pandas as pd
import pathlib
import re
import os
import matplotlib.pyplot as plt
import matplotlib as mpl
from tkinter import messagebox

#############################################################
# Sortir les valeurs uniques d'une liste
def unique(list1) :
    x = numpy.array(list1)
    return(numpy.unique(x))

#############################################################
# Lire un fichier, 3 types possibles
def lire_fichier(file, type):
    # Gestion erreurs    
    if type!="cnv" and type!="ratio" and type!="annot" :
        print("\nsegmentation.py\nin lire_fichier("+file+","+type+")\Erreur[4]: Type inconnu.\n")
        exit(4)

    try :
        nameHandle = open(file,'r')
    except FileNotFoundError :
        print("\nsegmentation.py\in lire_fichier("+file+","+type+")\Erreur[2]: Fichier introuvable.\n")
        exit(2)
    except OSError :
        print("\nsegmentation.py\in lire_fichier("+file+","+type+")\Erreur[3]: Impossible d'ouvrir le fichier.\n")
        exit(3)
    nameHandle.close()

    # Type de fichier "cnv"
    if (type=="cnv") :
        cnvs=pd.read_csv(file, delimiter="\t")
        cnvs["start"]=pd.to_numeric(cnvs["start"])
        cnvs["end"]=pd.to_numeric(cnvs["end"])
        cnvs["copy number"]=pd.to_numeric(cnvs["copy number"])
        cnvs["uncertainty"]=pd.to_numeric(cnvs["uncertainty"])
        cnvs["WilcoxonRankSumTestPvalue"]=pd.to_numeric(cnvs["WilcoxonRankSumTestPvalue"])
        cnvs["KolmogorovSmirnovPvalue"]=pd.to_numeric(cnvs["KolmogorovSmirnovPvalue"])
        return(cnvs)
    # Type de fichier "ratio"
    elif (type=="ratio"):
        path_split = file.split("/")
        file_extension = path_split[len(path_split)-1].split(".")[len(path_split[len(path_split)-1].split("."))-1]
        if (file_extension!="txt") :
            print("\nsegmentation.py\in lire_fichier("+file+","+type+")\Erreur[1]: Ce n'est pas un fichier de ratios.\n")
            exit(1)        
        # Lire le fichier
        ratiosDict=pd.read_csv(file, delimiter="\t")
        ratiosDict["Start"]=pd.to_numeric(ratiosDict["Start"])
        ratiosDict["Ratio"]=pd.to_numeric(ratiosDict["Ratio"])
        ratiosDict["MedianRatio"]=pd.to_numeric(ratiosDict["MedianRatio"])
        # Ratios sont en log2 donc on passe en 2^
        ratiosDict["CN"] = [numpy.power(2,ratiosDict["Ratio"][i]) for i in range(len(ratiosDict["Ratio"]))]
        # Identifier les DEL et AMP
        ratiosDict["alt"]= ["" for i in range(ratiosDict.shape[0])]
        ratiosDict.loc[numpy.logical_and(ratiosDict["Ratio"]!=-1,ratiosDict["CN"]<=1.5), "alt"] = "DEL"
        ratiosDict.loc[numpy.logical_and(ratiosDict["Ratio"]!=-1,ratiosDict["CN"]>=3),"alt"] = "AMP"
        ratiosDict.loc[numpy.logical_and(ratiosDict["Ratio"]!=-1,ratiosDict["alt"]==""), "alt"] = "NONE"
        return(ratiosDict)
    # Type de fichier "annot"   
    else :
        # Gestion erreurs
        path_split = file.split("/")
        file_extension = path_split[len(path_split)-1].split(".")[len(path_split[len(path_split)-1].split("."))-1]
        if (file_extension!="gtf") :
            print("\nsegmentation.py\in lire_fichier("+file+","+type+")\Erreur[1]: Ce n'est pas un fichier GTF.\n")
            exit(1)
        # Lire le fichier
        annotationDict=pd.read_csv(file, delimiter="\t", names=["chr","1","2","start","end","5","6","7","annots"])
        annotationDict=annotationDict[["chr","start","end","annots"]]
        annotationDict["start"]=pd.to_numeric(annotationDict["start"])
        annotationDict["end"]=pd.to_numeric(annotationDict["end"])
        # On enleve les charactère et converti la colonne "chr"
        annotationDict["chr"] = annotationDict["chr"].str[3:]
        annotationDict["geneName"] = annotationDict["annots"].str.split(";",
                                                                        expand=True).loc[:,4].str.split(" ",
                                                                                                        expand=True).loc[:,2].str[1:-1]
        return(annotationDict)        

#############################################################
# Segmentation Wilfried
def segmentation(ratiosDict): 
    # Initialisation du dictionnaire de sortie
    dataDict=pd.DataFrame(columns=["segmentChr_list",
                                "segmentStart_list",
                                "segmentEnd_list",
                                "segmentSize_list",
                                "segmentCount_list",
                                "segmentMed_list",
                                "segmentValue_list"])

    # Initialisation des Variables "En cours de boucle" 
    chr=""
    start=""
    ratio=""
    CN=""
    alt=""

    # Initialisation des Variables "Précédente boucle" 
    eventStart=""
    eventEnd=""
    eventValue=""
    eventCN=""
    eventRatio="coucou"
    eventChr=""
    eventArray=[]

    # Compteur des évènements (CNA)
    count=0

    # Itération sur l'ensemble des lignes du fichiers de ratios
    for i in range(0,len(ratiosDict["Chromosome"])) :
        chr=ratiosDict["Chromosome"][i]
        start=ratiosDict["Start"][i]
        ratio=ratiosDict["Ratio"][i]
        CN=ratiosDict["CN"][i]
        alt=ratiosDict["alt"][i]
        count=count+1
        if (eventStart=="") :
            eventStart=start
            eventEnd=start
            eventValue=alt
            eventRatio=ratio
            eventCN=CN
            eventChr=chr
            count=0
            eventArray=[]
        elif (eventRatio==-1.0) :
            eventStart=start
            eventEnd=start
            eventValue=alt
            eventRatio=ratio
            eventCN=CN
            eventChr=chr
            count=0
            eventArray=[]            
        
        else :
            if (eventChr!=chr) :
                # Nouveau chromosome, on enregistre the dernier évènement
                try :
                    med=statistics.median(eventArray)
                    if (med > 6) :
                        med = 6
                except(statistics.StatisticsError) :
                        med = CN

                if(count>=0):
                    dataDict.loc[len(dataDict)] = [ eventChr,
                                                    eventStart,
                                                    eventEnd,
                                                    eventEnd-eventStart,
                                                    count,
                                                    med,
                                                    eventValue]

                eventStart=start
                eventEnd=start
                eventValue=alt
                eventRatio=ratio
                eventChr=chr
                eventCN=CN
                count=0
                eventArray=[]
        
            else :
                if (eventValue!=alt) :
                    # Nouvel évènement, on enregistre the dernier évènement
                    try :
                        # Gestion des erreurs et seuil sur médiane à 6 max
                        med=statistics.median(eventArray)
                        if (med > 6) :
                            med = 6
                    except(statistics.StatisticsError) :
                        med = CN

                    if(count>=0):
                        dataDict.loc[len(dataDict)] = [ eventChr,
                                                        eventStart,
                                                        eventEnd,
                                                        eventEnd-eventStart,
                                                        count,
                                                        med,
                                                        eventValue]               

                    # Réinitialisation des variables "Précédente boucle"
                    eventStart=start
                    eventEnd=start
                    eventValue=alt
                    eventRatio=ratio
                    eventChr=chr
                    eventCN=CN
                    count=0
                    eventArray=[]
            
                else :
                    # On avance en enregister la valeur CN
                    eventEnd=start
                    if (count==1) :
                        eventArray.append(eventCN)

                    eventArray.append(CN)

    #print the last event
    try :
        med=statistics.median(eventArray)
        if (med > 6) :
            med = 6
    except(statistics.StatisticsError) :
        med = CN

    dataDict.loc[len(dataDict)] = [ eventChr,
                                    eventStart,
                                    eventEnd,
                                    eventEnd-eventStart,
                                    count,
                                    med,
                                    eventValue] 
    
    return(dataDict)

#############################################################
## Fonction pour filtrer un Dataframe pandas à partir d'une valeur donnée
def filtering(segmentsDict,cutoff): 
    segmentsDict_filtered = segmentsDict.loc[numpy.logical_and(segmentsDict["segmentValue_list"]!='NONE',
                                                               segmentsDict["segmentCount_list"]>=cutoff), :]
    return(segmentsDict_filtered)

#############################################################
## Fonction pour annoter un Dataframe pandas à partir d'un autre Dataframe d'annotation
def annotation(segmentsDict_filtered,annotationDict): 
    genes_list=[]
    # Si le dataframe vient des segments 
    if list(segmentsDict_filtered.columns)[0]=="segmentChr_list":
        colonne_chr="segmentChr_list"
        colonne_start="segmentStart_list"
        colonne_end="segmentEnd_list"
    # Si le dataframe vient des ratios         
    else :
        colonne_chr="chr"
        colonne_start="start"
        colonne_end="end"

    for i in range(len(list(segmentsDict_filtered[colonne_chr]))) :
        annotChr_list=list(annotationDict["chr"][annotationDict["chr"]==str(segmentsDict_filtered[colonne_chr][i])])
        annotStart_list=list(annotationDict["start"][annotationDict["chr"]==str(segmentsDict_filtered[colonne_chr][i])])
        annotEnd_list=list(annotationDict["end"][annotationDict["chr"]==str(segmentsDict_filtered[colonne_chr][i])])
        annotGene_list=list(annotationDict["geneName"][annotationDict["chr"]==str(segmentsDict_filtered[colonne_chr][i])])
        segmentStart=segmentsDict_filtered[colonne_start][i]
        segmentEnd=segmentsDict_filtered[colonne_end][i]

        genes_str=""
        for j in range(0,len(annotStart_list)) :
            if (annotStart_list[j]>=segmentStart and annotStart_list[j]<segmentEnd) or (annotEnd_list[j]>segmentStart and annotEnd_list[j]<=segmentEnd) :
                genes_str= str(annotGene_list[j]) if genes_str=="" else str(genes_str+";"+annotGene_list[j])

        genes_list.append(genes_str)

    segmentsDict_filtered.insert(segmentsDict_filtered.shape[1], "genes_list", genes_list)
    
#############################################################
## Fonction pour enregister le Dataframe pandas de segments
def enregistrer_segments(out_file,segmentsDict_filtered,sampleId) :
    fichier = open(out_file, "a")
    for i in range(0,len(segmentsDict_filtered["segmentChr_list"])) :
        fichier.write(str(sampleId)+","+
                      str(segmentsDict_filtered["segmentChr_list"][i])+","+
                      str(segmentsDict_filtered["segmentStart_list"][i])+","+
                      str(segmentsDict_filtered["segmentEnd_list"][i])+","+
                      str(segmentsDict_filtered["segmentSize_list"][i])+","+
                      str(segmentsDict_filtered["segmentCount_list"][i])+","+
                      str(segmentsDict_filtered["segmentMed_list"][i])+","+
                      str(segmentsDict_filtered["segmentValue_list"][i])+","+
                      str(segmentsDict_filtered["genes_list"][i])+"\n")
    fichier.close()

#############################################################
## Fonction pour enregister le Dataframe pandas de CNVs
def enregistrer_cnvs(out_file,cnvs,sampleId) :
    fichier = open(out_file, "a")
    for i in range(0,len(cnvs["chr"])) :
        fichier.write(str(sampleId)+","+
                      str(cnvs["chr"][i])+","+
                      str(cnvs["start"][i])+","+
                      str(cnvs["end"][i])+","+
                      str(cnvs["end"][i]-cnvs["start"][i])+","+                      
                      str(cnvs["copy number"][i])+","+
                      str(cnvs["CNAnumber"][i])+","+
                      str(cnvs["status"][i])+","+
                      str(cnvs["genotype"][i])+","+
                      str(cnvs["uncertainty"][i])+","+
                      str(cnvs["WilcoxonRankSumTestPvalue"][i])+","+
                      str(cnvs["KolmogorovSmirnovPvalue"][i])+","+
                      str(cnvs["genes_list"][i])+"\n")
    fichier.close()

#############################################################
## Fonction pour enregister le Dataframe pandas des segments IGV
def enregistrer_freecs(out_file,freecs,sampleId) :
    fichier = open(out_file, "a")
    for i in range(0,len(freecs["Chromosome"])) :
        fichier.write(str(sampleId)+"\t"+
                      str(freecs["Chromosome"][i])+"\t"+
                      str(freecs["Start"][i])+"\t"+
                      str(freecs["End"][i])+"\t"+
                      str(freecs["Num_Probes"][i])+"\t"+
                      str(freecs["Segment_Mean"][i])+"\n")
    fichier.close()

#############################################################
## Fonction pour enregister les statistiques
def enregistrer_stats(outStats_file,stats,header) :
    fichier = open(outStats_file, "w")
    fichier.write(header+"\n")
    for line in stats :
        fichier.write(line+"\n")
    fichier.close()

#############################################################
## Fonction pour trouver le chemin des fichiers de ratios
def find_ratios_files(folder) :
    parent_folder=pathlib.Path(folder)
    out=""
    for file in parent_folder.glob("*.bam_ratio.txt") :
        out=folder+"/"+file.name
        
    return(out)

#############################################################
## Fonction pour trouver le chemin des fichiers de CNVs
def find_cnvs_files(folder) :
    parent_folder=pathlib.Path(folder)
    out=""

    max=0
    val=""
    for name in parent_folder.glob("*.bam_CNVs*"):
        if len(name.name)>max :
            val = name.name
            max=len(name.name)

    return(folder+"/"+val)

#############################################################
## Fonction de la méthode conseillé par W.G (ICO)
def plot_wilfried(ratiosDict, segmentsDict, sampleId, out_svg):

    # Création des figures
    fig, ax = plt.subplots()

    # Création des coordonnées des points
    x = []
    breaks=[]
    ticks=[]
    for chr in unique(list(ratiosDict["Chromosome"])):
        tmp = list(ratiosDict["Start"][ratiosDict["Chromosome"]==chr])
        if chr==1 :
            ancien = tmp[len(tmp)-1]
            for val in tmp : x.append(val) 
        else :
            for i in range(len(tmp)) :
                tmp[i] = tmp [i]+ ancien
            for val in tmp : x.append(val) 
            ancien = tmp[len(tmp)-1]
        breaks.append(tmp[len(tmp)-1])
    ticks.append(1+((breaks[0]-1)/2))
    for i in range(1,len(breaks)) : 
        ticks.append(breaks[i-1]+((breaks[i]-breaks[i-1])/2))
    # Plot les points
    index_tmp=list(ratiosDict.index)
    for i in range(0,len(x)) :
        if ratiosDict.loc[index_tmp[i],"Ratio"]==-1 :
            ax.plot(x[i],numpy.nan)
        elif ratiosDict.loc[index_tmp[i],"CN"]<=1.7 :
            ax.plot(x[i],ratiosDict.loc[index_tmp[i],"CN"],'ob',markersize=1)
        elif ratiosDict.loc[index_tmp[i],"CN"]>=3 :
            if ratiosDict.loc[index_tmp[i],"CN"] > 6 :
                ax.plot(x[i],6,'or',markersize=1)
            else :
                ax.plot(x[i],ratiosDict.loc[index_tmp[i],"CN"],'or',markersize=1)
        else :
            ax.plot(x[i],ratiosDict.loc[index_tmp[i],"CN"],'og',markersize=1)

    # Création des coordonnées des points
    event_chr=""
    j=-1

    for chr in unique(list(segmentsDict["segmentChr_list"])):
        tmp_start = list(segmentsDict["segmentStart_list"][segmentsDict["segmentChr_list"]==chr])
        tmp_end = list(segmentsDict["segmentEnd_list"][segmentsDict["segmentChr_list"]==chr])
        tmp_Medratio = list(segmentsDict["segmentMed_list"][segmentsDict["segmentChr_list"]==chr])
        tmp_alt = list(segmentsDict["segmentValue_list"][segmentsDict["segmentChr_list"]==chr])
        for i in range(0,len(tmp_start)) :
            if chr == 1 :
                val=0
            else :
                val=breaks[j]
            
            if tmp_alt[i]== "NONE" :
                ys=[2,2]
            elif tmp_alt[i]=="AMP" :
                if (tmp_Medratio[i]>6 or tmp_Medratio[i]>3) :
                    ys=[6,6]
                else : 
                    ys = [3,3]
            else :
                ys = [1,1]

            ax.plot([tmp_start[i]+val,tmp_end[i]+val],ys,'k',linestyle='-',linewidth=1, alpha=0.75)
        j=j+1

    ax.vlines(x=breaks[0:-1], ymin= 0, ymax=6.2, color='black',linestyle="--", alpha=0.5,linewidth=1)
    ax.set_ylim(ymin=0,ymax=6.2)
    #ax.set_xlim(xmin=0,xmax=x[len(x)-1]+1)
    ax.set_xmargin(0.005)
    ax.set_xticks(ticks)
    ax.grid(axis='y', linestyle="dotted")
    ax.set_xticklabels(unique(list(ratiosDict["Chromosome"])))
    ax.set_title(sampleId)
    ax.set_ylabel("Copy Number Profile")
    ax.set_xlabel("Chromosome")
    fig.set_figwidth(20)
    fig.tight_layout()
    plt.savefig(out_svg,format="svg")
    fig.clear()
    plt.close(fig)

#############################################################
## Fonction du graphique Methode 2 FREEC
def plot_freec(ratiosDict, freecs,cnvs, sampleId, cutoff, out_svg):

    # Création des figures
    fig, ax = plt.subplots(nrows=2, ncols=1)

    # Création des coordonnées des points
    x = []
    breaks=[]
    ticks=[]
    pat1 = re.compile("[0-9]+")
    pat2 = re.compile("[a-zA-Z]+")
    chrs=sorted(numpy.unique(list(ratiosDict["Chromosome"])))
    letters=list(filter(pat2.match, chrs))
    chrs=list(filter(pat1.match, chrs))
    chrs = sorted([int(chrs[i]) for i in range(len(chrs))])
    chrs = [str(chrs[i]) for i in range(len(chrs))]

    # Création des ticks
    for chr in (chrs+letters):
        tmp_start = list(ratiosDict["Start"][ratiosDict["Chromosome"]==chr])

        if chr=="1" :
            ancien = tmp_start[len(tmp_start)-1]
            for val in tmp_start : x.append(val) 
        else :
            for i in range(len(tmp_start)) :
                tmp_start[i] = tmp_start[i] + ancien
            for val in tmp_start : x.append(val) 
            ancien = tmp_start[len(tmp_start)-1]
        breaks.append(tmp_start[len(tmp_start)-1])
    ticks.append(1+((breaks[0]-1)/2))
    for i in range(1,len(breaks)) : 
        ticks.append(breaks[i-1]+((breaks[i]-breaks[i-1])/2))

    # Plot les points
    y=numpy.log2(list(ratiosDict["Ratio"]))
    index_tmp=list(ratiosDict.index)
    orig_cmap= mpl.cm.coolwarm
    ax[0].scatter(x,y,s=1,c=y,cmap=orig_cmap, vmin=-0.5, vmax=0.5)

    for i in range(0,len(x)) :
        if ratiosDict.loc[index_tmp[i],"CN"]<=1.7 and ratiosDict.loc[index_tmp[i],"Ratio"]!=-1:
            ax[1].plot(x[i],ratiosDict.loc[index_tmp[i],"Ratio"]*2,'ob',markersize=1)
        elif ratiosDict.loc[index_tmp[i],"CN"]>=3 and ratiosDict.loc[index_tmp[i],"Ratio"]!=-1:
            if ratiosDict.loc[index_tmp[i],"CN"]>=6 :
                ax[1].plot(x[i],6,"^r",markersize=2)
            else :
                ax[1].plot(x[i],ratiosDict.loc[index_tmp[i],"Ratio"]*2,'or',markersize=1)
        elif ratiosDict.loc[index_tmp[i],"Ratio"]!=-1 :
            ax[1].plot(x[i],ratiosDict.loc[index_tmp[i],"Ratio"]*2,'o',color='green',markersize=1, alpha =0.75)
    
    # Plot les segments
    j=-1
    for chr in (chrs+letters):    
        tmp_segStart = list(freecs["Start"][freecs["Chromosome"]==chr])
        tmp_segEnd = list(freecs["End"][freecs["Chromosome"]==chr])
        tmp_segVal = list(freecs["Segment_Mean"][freecs["Chromosome"]==chr])
        tmp_Num = list(freecs["Num_Probes"][freecs["Chromosome"]==chr])

        tmp_start = list(cnvs["start"][cnvs["chr"]==chr])
        tmp_end = list(cnvs["end"][cnvs["chr"]==chr])
        tmp_ploidy = list(cnvs["copy number"][cnvs["chr"]==chr])
        tmp_CNA = list(cnvs["CNAnumber"][cnvs["chr"]==chr])

        for start, end, val, num in zip(tmp_segStart,tmp_segEnd,tmp_segVal, tmp_Num) :
            if chr == "1" :
                val_seg=0
            else :
                val_seg=breaks[j]

            if num>1 :
                ax[0].plot([start+val_seg,end+1+val_seg], [val,val], color='black',  linewidth=1)

        for start, end, ploidy, num in zip(tmp_start,tmp_end,tmp_ploidy, tmp_CNA) :
            if chr == "1" :
                val_seg=0
            else :
                val_seg=breaks[j]

            if num>1 :
                if ploidy > 6 :
                    ax[1].plot([start+val_seg,end+val_seg], [6,6], color='black',  linewidth=1)      
                else :
                    ax[1].plot([start+val_seg,end+val_seg], [ploidy,ploidy], color='black',  linewidth=1)      
                    
        j=j+1


    ax[0].vlines(x=breaks[0:-1], ymin= 0,ymax= 1, transform= ax[0].get_xaxis_transform(),color='black',linestyle="--", alpha=0.5,linewidth=1)
    ax[0].set_xmargin(0.005)
    ax[0].set_xticks(ticks)
    ax[0].grid(axis='y', linestyle="dotted")
    ax[0].set_xticklabels((chrs+letters))
    ax[0].set_title(sampleId)
    ax[0].set_xlabel("Chromosome")
    ax[0].set_ylabel("Normalised Copy Number Profile")

    ax[1].vlines(x=breaks[0:-1], ymin= 0,ymax= 1, transform= ax[1].get_xaxis_transform(),color='black',linestyle="--", alpha=0.5,linewidth=1)
    ax[1].set_xmargin(0.005)
    ax[1].set_xticks(ticks)
    ax[1].grid(axis='y', linestyle="dotted")
    ax[1].set_xticklabels(chrs+letters)
    ax[1].set_title(sampleId)
    ax[1].set_xlabel("Chromosome")
    ax[1].set_ylabel("Copy Number Profile")

    fig.set_figwidth(20)
    fig.set_figheight(10)
    fig.tight_layout()
    plt.savefig(out_svg,format="svg")
    fig.clear()
    plt.close(fig)

#############################################################
# Fonction traduite de perl à python, source : control-freec manual
def freec2absolute(ratiosDict):
    dataDict=pd.DataFrame(columns=["Chromosome",
                                "Start",
                                "End",
                                "Num_Probes",
                                "Segment_Mean"])
    weirdNum=345

    for chr in numpy.unique(list(ratiosDict["Chromosome"])):
        tt = list(ratiosDict["Chromosome"][ratiosDict["Chromosome"]==chr].index)
        if (len(tt)>0) :
            myMedianRatio=weirdNum
            mySegNUmber=0
            for j in range(0,len(tt)) :
                if (ratiosDict.loc[tt,"MedianRatio"][tt[j]]!=myMedianRatio) :
                    #print the record if it is not -1 or weirdNum
                    if (myMedianRatio != -1 and myMedianRatio != weirdNum) :
                        dataDict.loc[len(dataDict)] =  [chr,
                                                        ratiosDict.loc[tt,"Start"][tt[j]-mySegNumber],
                                                        ratiosDict.loc[tt,"Start"][tt[j]]-1,
                                                        mySegNumber,
                                                        numpy.log2(myMedianRatio)]
                    #update
                    mySegNumber=1
                    myMedianRatio=ratiosDict["MedianRatio"][tt[j]]

                else :
                    #update:
                    mySegNumber = mySegNumber+1
                    
            #print the last segment
            if (myMedianRatio != -1 and myMedianRatio != weirdNum) :
                dataDict.loc[len(dataDict)] =  [chr,
                                                ratiosDict.loc[tt,"Start"][tt[j]-mySegNumber],
                                                ratiosDict.loc[tt,"Start"][tt[j]]-1,
                                                mySegNumber,
                                                numpy.log2(myMedianRatio)]
    return(dataDict)  