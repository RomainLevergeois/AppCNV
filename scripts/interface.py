#!/usr/bin/env python3 

#Interface graphique pour python nécessitant l'installation de python 3 avec les modules complémentaires suivant :
#	-MatPlotLib
#	-Tkinter
#	-numpy
#   -pandas

#Utilisation : > python3 ./interface.py

#Par Levergeois.R

# Importation des packages################
import tkinter as tk
import tkinter.font as tkfont
from tkinter.filedialog import *
from tkinter import ttk
from tkinter import messagebox
import numpy
import functools
import threading
import math
import os
import re
import time
import gc
import pandas as pd
from PIL import Image, ImageTk
fp = functools.partial

# Importation des fonctions
import functions

# Variables globales pour les fonctions internes Tkinter
old_width=0
# Pour linux 196
val = 208
img_b = []

#Fonctions###############################
## Fonctions de gestion de la barre de progression
def update(ind):
    frame = animation[ind]
    label.configure(image=frame)
    ind += 1
    if ind == framesTotal:
        ind = 0
    root.after(60, update, ind)


def update_progress_label():
    val = round(pb['value'],1)
    return f"Progression actuelle : {val}%"

def progression(val):
    global elapsed_time
    if val < 100:
        pb['value'] = val
        value_label['text'] = update_progress_label()
        root.update_idletasks()
    else:
        pb['value'] = 100
        value_label['text'] = update_progress_label()
        root.update_idletasks()
        messagebox.showinfo(message='Le processus est terminé !\nTemps écoulé : '+str(math.trunc(elapsed_time/60))+'m'+str(math.trunc(elapsed_time%60))+"s")
        reinitialiser()

def stop():
    pb.stop()
    value_label['text'] = update_progress_label()

## Fonctions de gestion des widgets
def reinitialiser():
    global sample_table
    global cnvs_file
    global ratios_files
    # On réactive les widgets
    enable(buttons_frame.winfo_children())
    plus_button.configure(state="normal")
    moins_button.configure(state="normal")
    run_button.configure(state="normal")
    out_folder_button.configure(state="normal")

    stop()
    params=[]
    ratios_files=[]
    sample_table=[]
    cnvs_file=[]
    gc.collect()

def resize_paths():
    global filepath
    global buttons_frame
    global dirs_table
    i=1
    for path in dirs_table:
        filepath2 = path
        cpt=2
        tmp=0
        font.measure(filepath2) > buttons_frame.nametowidget("text"+str(i)).winfo_width()
        for j in range(len(filepath2.split("/"))-1) :
            if font.measure(filepath2) <= buttons_frame.nametowidget("text"+str(i)).winfo_width() :
                continue

            truc=filepath2.split("/")[len(filepath2.split("/"))-cpt]
            index_a_retirer=filepath2.index(truc)
            if tmp==0 :
                tmp=index_a_retirer+len(truc)
                cpt=cpt+1
            filepath2=filepath2[0:index_a_retirer]+"..."+filepath2[tmp:len(filepath2)]
            tmp=filepath2.index(filepath2.split("/")[len(filepath2.split("/"))-1])-1

        buttons_frame.nametowidget("text"+str(i)).config(state=tk.NORMAL)
        buttons_frame.nametowidget("text"+str(i)).delete("1.0","end")
        buttons_frame.nametowidget("text"+str(i)).insert(tk.END,filepath2)
        buttons_frame.nametowidget("text"+str(i)).config(state=tk.DISABLED)
        i=i+1



