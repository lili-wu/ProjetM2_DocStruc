# -*- coding: utf-8 -*-
"""**Importations**"""

import re
import requests
from bs4 import BeautifulSoup
from lxml import etree as ET

"""**Fonctions**"""

def extract_characters(url):
    """ Extraction des nouveaux personnages introduits par volume """
    html = requests.get(url) # on récupère le contenu
    soup = BeautifulSoup(html.text, 'lxml')

    characters = list()
    for line in soup.select("span[id*=\"Characters_introduced\"]"):
        character = list()
        h3_tag = line.parent
        next_div_tag = h3_tag.findNext("div")
        for elt in next_div_tag.find_all("table", class_="infobox people headerlink"):
            _ = list()
            for sent in elt.select('img'):
                chara = elt.text
                chara = re.sub('\n+', '\n', chara).strip()
                plus = chara.split('\n')
                _.append(('{}|{}|{}'.format(plus[0], plus[1:], sent.get('src'))))
            character.append(_)
        characters.extend(character)
    return characters

def extract_vd(url):
    """ Extraction des victimes et personnes décédées par volume """
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'lxml')

    victims, deceased = list(), list()
    for line in soup.select("span[id*=\"People\"]"):
        v, d = list(), list()
        h3_tag = line.parent
        next_div_tag = h3_tag.findNext("div")
        for elt in next_div_tag.find_all("table", class_="infobox people headerlink"):
            for sent in elt.select('img'):
                chara = elt.text
                if re.findall('Victim', chara):
                    chara = re.sub('\n+', '\n', chara).strip()
                    plus = chara.split('\n')
                    v.append(('{}|{}|{}'.format(plus[0], plus[1:], sent.get('src'))))
                if re.findall('Deceased', chara):
                    chara = re.sub('\n+', '\n', chara).strip()
                    plus = chara.split('\n')
                    d.append(('{}|{}|{}'.format(plus[0], plus[1:], sent.get('src'))))
        victims.extend(v)
        deceased.extend(d)
    return victims, deceased

def extract_cover(url):
    """ Extraction des couvertures de volume """
    html = requests.get(url) # on récupère le contenu
    soup = BeautifulSoup(html.text, 'lxml')

    cover = ""
    for line in soup.select('table[class="infobox"]'):
        cover = line.img['src']

    return cover

def extract(url):
    """ Extraction des données """
    html = requests.get(url) # on récupère le contenu
    soup = BeautifulSoup(html.text, "lxml") # on crée un objet pour traiter la page
    
    # pour les noms de chapitres par volume avec elements de plots
    resume = soup.select("td[style=\"padding:5px;\"]")
    volumes = dict()
    for line in soup.find_all("table"):
        vol = line.find("td", style="border: 0;")
        chap = line.find("td", style="border:0;   padding-left: 5px;")
        if vol != None:
            k = (int(vol.a.text[7:]), vol.a.text)
        if chap != None :
            v = chap.text.strip()
            pl = list()
            for plot in chap.find_all("a", href="/wiki/Detective_Conan_Wiki:Plot_Legend"):
                pl.append(plot["title"])
            if len(pl) > 0:
                v = "{} |{}".format( v, str(pl) )
            if volumes.get(k) == None:
                volumes[k] = [v]
            elif v != volumes[k][0]: # pour éviter un doublon sur le premier chapitre de chaque page web du site
                volumes[k].append(v)

    # pour le resume du volume
    contenu = ""
    summary = list()
    for item in resume:
        contenu = re.sub(r"\n", " ", str(item))
        tableau_sum = re.findall(r"<table.+</tbody></table>", contenu) # on ne veut pas du tableau dans le résumé
        sum = re.sub(tableau_sum[0], "", contenu) # car tableau_sum est une liste à 1 élément
        sum = re.sub("<[^<]+?>", "", sum)
        summary.append(sum)

    # pour le resume du plot
    summary_plot = list()
    for resum in soup.select("td[style=\"padding:5px;\"] > table"):
        _ = list()
        for sent in resum.find_all("td", style="border: none; padding-right: 10px;"):
            plot = sent.a
            _.append( ( "{}|{}".format( plot["title"], sent.text.strip() ) ) )
        summary_plot.append(_)
    
    return volumes, summary, summary_plot

