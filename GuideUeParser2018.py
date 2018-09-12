import subprocess

from lxml import etree
import re
import json
# subprocess.Popen("pdftohtml -f 64 -l 100 -i -noframes -xml guide-UE-17-web2.pdf test.xml", shell=True)

uv = {}
liste_cours = []
uv_actuel = ""
uv_intermediaire = ""
commentaire = 0
texte_com = ""
texte_ant = ""
objectif_contenu = ""
programme_contenu = ""
top_uv = 0
objectif = 0
programme = 0
type_uv = ""
tree = etree.parse("newtest.xml")


for contenu in tree.xpath("/pdf2xml/page/text"):
    for b in contenu:
        if b.text is not None:
            contenu.text = b.text
    if bool(re.match(r"[^ ]", contenu.text)):
        
        if (int(contenu.get("height"))) == 11 and (int(contenu.get("left"))) > 700: #Parse les noms d'uv
            type_uv = contenu.text

        if (int(contenu.get("left"))) < 100:
            
            if (int(contenu.get("height"))) == 21: #Parse les noms d'uv
                top_uv = int(contenu.get("top")) #Positionnement de l'intitulé de l'uv

                if(re.search(r"[a-zA-Z]+", texte_com)): #Permet de vérifier si l'uv précédente contenait des coms
                    texte_com = re.sub(r'^Commentaire : ', '', texte_com)
                    uv[uv_actuel]["Commentaire"] = texte_com #Ajoute le com à l'uv précédente
                    texte_com = ""

                if(re.search(r"[a-zA-Z]+", texte_ant)): #Permet de vérifier si l'uv précédente contenait des anté
                    texte_ant = re.sub(r'^Antécédent : ', '', texte_com)
                    uv[uv_actuel]["Antecedent"] = texte_ant #Ajoute l'antécédent à l'uv précédente
                    texte_ant = ""

                # print ("Gauche : " + (contenu.text))
                uv[contenu.text] = {"nom":contenu.text}
                nb_cours = 0
                uv_actuel = contenu.text


            elif (int(contenu.get("height"))) == 12:
                # print ("Gauche : " + (contenu.text))
                if(bool(re.search(r"UE", contenu.text))):
                    contenu.text = re.sub(r'.$', '', contenu.text)
                    uv[uv_actuel]["Type"] = contenu.text

            elif (int(contenu.get("height"))) == 14: #Parse les types de cours TP et semestre ect et de tout ranger dans les cases
                if(bool(re.match(r"[^0-9]", contenu.text))):
                    if (bool(re.match(r"(Automne|Printemps)", contenu.text))):
                        # print("le sem est : " + contenu.text)
                        uv[uv_actuel]["Semestre"] = contenu.text    
                    elif((bool(re.search(r"(C|TD|TP|THE|PRJ)", contenu.text)))):
                        # print ("liste cours : " + (contenu.text))  
                        liste_cours.append(contenu.text)
                else:
                    if (bool(re.search(r"crédits", contenu.text))):
                        # print("search credit : " + contenu.text)
                        uv[uv_actuel]["Credits"] = contenu.text    

                    elif((bool(re.search(r"[0-9]{1,2} h", contenu.text)))):
                        # print ("heures cours : " + (contenu.text))      
                        uv[uv_actuel][liste_cours[nb_cours]] = contenu.text    
                        nb_cours += 1


            elif (int(contenu.get("height"))) == 10: #Parse les coms et antécédents
                if((bool(re.search(r"Antécédent", contenu.text)))):
                    commentaire = -1
                elif((bool(re.search(r"Commentaire", contenu.text)))):
                    commentaire = 1

                if(commentaire == 1): #Permet d'ajouter les commentaires petit a petit
                    if(texte_com == ""): 
                        texte_com = contenu.text
                    else:
                        texte_com += contenu.text

                elif(commentaire == -1): #Permet d'ajouter les antécédents petit a petit
                    if(texte_ant == ""): 
                        texte_ant = contenu.text
                    else:
                        texte_ant += contenu.text

        elif ((100 < (int(contenu.get("left"))) < 700) and not (bool(re.match(r"^[0-9]{2,3}$", contenu.text)))):

            # print(contenu.text)
            if (int(contenu.get("height"))) == 27 or (int(contenu.get("height"))) == 21:
                if (top_uv - 4 < int(contenu.get("top")) < top_uv + 4):
                    uv[uv_actuel]["intitule"] = contenu.text  
                    uv[uv_actuel]["type"] = type_uv  

                    objectif = 0
                    programme = 0
                    programme_contenu = re.sub(r'∙', '',programme_contenu)
                    programme_contenu = re.sub(r'Programme', '',programme_contenu)
                    if (uv_intermediaire == ""):
                        uv[uv_actuel]["programme"] = programme_contenu    
                        
                    else:
                        uv[uv_intermediaire]["programme"] = programme_contenu    
                    

            if(int(contenu.get("height"))) == 12:
                if(bool(re.search(r"(Objectif|objectif|OBJECTIF)", contenu.text))):
                    objectif = 1
                    programme = 0
                    objectif_contenu = ""

                if(bool(re.search(r"(Programme|programme|PROGRAMME)", contenu.text))):
                    uv_intermediaire = uv_actuel
                    objectif_contenu = re.sub(r'∙', '', objectif_contenu)
                    objectif_contenu = re.sub(r'objectif', '', objectif_contenu)
                    uv[uv_actuel]["objectif"] = objectif_contenu    
                    programme_contenu = ""
                    objectif = 0
                    programme = 1

            if objectif:
                objectif_contenu += contenu.text
            if programme:
                programme_contenu += contenu.text

#or user in tree.xpath("/users/user[metier='Veterinaire']/nom"):
 #   print(user.text)
# for key, value in uv.items():
#     print("\n")
#     print("UV : " + key)
#     for key2, value2 in value.items():
#         print(key2 + " " + value2)

new_uv = []
for key,value in uv.items():
    new_uv.append(value)

print(uv)        
with open("uvs.json", "w", encoding='utf-8') as f:
    json.dump(new_uv, f, ensure_ascii= False, sort_keys=True, indent=4)