def soumettre_dossiers(i):
    # Cette fonction est appelée avec le bouton "Soumettre un fichier",
    # Stocke le contenu du fichier sélectionné dans le fichier cible.fasta .
    global filepath
    global buttons_frame
    filepath = str(askdirectory(title="Ouvrir un Dossier"))
    dirs_table[i-1]=filepath
    filepath2 = filepath
    cpt=2
    tmp=0
    font.measure(filepath2) > buttons_frame.nametowidget("text"+str(i)).winfo_width()
    for j in range(len(filepath2.split("/"))-1) :
        if font.measure(filepath2) <= buttons_frame.nametowidget("text"+str(i)).winfo_width() :
            continue

        truc=filepath2.split("/")[len(filepath2.split("/"))-cpt]
        index_a_retirer=filepath2.index(truc)
        if tmp==0 :
            tmp=index_a_retirer+len(truc)
            cpt=cpt+1
        filepath2=filepath2[0:index_a_retirer]+"..."+filepath2[tmp:len(filepath2)]
        tmp=filepath2.index(filepath2.split("/")[len(filepath2.split("/"))-1])-1

    buttons_frame.nametowidget("text"+str(i)).config(state=tk.NORMAL)
    buttons_frame.nametowidget("text"+str(i)).delete("1.0","end")
    buttons_frame.nametowidget("text"+str(i)).insert(tk.END,filepath2)
    buttons_frame.nametowidget("text"+str(i)).config(state=tk.DISABLED)

    buttons_frame.nametowidget("sampleId"+str(i)).delete(0,tk.END)
    buttons_frame.nametowidget("sampleId"+str(i)).insert(tk.END,filepath2.split("/")[len(filepath2.split("/"))-1])

def soumettre_dossier_sortie():
    # Cette fonction est appelée avec le bouton "Soumettre un fichier",
    # Stocke le contenu du fichier sélectionné dans le fichier cible.fasta .
    global filepath
    filepath = str(askdirectory(title="Ouvrir un Dossier"))
    root.nametowidget("text_out_folder").config(state=tk.NORMAL)
    root.nametowidget("text_out_folder").delete("1.0","end")
    root.nametowidget("text_out_folder").insert(tk.END,filepath)
    root.nametowidget("text_out_folder").config(state=tk.DISABLED)

def resize(event):
    global canva
    global old_width
    global val
    global totrows
    canva.update_idletasks()
    
    if old_width!=0:
        diff = canva.winfo_width() - old_width
        val = val+diff*0.5
        for i in range(1,totrows):
            buttons_frame.nametowidget("text"+str(i)).grid(row=i, column=1, 
                                                    columnspan=1, rowspan=1,  
                                                    padx=5, pady=5,sticky="nsew", ipadx=val)
        buttons_frame.update_idletasks()

    old_width = canva.winfo_width()
    resize_paths()

def ajouter_ligne():
    global totrows
    global buttons_frame
    i=totrows
    global img_b
    global val

    img_tmp = Image.open("../img/img_upload_b.png")
    img_tmp = img_tmp.resize((25,25))
    img_tmp = ImageTk.PhotoImage(img_tmp)
    img_b.append(img_tmp)

    sampleId = tk.Entry(buttons_frame, 
                     width=20, 
                     justify=tk.CENTER, 
                     name="sampleId"+str(i))
    sampleId.insert(0,"Sample Id"+str(i))
    tk.Text(buttons_frame, 
                            width=1, 
                            height=1, 
                            state=tk.DISABLED, 
                            name="text"+str(i), 
                            bg=defaultbg)
    folder_button=tk.Button(buttons_frame,
                            compound=tk.LEFT,
                            name="folder_button"+str(i),
                            command= lambda : soumettre_dossiers(i), 
                            bg="#555555", fg="white", 
                            activeforeground="#555555", 
                            activebackground="white",
                            image=img_b[i-1])

    sampleId.grid(row=i, column=0, 
                  columnspan=1, rowspan=1,  
                  padx=5, pady=5,sticky=tk.N)
    buttons_frame.nametowidget("text"+str(i)).grid(row=i, column=1, 
                          columnspan=1, rowspan=1,  
                          padx=5, pady=5,sticky="nsew", ipadx=val)

    folder_button.grid(row=i, column=2, 
                       columnspan=1, rowspan=1,  
                       padx=2, pady=1, sticky=tk.W)
    totrows=totrows+1

    global bbox
    bbox=(0,0,0,bbox[3]+33)  
    canva.configure(scrollregion=bbox)
    canva.yview_moveto("1.0")
    dirs_table.append("")

def supprimer_ligne():
    global totrows
    global dirs_table
    global sample_table
    i=totrows
    try :
        buttons_frame.nametowidget("sampleId"+str(i-1)).destroy()
        buttons_frame.nametowidget("text"+str(i-1)).destroy()
        buttons_frame.nametowidget("folder_button"+str(i-1)).destroy()
    except KeyError :
        return
    totrows=totrows-1
    
    global bbox
    bbox = (0,0,0,bbox[3]-33)
    canva.configure(scrollregion=bbox)
    del dirs_table[-1]

