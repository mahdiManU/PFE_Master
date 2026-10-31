"""
structural.py - structural errors (family "S" in the thesis) and legal-text lookup.

Structural errors are anti-patterns in how gateways are combined:

    Deterministic deadlock                   exclusive gateway -> parallel gateway
    Deterministic lack of synchronization    parallel gateway  -> exclusive gateway
    Nondeterministic lack of synchronization inclusive gateway -> exclusive gateway
    Nondeterministic deadlock                inclusive gateway -> parallel gateway

Also detected: "dead tasks" (tasks that nothing leads to).

The main entry point is message(bpmnfile, bpmnfile2, fichier_loi): it finds the
errors, colours the faulty paths red, renames the tasks involved, then looks up
the legal articles concerned (trouver_article) and returns
(french_messages, english_messages).

The file has three parts:
    1. Legal text helpers   - lire_decrets, extract_articles, ramener_art, ...
    2. BPMN reading helpers - get_element_type, get_task, get_annotation2, ...
    3. S detectors          - verif, verif2, verif3, verif4, colorier_chemin, message
"""
import xml.etree.ElementTree as ET
import re
from .bpmn_utils import supprimer_doublons, color_task, PALETTE_STRUCTURAL

# --- 1. legal text helpers -----------------------------------------------

def clean_list(mixed_list):
    # Utiliser une compréhension de liste pour filtrer les éléments vides (listes vides et chaînes vides)
    return [item for item in mixed_list if item]

def lire_decrets(fichier):
    with open(fichier, 'r', encoding='utf-8') as f:
        texte = f.read()
    
    # Séparation des décrets en utilisant la chaîne "Decree n°"
    decrets = texte.split("Decret n")[1:]
    
    # Ajout de "Decree n°" au début de chaque décret pour le reformater
    decrets = ["Decret n" + decree.replace("\n", "") for decree in decrets]
    
    return decrets

def extract_articles(decret_text):
    # Define the pattern to match each article
    pattern = r'Art. \d+\..*?(?=Art. \d+\.|$)'
    
    # Use regular expressions to find all articles
    articles = re.findall(pattern, decret_text, re.DOTALL)
    
    return articles

def ramener_art(nom_article,nom_fichier):
    
    liste_decrees = lire_decrets(nom_fichier)
    
    for i in liste_decrees:
        temp = extract_articles(i)
        
        for j in temp:
            
            if(nom_article.__str__().split('/')[1] in j):
                return nom_article.split('/')[0]+j
    return ''

def taches_dans_article(article,listedestaches):
    cpt = 0
    for i in listedestaches:
        if (i.lower() in article.lower()):
            cpt +=1
    if(cpt <= len(listedestaches) and cpt >=1):
        return True
    else:
        return False

def valide_type_err(typeErr,articles):
    if("(Deterministic deadlock)" in typeErr):
        if((("either" in articles) and ("or" in articles)) or (("soit" in articles) and ("et" in articles))):
            return True
    if("(Deterministic lack of synchronization)" in typeErr):
        if((("and" in articles) and ("or" in articles)) or (("et" in articles) and ("ou" in articles))):
            return True
    if("(Nondeterministic lack of synchronization)" in typeErr):
        if((("or" in articles) and ("then" in articles)) or (("ou" in articles) and ("puis" in articles))):
            return True
    if("(Nondeterministic deadlock)" in typeErr):
        if((("and" in articles) and ("or" in articles)) or (("et" in articles) and ("puis" in articles))):
            return True
    return False