"""**Transformation xml**"""

#print("Transformation en cours...")

cpt1, cpt2 = 1, 10

#Entête XML et lien avec sa grammaire RNG
print("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
print("<?xml-model href=\"../grammairedonnees.rng\" type=\"application/xml\" schematypens=\"http://relaxng.org/ns/structure/1.0\"?>\n")
print("<!DOCTYPE bibliographie SYSTEM \"../grammaire/donnees.dtd\">\n")

#Racine du document XML
print("<root>")

while cpt1 < 90:
    domain = "https://www.detectiveconanworld.com"
    url = "{}/wiki/Volume_{}-{}".format(domain, str(cpt1), str(cpt2)) # le lien vers le site
    
    volumes, summary, summary_plot = extract(url)
    
    # Affichage des données extraites
    i = 0
    for k, v in sorted(volumes.items(), key=lambda t: t[0][0]):
      print( "\t<volume n=\"{}\">".format(k[1][7:]) )
      
      cover = extract_cover("{}/wiki/Volume_{}".format(domain, k[0]))

      print( "\t\t<cover_url>{}</cover_url>".format(domain+cover) )

      print( "\t\t<chapters>")
      for c in v:
        c = re.sub("&", "&amp;", c)
        if "|" in c:
          chaine = c.split("|")
          print( "\t\t\t<chapter>\n\t\t\t\t<title>{}</title>\n\t\t\t\t<events>{}</events>\n\t\t\t</chapter>".format(chaine[0], chaine[1]) )

        else:
          print( "\t\t\t<chapter>\n\t\t\t\t<title>{}</title>\n\t\t\t</chapter>".format(c) )
      print("\t\t</chapters>")

      if "No summary yet" in summary[i]:
        print( "\t\t<summary>No summary yet</summary>" )
      else:
        print( "\t\t<summary>{}</summary>".format(summary[i]) )
      
      print("\t\t<summary_plot>")
      for s in summary_plot[i]:
        if "|" in s:
          chaine2 = s.split("|") 
          #print( "\t\t\t<event> <genre>{}</genre> <event_summary>{}</event_summary> </event>".format(chaine2[0], chaine2[1]) )
          print( "\t\t\t<event genre=\"{}\">{}</event>".format(chaine2[0], chaine2[1]) )
      print("\t\t</summary_plot>")

      charas = extract_characters("{}/wiki/Volume_{}".format(domain, k[0]))

      if len(charas) != 0: # on évite le cas sans characters
        print("\t\t<characters>")
        for chara in charas:
          chaine_chara = chara[0].split("|")
          print("\t\t\t<character>\n\t\t\t\t<name>{}</name>\n\t\t\t\t<informations>{}</informations>\n\t\t\t\t<image_url>{}</image_url>\n\t\t\t</character>".format(chaine_chara[0], chaine_chara[1], domain+chaine_chara[2]))
        print("\t\t</characters>")
      
      victims, deceased = extract_vd("{}/wiki/Volume_{}".format(domain, k[0]))

      if len(victims) != 0 or len(deceased) != 0:
        print("\t\t<casualties>")
        if len(victims) != 0:
          print("\t\t\t<victims>")
          for victim in victims:
            victim = victim.split("|")
            print("\t\t\t\t<victim>\n\t\t\t\t\t<name>{}</name>\n\t\t\t\t\t<informations>{}</informations>\n\t\t\t\t\t<image_url>{}</image_url>\n\t\t\t\t</victim>".format(victim[0], victim[1], domain+victim[2]))
          print("\t\t\t</victims>")
        if len(deceased) != 0:
          print("\t\t\t<deceased>")
          for d in deceased:
            d = d.split("|")
            print("\t\t\t\t<dead>\n\t\t\t\t\t<name>{}</name>\n\t\t\t\t\t<informations>{}</informations>\n\t\t\t\t\t<image_url>{}</image_url>\n\t\t\t\t</dead>".format(d[0], d[1], domain+d[2]))
          print("\t\t\t</deceased>")
        print("\t\t</casualties>")

      print("\t</volume>")
      i+=1

    cpt1+=10
    cpt2+=10

print("</root>")