def _bound_to_mouse_wheel(event):
    canva.bind_all("<MouseWheel>",_on_mousewheel_windows)
    canva.bind_all("<Button-4>", fp(_on_mousewheel_linux,scroll=-1))
    canva.bind_all("<Button-5>", fp(_on_mousewheel_linux,scroll=1))

def _unbound_to_mouse_wheel(event):
    canva.unbind_all("<MouseWheel>")
    canva.unbind_all("<Button-4>")
    canva.unbind_all("<Button-5>")

def _on_mousewheel_windows(event):
    canva.yview_scroll(int(-1*(event.delta/120)), "units")

def _on_mousewheel_linux(event, scroll):
    canva.yview_scroll(int(scroll), "units")

def disable(children):
    for child in children :
        child.configure(state="disable")

def enable(children):
    for child in children :
        child.configure(state="normal")

## Fonction Principale appelée quand click sur bouton "LANCER"
def run():
    # Apparition de l'icone de chargement
    label.grid(column=1, row=5, columnspan=1, rowspan=1, sticky=tk.E)
    
    # Désactivation de tout les widgets
    disable(buttons_frame.winfo_children())
    plus_button.configure(state="disable")
    moins_button.configure(state="disable")
    run_button.configure(state="disable")
    out_folder_button.configure(state="disable")

    # Timer démarre
    start_time = time.time()

    # On récupère les infos dans le formulaire des dossiers et noms d'échantillons
    global dirs_table
    global sample_table
    global ratios_files
    global outdir
    global elapsed_time
    elapsed_time = 0
    sample_table=[]
    ratios_files=[]

    # Lever d'erreur si pas de ligne
    if len(dirs_table)==0 :
            reinitialiser()
            label.grid_forget()
            messagebox.showwarning("ErreurTk 2","Il faut insérer une ligne\net remplir le formulaire !", icon="error")
            return
    for i in range(0,len(dirs_table)) :
        # On leve l'erreur si il manque un dossier dans une ligne
        if dirs_table[i]=='' :
            reinitialiser()
            label.grid_forget()
            messagebox.showwarning("ErreurTk 1","Il manque un nom de dossier", icon="error")
            return
        # On récupère les sample Ids
        else :
            sample_table.append(buttons_frame.nametowidget("sampleId"+str(i+1)).get())
    
    # On récupère les paramètres
    params=[]
    params.append(var_w.get())
    params.append(var_cnp.get())
    params.append(cna.get())
    params.append(root.nametowidget("text_out_folder").get('1.0','end'))

    # Lever d'erreurs diverses
    try :
        params.append(int(cna.get()))
    except(ValueError) :
        params=[]
        reinitialiser()
        label.grid_forget()
        messagebox.showwarning("ErreurTk 3","Il faut spécifier un nombre de CNA contigus minimum", icon="error")
        return

    if params[3]=='\n' :
        reinitialiser()
        label.grid_forget()
        messagebox.showwarning("ErreurTk 5","Il faut spécifier dossier de sortie !", icon="error")
        return

    # On recupère les noms de fichiers de ratios dans les répertoires
    for dir in dirs_table :
        ratios_files.append(functions.find_ratios_files(dir))

    for file, dir in zip(ratios_files, dirs_table) :
        if file=="":
            reinitialiser()
            label.grid_forget()
            messagebox.showwarning("ErreurTk 6","Fichier de Ratios introuvable dans: "+dir, icon="error")
            return

    cutoff=int(params[2])
    outdir=params[3][0:len(params[3])-1]
    annotation_file="../param_data/gencode.v19.annotation.genes.protein_coding.known.gtf"
    outSegment_file_w=outdir+"/Segments_"+str(cutoff)+"CNAcontigus_wilfried.csv"
    outStats_file_w=outdir+"/Stats_wilfried.csv"
    outSegment_file_c=outdir+"/Segments_"+str(cutoff)+"CNAcontigus_freec.csv"
    outStats_file_c=outdir+"/Stats_freec.csv"

    ############ MÉTHODE 1 : Par Wilfried Gouraud (ICO - Nantes St Herblain) ############
    if params[0]==1:
        cpt=0
        stats=[]
        prog=0
        step=100/len(sample_table)
        for file, sampleId in zip(ratios_files,sample_table) :
            ## Créer répertoire de sortie pour chaque sample
            if params[1]==1:
                if (os.path.exists(outdir+"/"+sampleId)==False):
                    os.mkdir(outdir+"/"+sampleId)
                else :
                    reinitialiser()              
                    label.grid_forget()
                    messagebox.showwarning("ErreurTk 8 :",'Le nom de dossier: "'+outdir+'/'+sampleId+'" est deja utilisé.')
                    return
            
            out_svg=outdir+"/"+sampleId+"/"+sampleId+"_CNP_wilfried.svg"

            ## Lire les fichiers
            ratiosDict=functions.lire_fichier(file, "ratio")
            # On enleve les Chromosomes X et Y
            ratiosDict = ratiosDict[list(ratiosDict.columns)][ratiosDict["Chromosome"]!='X']
            ratiosDict = ratiosDict[list(ratiosDict.columns)][ratiosDict["Chromosome"]!='Y']
            ratiosDict["Chromosome"]=pd.to_numeric(ratiosDict["Chromosome"])
            annotationDict=functions.lire_fichier(annotation_file, "annot")
            ## Segmentation des Ratios
            segmentsDict=functions.segmentation(ratiosDict)
            ## Filtering segmentsDict to a value
            segmentsDict_filtered=functions.filtering(segmentsDict,cutoff)
            segmentsDict_filtered.index = range(segmentsDict_filtered.shape[0])

            ## Annotation des segments
            functions.annotation(segmentsDict_filtered,annotationDict)

            ## Enregistrer segments dans le fichier de sortie
            if cpt==0 :
                fichier = open(outSegment_file_w, "w")
                fichier.write("Sample,Chr,Segment begin,Segment end,Segment size,CNA number,Copy number median,Del (<=1.5cn) / Amp (>=3cn),Genes\n")
                fichier.close()            
            functions.enregistrer_segments(outSegment_file_w,segmentsDict_filtered,sampleId)
            
            cpt=cpt+1
            ## Création statistiques
            tot=len(ratiosDict["Chromosome"])
            chrs=list(functions.unique(sorted(list(ratiosDict["Chromosome"]))))
            ### Stats 
            stats_list=str(sampleId)+","+str(tot)+","
            header="Sample,Tot\\Chr,"
            for chr, h in zip(chrs,range(0,len(chrs))) :
                header=header+str(chr)+","
                index_chr=list(filter(lambda x : (chr==ratiosDict["Chromosome"][x]),range(len(ratiosDict["Chromosome"]))))
                stats_list=stats_list+str(len(index_chr))+","

            if params[1]==1:
                functions.plot_wilfried(ratiosDict, segmentsDict, sampleId, out_svg)
            ## Save stats_val
            stats.append(stats_list)
            prog=prog+step
            end_time = time.time()
            elapsed_time=end_time-start_time
            progression(prog)
        ## Enregistrer stats dans le fichier de sortie
        functions.enregistrer_stats(outStats_file_w,stats,header)

    ############ MÉTHODE 2 : Filtrage des CNVs de control-FREEC ############
    else :
        cpt=0
        stats=[]
        prog=0
        step=100/len(sample_table)
        global cnvs_files
        cnvs_files=[]
        # On recupère les noms de fichiers de ratios dans les répertoires
        for dir in dirs_table :
            cnvs_files.append(functions.find_cnvs_files(dir))

        for file, dir in zip(cnvs_files, dirs_table) :
            pat = re.compile(".+p[.]value.+")
            if file=="":
                reinitialiser()
                label.grid_forget()
                messagebox.showwarning("ErreurTk 7","Fichier des CNVs introuvable dans: "+dir, icon="error")
                return
            
            if bool(re.search("p.value",file))==False :
                reinitialiser()
                label.grid_forget()
                messagebox.showwarning("ErreurTk 10","La significativité des CNVs n'a pas été calculée, Arrêt.", icon="error")
                return
            
        for file, cnvs_file, sampleId in zip(ratios_files,cnvs_files,sample_table) :
            ## Créer répertoire de sortie pour chaque sample
            if (os.path.exists(outdir+"/"+sampleId)==False):
                os.mkdir(outdir+"/"+sampleId)
            else :             
                test=messagebox.askquestion("Attention !",'Le nom de dossier: "'+outdir+'/'+sampleId+'" est deja utilisé, continuer ?')
                if test=="no" :
                    reinitialiser()
                    label.grid_forget()   
                    return
                
            out_svg=outdir+"/"+sampleId+"/"+sampleId+"_CNP_freec.svg"
            out_freecs=outdir+"/"+sampleId+"/"+sampleId+"_segments_IGV.seg"
            ## Lire les fichiers
            ratiosDict=functions.lire_fichier(file,"ratio")
            cnvs=functions.lire_fichier(cnvs_file, "cnv")
            freecs=functions.freec2absolute(ratiosDict)
            annotationDict=functions.lire_fichier(annotation_file, "annot")

            ## Enregistrer les segments IGVs
            fichier = open(out_freecs, "w")
            fichier.write("#type=COPY_NUMBER\n\'ID\tchrom\tloc.start\tloc.end\tnum.mark\tseg.mean\n")
            fichier.close()     
            functions.enregistrer_freecs(out_freecs, freecs, sampleId)

            ## Création statistiques
            tot=len(ratiosDict["Chromosome"])
            chrs=list(functions.unique(sorted(list(ratiosDict["Chromosome"]))))
            ### Stats 
            stats_list=str(sampleId)+","+str(tot)+","
            header="Sample,Tot\\Chr,"
            for chr, h in zip(chrs,range(0,len(chrs))) :
                header=header+str(chr)+","
                index_chr=list(filter(lambda x : (chr==ratiosDict["Chromosome"][x]),range(len(ratiosDict["Chromosome"]))))
                stats_list=stats_list+str(len(index_chr))+","
 
            for i in range(0,len(cnvs['chr'])) :
                for j in range(0,len(freecs["Chromosome"])) :
                    if (cnvs['start'][i]==freecs["Start"][j]-1 and cnvs['chr'][i]==freecs["Chromosome"][j]):
                        cnvs.loc[i,"CNAnumber"]=freecs['Num_Probes'][j]
                        cnvs.loc[i,"MedRatio"]=freecs['Segment_Mean'][j]

            cnvs_significatifs = cnvs[cnvs.columns][numpy.logical_and(cnvs["WilcoxonRankSumTestPvalue"]<=0.05,cnvs["KolmogorovSmirnovPvalue"]<=0.05)]
            cnvs_significatifs.index = range(cnvs_significatifs.shape[0])

            cnvs_significatifs_noNeutrals =  cnvs_significatifs[cnvs_significatifs.columns][cnvs_significatifs["status"] != "neutral"]
            cnvs_significatifs_noNeutrals_cutoff =  cnvs_significatifs_noNeutrals[cnvs_significatifs_noNeutrals.columns][cnvs_significatifs_noNeutrals["CNAnumber"] >= cutoff]
            cnvs_significatifs_noNeutrals_cutoff.index = range(cnvs_significatifs_noNeutrals_cutoff.shape[0])
            
            functions.annotation(cnvs_significatifs_noNeutrals_cutoff,annotationDict)

            ## Enregistrer segments dans le fichier de sortie
            if cpt==0 :
                fichier = open(outSegment_file_c, "w")
                fichier.write("Sample,Chromosome,Start,End,Size,Predicted Copy Number,number of CNAs in segment ,Alteration type,Genotype,%Uncertainty of predicted gentotype,Wilcoxon RankSum Test Pvalue,Kolmogorov-Smirnov Test Pvalue, Genes\n")
                fichier.close()     
            functions.enregistrer_cnvs(outSegment_file_c,cnvs_significatifs_noNeutrals_cutoff,sampleId)

            if params[1]==1:
                functions.plot_freec(ratiosDict,freecs, cnvs,sampleId,cutoff, out_svg)
            
            cpt=cpt+1
            ## Save stats_val
            stats.append(stats_list)
            end_time = time.time()
            elapsed_time=end_time-start_time
            prog=prog+step
            progression(prog)
        ## Enregistrer stats dans le fichier de sortie
        functions.enregistrer_stats(outStats_file_c,stats,header)

    # Processus terminé, Disparition de l'icone de chargment
    label.grid_forget()

    # On réactive les widgets