def trouver_article(nom_fichier, nom_article ,typeErr,listeTaches):
    mesArticles = []
    
    for i in nom_article:
        if(i.__len__()>3):
         mesArticles.append(ramener_art(i,nom_fichier))
    mesArticles = supprimer_doublons(mesArticles)
    nom_article = supprimer_doublons(nom_article)
 
    if(("(Deterministic deadlock)" in typeErr) and (taches_dans_article(mesArticles.__str__(),listeTaches)) and (valide_type_err(typeErr,mesArticles.__str__()))): 
            return "probleme dans either // or dans les aticles suivants : "+mesArticles.__str__()+"#Reviser :"+nom_article.__str__(),"problem in either // or in the following articles : "+mesArticles.__str__()+"#Revise :"+nom_article.__str__()
    if(("(Deterministic lack of synchronization)" in typeErr) and (taches_dans_article(mesArticles.__str__(),listeTaches)) and (valide_type_err(typeErr,mesArticles.__str__()))):
            return "problem in and // or in the following articles:: "+mesArticles.__str__()+"#Reviser :"+nom_article.__str__(),"problem in and // or in the following articles:: "+mesArticles.__str__()+"#Revise :"+nom_article.__str__()
    if(("(Nondeterministic lack of synchronization)" in typeErr) and (taches_dans_article(mesArticles.__str__(),listeTaches)) and (valide_type_err(typeErr,mesArticles.__str__()))):
            return "probleme dans or // then dans les articles suivants: "+mesArticles.__str__()+"#Reviser :"+nom_article.__str__(),"problem in or // then in the following articles : "+mesArticles.__str__()+"#Revise :"+nom_article.__str__()
    if(("(Nondeterministic deadlock)" in typeErr) and (taches_dans_article(mesArticles.__str__(),listeTaches)) and (valide_type_err(typeErr,mesArticles.__str__()))):
            print(nom_article.__str__())
            return "probleme dans and // or dans l'article suivant:"+mesArticles.__str__()+"#Reviser :"+nom_article.__str__(),"problem in and // or in the following articles:"+mesArticles.__str__()+"#Revise :"+nom_article.__str__()
    
    return "Ambiguite dans l'article : "+mesArticles.__str__()+"#Reviser : " +mesArticles.__str__(),"Ambiguity in the article : "+mesArticles.__str__()+"#Revise : " +mesArticles.__str__()

# --- 2. BPMN reading helpers ---------------------------------------------
def get_element_type(id,bpmnfile):
     with open(bpmnfile, 'r') as file:
       lines = file.readlines()
     for i in lines:
         if(('id="'+id+'"')in i):
             match = re.match(r'^\s*<(\w+)', i)
             if(match):
              return match.group(1)

def get_task(bpmnfile,id_tache):
   with open(bpmnfile, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if (("<task" in line) or ("<sendTask" in line) or ("<receiveTask" in line)) and (id_tache in line):
            msg = re.search(r'name="([^"]+)"', line)
   return msg.group(1)

def get_annotation2(bpmn_file_path,id):
   msg = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<association" in line) and (id in line):
         match = re.search(r'targetRef="([^"]+)"', line)
         temp = match.group(1)
         for line2 in lines : 
             if temp in line2 and  '<textAnnotation' in line2:
                msg = re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1])
                if (msg):
                    return msg.group(1)
   return msg

def has_no_next(bpmnfile,id):
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for i in lines:
        if(('sourceRef="'+id) in i):
            return True
    return False

def get_valide(bpmnfile,id):
     cpt1 = 0 
     cpt2 = 0
     with open(bpmnfile, 'r') as file:
        lines = file.readlines()
     for i in lines:
         if(("sourceRef=" +'"'+id) in i):
             cpt1 +=1
         if(("targetRef=" +'"'+id) in i):
             cpt2 +=1
     return cpt2 > cpt1

def get_all_exclusiveG(bpmnfile):
     my_list = []
     with open(bpmnfile, 'r') as file:
        lines = file.readlines()
     for i in lines:
         if ("<exclusiveGateway" in i):
             match = re.search(r'id="([^"]+)"', i)
             my_list.append(match.group(1))
     return my_list

def get_all_inclusiveG(bpmnfile):
     my_list = []
     with open(bpmnfile, 'r') as file:
        lines = file.readlines()
     for i in lines:
         if ("<inclusiveGateway" in i):
             match = re.search(r'id="([^"]+)"', i)
             my_list.append(match.group(1))
     return my_list

def get_all_parallelG(bpmnfile):
     my_list = []
     with open(bpmnfile, 'r') as file:
        lines = file.readlines()
     for i in lines:
         if ("<parallelGateway" in i):
             match = re.search(r'id="([^"]+)"', i)
             my_list.append(match.group(1))
     return my_list

def count_distinct_values(lst):
    distinct_values = set(lst)
    return len(distinct_values)

def remove_duplicates(list_of_lists):
    # Convert each sublist to a tuple so it can be added to a set
    set_of_tuples = {tuple(sublist) for sublist in list_of_lists}
    # Convert the set of tuples back to a list of lists
    return [list(t) for t in set_of_tuples]
    
# --- 3. S detectors ------------------------------------------------------    
def dfs(bpmnfile,graph, start, end, path=[], paths=[]):
    path = path + [start]
    
    if start == end:
       paths.append(path)
       return paths
    if((get_element_type(start,bpmnfile)!="endEvent") and (start in graph)):
        
        
        for neighbor in graph[start]:
            if neighbor not in path:
                paths = dfs(bpmnfile,graph, neighbor, end, path, paths)
    return paths

