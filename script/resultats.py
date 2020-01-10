# -*- coding: utf-8 -*-
""" Importations """
# Pour les opérations sur le fichier XML
from lxml import etree
from collections import Counter
import re

# Pour les graphes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

def stat_events(filepath):
    """
    Parse le fichier XML et affiche les différents thèmes qui apparaissent dans les volumes et combien de fois ils apparaissent.
    """
    cnt = Counter()
    
    tree = etree.parse(filepath)
    
    # Les différents thèmes/genres
    genres = []
    for resume_plot in tree.xpath("/root/volume/summary_plot/event"):
        genres.append(resume_plot.get("genre"))

    # Compter le nombre de chapitres par thème
    for element in genres:
        cnt[element] +=1
    
    # Affichage des thèmes et du nombre de chapitres qui les contient
    with open("thematique.txt", "w") as f:
        f.write("Nombre de chapitres par thème : \n")
    
        for k, v in cnt.items():
            f.write("\t{} : {}\n".format(k, v))
    
    # Affichage du camembert
    x, labels = list(), list()
    for k, v in cnt.items():
        x.append(int(v))
        labels.append(str(k))
    
    f = plt.figure(figsize = (8, 8), dpi=100)
    plt.pie(x, 
            labels=labels,
            autopct = lambda x: str(round(x, 2)) + '%',
            pctdistance = 0.6,
            labeldistance = 1.1)
    
    plt.savefig("thematique_camembert.png", bbox_inches="tight")
    
    return "stat_events done"

def stat_casualties(filepath, type, type2):
    """
    Parse le fichier XML et affiche le type de mort et son nombre d'occurence.
    """
    cnt = Counter()
    
    tree = etree.parse(filepath)
    
    # Trouver les causes de mort
    causes = []
    for cause_mort in tree.xpath("/root/volume/casualties/{}/{}/informations".format(type, type2)):
        if "(" in cause_mort.text:
            temp = cause_mort.text
            temp2 = temp[temp.find("(")+1:temp.find(")")]
            causes.append(temp2)
        
    for cause in causes:
        cnt[cause.lower()] +=1
    
    # Affichage texte
    with open("{}.txt".format(type), "w") as f:
        f.write("Nombre de morts par cause ({}): \n".format(type))
    
        for item in cnt.most_common():
            f.write("\t{} : {}\n".format(item[0], item[1]))
    
    # Affichage de l'histogramme
    x, labels = list(), list()
    for item in cnt.most_common(10):
        x.append(int(item[1]))
        labels.append(item[0])
    
    f = plt.figure(figsize = (5, 4), dpi=100)
    plt.bar(range(10), x,
            width = 0.6, 
            color = "red",
            edgecolor = "black",
            linewidth = 1)
    plt.xticks(range(10),
            labels,
            rotation = 45)
    plt.tight_layout() # évite le problème d'affichage des labels
    
    plt.savefig("morts_histogramme_{}.png".format(type), bbox_inches="tight")
    
    return "stat_casualties ({}) done".format(type)

def main():
    filepath = "donnees.xml"
    print(stat_events(filepath))
    print(stat_casualties(filepath, "victims", "victim"))
    print(stat_casualties(filepath, "deceased", "dead"))

if __name__ == '__main__':
    main()