def lancer_thread():
    t= threading.Thread(target=run)
    t.start()

#Interface #####################################
global dirs_table
dirs_table=[]
totrows=1

# Fenetre
root = tk.Tk()
root.title("AppCNV")
root.minsize(550, 200)
#root.attributes('-topmost', True)
defaultbg = root.cget('bg')
tkfont.Font(font="TkFixedFont").actual()
font = tkfont.Font(font="TkFixedFont")

# si le 50 chars font 50*8 = 400 su 

root.grid_rowconfigure(1, weight=1)

root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=2)
root.grid_columnconfigure(2, weight=2)
root.grid_columnconfigure(3, weight=1)
root.grid_columnconfigure(5, weight=1)

## Titre en haut de la fenetre
tk.Label(root, 
      text="Traitement des fichiers Control-FREEC", 
      font=("Arial",25)).grid(row=0, 
                              column=1, 
                              columnspan=4, 
                              rowspan=1,  
                              padx=1, 
                              pady=20)

## Conteneur du Canva dans la colonne 2
frame1=tk.Frame(root, highlightbackground="grey", highlightthickness=1)
frame1.grid(row=1,
            column=1, 
            columnspan=2, 
            rowspan=1,  
            padx=10, 
            pady=0, 
            sticky="nsew")

## Ajout des boutons plus et moins dans la colonne 1
plus_button=tk.Button(frame1,
                      text="+", 
                      font=("Arial",20),
                      padx=0, pady=0,
                      width=3, 
                      bg="#4CAF50", fg = "white",
                      activebackground = "white", 
                      activeforeground="#4CAF50",
                      command=ajouter_ligne)