def get_gateway_paths(xml_file, start_gateway_id, end_gateway_id):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    graph = {}
    for sequenceFlow in root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow') + root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}messageFlow'):
        sourceRef = sequenceFlow.get('sourceRef')
        targetRef = sequenceFlow.get('targetRef')
        if sourceRef not in graph:
            graph[sourceRef] = []
        graph[sourceRef].append(targetRef)

    all_paths = dfs(xml_file,graph, start_gateway_id, end_gateway_id)

    # Filter paths to keep only those starting from start_gateway_id and ending at end_gateway_id
    gateway_paths = [path for path in all_paths if path[0] == start_gateway_id and path[-1] == end_gateway_id]

    return gateway_paths

def chemin_valide(maliste):
    liste2 = []
    for i in maliste:
        liste2.append(i[1])
    if(count_distinct_values(liste2)>=2):
        return True
    return False

def verif(bpmnfile):
    listef = []
    exclu = get_all_exclusiveG(bpmnfile)
    para = get_all_parallelG(bpmnfile)
    inclu= get_all_inclusiveG(bpmnfile)
    
    list_finale = []
    for i in exclu:
        for j in para:
            list_finale = get_gateway_paths(bpmnfile,i,j)
            if((list_finale.__len__() >= 2) and (chemin_valide(list_finale))):
              listef.append(list_finale)
        list_finale = []
         
    return listef , exclu , para , inclu
    
def verif2(bpmnfile):
    listef = []
    exclu = get_all_exclusiveG(bpmnfile)
    para = get_all_parallelG(bpmnfile)
    list_finale = []
    for i in exclu:
        for j in para:
            list_finale = get_gateway_paths(bpmnfile,j,i)
            print(get_gateway_paths(bpmnfile,j,i).__str__())
            nb = 0
            if((list_finale.__len__() >= 2) and (chemin_valide(list_finale)) and get_valide(bpmnfile,i)):
              print("hello lala")
              
              for t in list_finale:
                  for k in t:
                     if(get_element_type(k,bpmnfile) == "parallelGateway"):
                         nb +=1
                  if(not(nb%2 == 0)): 
                    print("chaima")  
                    listef.append(list_finale)
        list_finale = []
              
    return listef

def verif3(bpmnfile):
    listef = []
    exclu = get_all_exclusiveG(bpmnfile)
    inclu= get_all_inclusiveG(bpmnfile)
    list_finale = []
    for i in exclu:
        for j in inclu:
            list_finale = get_gateway_paths(bpmnfile,j,i)
            if((list_finale.__len__() >= 2) and (chemin_valide(list_finale))):
              listef.append(list_finale)
        list_finale = []
              
    return listef 

def verif4(bpmnfile):
    listef = []
    para = get_all_parallelG(bpmnfile)
    inclu= get_all_inclusiveG(bpmnfile)
    list_finale = []
    for i in para:
        for j in inclu:
            list_finale = get_gateway_paths(bpmnfile,j,i)
            if((list_finale.__len__() >= 2) and (chemin_valide(list_finale))):
              listef.append(list_finale)
        list_finale = []
              
    return listef 

def modifier_noms(bpmnfile, id_liste, nouveau_nom):
   with open(bpmnfile, 'r') as file:
     lines = file.readlines()
   nv_lines = []
   for i in id_liste:
       with open(bpmnfile, 'r') as file:
         lines = file.readlines() 
       for line in lines:
           if(("<task" in line) and (i in line)):
               if("name=" not in line):
                    
                    nv_line = re.sub(r'(id="[^"]+")', r'\1 name="erreur '+nouveau_nom+'"', line)
                    
                    nv_lines.append(nv_line)
               if("name=" in line):
                   
                    nv_line = re.sub(r'name="([^"]+)"', r'name="erreur '+nouveau_nom+'"', line)
                    nv_lines.append(nv_line)
           else:
               nv_lines.append(line)
       with open(bpmnfile, 'w') as file:
            file.truncate(0)
            file.writelines(nv_lines)
       nv_lines = []

def color_elements_in_xml(file_path, element_ids):
    # Charger le fichier XML
    tree = ET.parse(file_path)
    root = tree.getroot()

    # Définir l'espace de noms utilisé dans le fichier XML
    namespace = {'bpmn': 'http://www.omg.org/spec/BPMN/20100524/MODEL',
                 'bpmndi': 'http://www.omg.org/spec/BPMN/20100524/DI',
                 'omgdi': 'http://www.omg.org/spec/DD/20100524/DI',
                 'omgdc': 'http://www.omg.org/spec/DD/20100524/DC',
                 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}

    # Parcourir les éléments à colorier
    for element_id in element_ids:
        # Trouver l'élément avec l'ID correspondant
        element = root.find('.//bpmn:BPMNShape[@id="{}"]'.format(element_id), namespaces=namespace)
        if element is not None:
            # Modifier les attributs de l'élément pour le colorier en rouge
            element.set('{http://bpmn.io/bpmn}fill', '#ffcdd2')
            element.set('{http://bpmn.io/bpmn}stroke', '#831311')

    # Enregistrer les modifications dans le fichier XML
    tree.write(file_path)