moins_button=tk.Button(frame1,
                       text="-",
                       font=("Arial",20),
                       padx=0, pady=0,
                       width=3,  
                       bg="#f44336", fg = "white",
                       activebackground = "white", 
                       activeforeground="#f44336",
                       command=supprimer_ligne)

frame1.rowconfigure(0, weight=1)
frame1.rowconfigure(1, weight=1)

frame1.columnconfigure(1, weight=1)

plus_button.grid(row=0, column=0, sticky="NSEW")
moins_button.grid(row=1, column=0, sticky="NSEW")

### Canva dans frame 1 (dans root)
canva = tk.Canvas(frame1, 
                width=500,
               highlightthickness=0)
canva.grid(row=0, column=1, rowspan=2, sticky="NSEW")

#### Scrollbar dans canva (dans frame1 (dans root))
scroll_bar = tk.Scrollbar(frame1, command=canva.yview)
scroll_bar.configure(command=canva.yview)

scroll_bar.grid(row=0, column=2, rowspan=2, sticky="NSEW")
canva.configure(yscrollcommand=scroll_bar.set)

#### Association du canva à la frame
buttons_frame = tk.Frame(canva)

#### Création de la fenetre canva
canva.create_window((0,0), window=buttons_frame, anchor="nw")
buttons_frame.update_idletasks()

#### Association scrollbar et canva
bbox=(0, 0, 0, 0)
canva.configure(scrollregion=bbox)
canva.bind("<Enter>", _bound_to_mouse_wheel)
canva.bind("<Leave>", _unbound_to_mouse_wheel)
canva.bind("<Configure>", resize)

##### Ajout de la première ligne
ajouter_ligne()


## Conteneur des boutons annexes en colonne 4 (la 3 étant occupé par la scrollbar du canva)
frame2=tk.Frame(root, 
                highlightbackground="grey", 
                highlightthickness=1,
                height=200)
frame2.grid(row=1, column=3, 
            columnspan=2, rowspan=1,  
            padx=10, pady=0, sticky="NSWE")
frame2.grid_rowconfigure(2, weight=1)
frame2.grid_rowconfigure(4, weight=1)
frame2.grid_columnconfigure(0, weight=1)


### Label des choix de méthodes
tk.Label(frame2, 
      text="Méthode :", 
      font=("Arial",14)).grid(row=0, column=0, 
                              columnspan=1, rowspan=1,  
                              padx=20, pady=20, sticky=tk.E)

#### Boutons méthode Wilfried
var_w=tk.IntVar()
var_w.set(1)
bouton_w = tk.Radiobutton(frame2, text='Wilfried',value=1,variable=var_w)
bouton_w.grid(row=0, column=1, columnspan=1, rowspan=1,  padx=20, pady=1, sticky=tk.W)