def colorier_chemin(bpmnfile):
    chemin  , exclu, para , inclu= verif(bpmnfile)

    chemin +=verif2(bpmnfile)
    chemin +=verif3(bpmnfile)
    chemin +=verif4(bpmnfile)
    retoure = []
   
    final = []
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for i in chemin:
        for j in i:
            for k in j:
                for t in lines:
                    if((k in t) and ("<bpmndi:BPMNShape" in t) and (' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n' not in t)):
                        
                        t= t[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
                       
                        final.append(t)
                        
                    else:
                        final.append(t)
                with open(bpmnfile, 'w') as file:
                    file.truncate(0)
                    file.writelines(final)
                    final=[]
                lines = []
                with open(bpmnfile, 'r') as file:
                   lines = file.readlines()
    return chemin ,exclu ,para , inclu 

def message(bpmnfile,bpmnfile2,fichier_loi):
    mesmessage , exclu, para ,inclu = colorier_chemin(bpmnfile)
    
    nvmsg = []
    nvmsgENG = []
    acti = []
    temp = []
    test = []
    err =0
    trr = 0
    for i in mesmessage:
        trr+=1
        if((i[0][0] in exclu) and (i[0][-1] in para)):
          nvmsg.append("Erreur S "+str(trr)+"# (Deterministic deadlock)")
          nvmsgENG.append("Error S "+str(trr)+"# (Deterministic deadlock)")
        if((i[0][-1] in exclu) and (i[0][0] in para)):
          nvmsg.append("Erreur S "+str(trr)+"# (Deterministic lack of synchronization)")
          nvmsgENG.append("Error S "+str(trr)+"# (Deterministic lack of synchronization)")
        if((i[0][-1] in exclu) and (i[0][0] in inclu)):
          nvmsg.append("Erreur S "+str(trr)+"# (Nondeterministic lack of synchronization)")
          nvmsgENG.append("Error S "+str(trr)+"# (Nondeterministic lack of synchronization)")
        if((i[0][-1] in para) and (i[0][0] in inclu)):
          nvmsg.append("Erreur S "+str(trr)+"# (Nondeterministic deadlock)")
          nvmsgENG.append("Error S "+str(trr)+"# (Nondeterministic deadlock)")
    for i in mesmessage:
        err+=1
        for j in i:
            modifier_noms(bpmnfile,j,"Erreur S "+str(err))
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for line in lines:
        if("<task" in line):
            match = re.search(r'id="([^"]+)"', line)
            acti.append(match.group(1))
    for id in acti:
        cpt = 0
        for line in lines:
            if(('targetRef="'+id) in line):
                cpt+=1
        if(cpt == 0):
            trr = trr+1
            temp.append(id)
            modifier_noms(bpmnfile,temp,"Erreur S "+str(trr))
            
            nvmsg.append("Erreur S "+str(trr)+"# tache sans source#"+get_annotation2(bpmnfile,id).__str__())
            colorier_task(bpmnfile,id)
            nvmsgENG.append("Error S "+str(trr)+"# dead task#"+get_annotation2(bpmnfile,id).__str__())
            temp = []
    
    taches = []
    for i in mesmessage:
        loi = []
        tache = [] 
        for j in i:
            for t in j:
                if(get_element_type(t,bpmnfile) == "task"):
                    loi.append(get_annotation2(bpmnfile,t))
                    tache.append(get_task(bpmnfile2,t))
        taches.append(tache)
        test.append(loi)
    arts = []
    artsENG = []
    for i in range(len(nvmsg)):
        if ('tache sans source' not in nvmsg[i]):
            fr , eng = trouver_article(fichier_loi,test[i],nvmsg[i],taches[i])
            arts.append(nvmsg[i]+"#"+fr) 
            artsENG.append(nvmsgENG[i]+"#"+eng)

        else:
            arts.append(nvmsg[i]) 
            artsENG.append(nvmsgENG[i])  
    return arts , artsENG

def colorier_task(bpmnfile, id_task):
    """Colour an element red (structural error)."""
    color_task(bpmnfile, id_task, PALETTE_STRUCTURAL)