#### Boutons méthode FREEC
bouton_c = tk.Radiobutton(frame2, text='control-FREEC', value=2,variable=var_w)
bouton_c.grid(row=1, column=1, columnspan=1, rowspan=1, padx=20, pady=1, sticky=tk.W)

### Séparateur horizontal
ttk.Separator(frame2, orient='horizontal').grid(row=2, column=0, 
                                                columnspan=2, rowspan=1, 
                                                padx=20 ,sticky=tk.EW)

### Label du choix du CNP
tk.Label(frame2, text="CNP :", font=("Arial",13)).grid(row=3, column=0, 
                                                    columnspan=1, rowspan=1,  
                                                    padx=20, pady=1, sticky="E")

#### Bouton oui du CNP
var_cnp=tk.IntVar()
bouton_cnp = tk.Checkbutton(frame2, text='oui',onvalue=1, offvalue=0, var=var_cnp)
bouton_cnp.grid(row=3, column=1, columnspan=1, rowspan=1,  padx=20, pady=1, sticky=tk.W)

### Séparateur horizontal
ttk.Separator(frame2, orient='horizontal').grid(row=4, column=0, 
                                                columnspan=2, rowspan=1, 
                                                padx=20 ,sticky=tk.EW)

tk.Label(frame2, 
      text="     Nombre de\nCNA contigus :", 
      font=("Arial",13)).grid(row=5, column=0, 
                              columnspan=1, rowspan=1,  
                              padx=20, pady=20, sticky=tk.E)

cna = tk.Spinbox(frame2, from_= 2, to= 100000, width=10)
cna.grid(row=5, column=1, 
       columnspan=1, rowspan=1,  
       padx=20, pady=1, sticky=tk.W)

## Séparateur horizontal hors frame 1 (Séparateur entre le haut et le bas)
ttk.Separator(root, orient='horizontal').grid(row=2, column=1, 
                                              columnspan=4, rowspan=1, 
                                              pady=20 ,sticky=tk.EW)

## Label pour le dossier de sortie
tk.Label(root, 
      text="Dossier de sortie :", 
      font=("Arial",13)).grid(row=3, column=1, 
                              columnspan=1, rowspan=1, pady=5)

### Zone d'affichage du dossier de sortie
out_folder = tk.Text(root, width=70, height=1, state=tk.DISABLED, name="text_out_folder", bg=defaultbg)
out_folder.grid(row=3, column=2, columnspan=1, rowspan=1, pady=5)

### Bouton pour soummettre le dossier de sortie
out_folder_button=tk.Button(root, 
                        text="Soumettre un Dossier",
                        name="out_folder_button",
                        command= lambda : soumettre_dossier_sortie(), 
                        bg="#555555", fg="white", 
                        activeforeground="#555555", 
                        activebackground="white")
out_folder_button.grid(row=3, column=3, columnspan=2, rowspan=1, pady=5)

## Séparateur horizontal hors frame 1 (Séparateur entre le haut et le bas)
ttk.Separator(root, orient='horizontal').grid(row=4,
                                              column=1,
                                              columnspan=4,
                                              rowspan=1,
                                              pady=20 ,
                                              sticky=tk.EW)

## Ajout du bouton RUN
run_button=tk.Button(root,
                      text="Lancer", 
                      font=("Arial",20),
                      padx=0, pady=0,
                      width=15, height=2, 
                      bg="#008CBA", fg = "white",
                      activebackground = "white", 
                      activeforeground="#008CBA",
                      command=lancer_thread)
run_button.grid(row=5, column=3, columnspan=1, rowspan=2, pady=20)

## Ajout de la progress bar
pb = ttk.Progressbar(
    root,
    orient='horizontal',
    mode='determinate',
    length=500,
    value=0.0
)
pb.grid(column=2, row=5, columnspan=1, padx=10, pady=20)


## Valeur de progression
value_label = ttk.Label(root, text=update_progress_label)
value_label.grid(column=2, row=6, columnspan=1)
value_label['text'] = update_progress_label()

image1 = Image.open("../img/test.gif")
framesTotal = image1.n_frames
animation = [tk.PhotoImage(file="../img/test.gif", format=f'gif -index {i}') for i in range(framesTotal)]

label=tk.Label(root)

# Boucle principale
root.after(0, update, 0)
root.mainloop()

