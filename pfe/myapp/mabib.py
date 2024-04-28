import xml.etree.ElementTree as ET
import re
def get_element_type(id,bpmnfile):
     with open(bpmnfile, 'r') as file:
       lines = file.readlines()
     for i in lines:
         if(('id="'+id+'"')in i):
             match = re.match(r'^\s*<(\w+)', i)
             if(match):
              return match.group(1)
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
def has_no_next(bpmnfile,id):
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for i in lines:
        if(('sourceRef="'+id) in i):
            return True
    return False

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
def get_all_exclusiveG(bpmnfile):
    exclusive_gateways = []
    tree = ET.parse(bpmnfile)
    root = tree.getroot()
    namespace = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
    for exclusiveGateway in root.findall('.//{}exclusiveGateway'.format(namespace)):
       exclusive_gateways.append(exclusiveGateway.get('id'))
    return exclusive_gateways
def get_all_inclusiveG(bpmnfile):
    exclusive_gateways = []
    tree = ET.parse(bpmnfile)
    root = tree.getroot()
    namespace = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
    for exclusiveGateway in root.findall('.//{}inclusiveGateway'.format(namespace)):
       exclusive_gateways.append(exclusiveGateway.get('id'))
    return exclusive_gateways
def get_all_parallelG(bpmnfile):
    parallel_gateways = []
    tree = ET.parse(bpmnfile)
    root = tree.getroot()
    namespace = '{http://www.omg.org/spec/BPMN/20100524/MODEL}'
    for paraGateway in root.findall('.//{}parallelGateway'.format(namespace)):
       parallel_gateways.append(paraGateway.get('id'))
    return parallel_gateways
def count_distinct_values(lst):
    distinct_values = set(lst)
    return len(distinct_values)
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
            if((list_finale.__len__() >= 2) and (chemin_valide(list_finale))):
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
def get_task(bpmnfile,id_tache):
   with open(bpmnfile, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<task" in line) and (id_tache in line):
            msg = re.search(r'name="([^"]+)"', line)
   return msg.group(1)

def message2(bpmnfile):
    mesmessage , exclu, para ,inclu = colorier_chemin(bpmnfile)
    print("helloo mahdi "+mesmessage.__str__())
    nvmsg = []
    acti = []
    temp = []
    err =0
    trr = 0
    for i in mesmessage:
        trr+=1
        if((i[0][0] in exclu) and (i[0][-1] in para)):
          nvmsg.append("erreur S "+str(trr)+" (Deterministic deadlock)")
        if((i[0][-1] in exclu) and (i[0][0] in para)):
          nvmsg.append("erreur S "+str(trr)+" (Deterministic lack of synchronization)")
        if((i[0][-1] in exclu) and (i[0][0] in inclu)):
          nvmsg.append("erreur S "+str(trr)+" (Nondeterministic lack of synchronization)")
        if((i[0][-1] in para) and (i[0][0] in inclu)):
          nvmsg.append("erreur S "+str(trr)+" (Nondeterministic deadlock)")
    for i in mesmessage:
        err+=1
        for j in i:
            modifier_noms(bpmnfile,j,"erreur S "+str(err))
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
            modifier_noms(bpmnfile,temp,"erreur S "+str(trr))
            
            nvmsg.append("erreur S "+str(trr)+" tache sans source")
            temp = []
    return nvmsg


def message(bpmnfile,bpmnfile2):
    mesmessage , exclu, para ,inclu = colorier_chemin(bpmnfile)
    
    nvmsg = []
    acti = []
    temp = []
    test = []
    err =0
    trr = 0
    for i in mesmessage:
        trr+=1
        if((i[0][0] in exclu) and (i[0][-1] in para)):
          nvmsg.append("erreur S "+str(trr)+" (Deterministic deadlock)")
        if((i[0][-1] in exclu) and (i[0][0] in para)):
          nvmsg.append("erreur S "+str(trr)+" (Deterministic lack of synchronization)")
        if((i[0][-1] in exclu) and (i[0][0] in inclu)):
          nvmsg.append("erreur S "+str(trr)+" (Nondeterministic lack of synchronization)")
        if((i[0][-1] in para) and (i[0][0] in inclu)):
          nvmsg.append("erreur S "+str(trr)+" (Nondeterministic deadlock)")
    for i in mesmessage:
        err+=1
        for j in i:
            modifier_noms(bpmnfile,j,"erreur S "+str(err))
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
            modifier_noms(bpmnfile,temp,"erreur S "+str(trr))
            
            nvmsg.append("erreur S "+str(trr)+" tache sans source")
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
    return nvmsg,test,taches
def valide_type_err(typeErr,articles):
    if("(Deterministic deadlock)" in typeErr):
        print((("either" in articles) and ("or" in articles)) or (("soit" in articles) and ("ou" in articles)))
        if((("either" in articles) and ("or" in articles)) or (("soit" in articles) and ("ou" in articles))):
            return True
    if("(Deterministic lack of synchronization)" in typeErr):
        if((("and" in articles) and ("or" in articles)) or (("et" in articles) and ("ou" in articles))):
            return True
    if("(Nondeterministic lack of synchronization)" in typeErr):
        if((("or" in articles) and ("then" in articles)) or (("ou" in articles) and ("puis" in articles))):
            return True
    if("(Nondeterministic deadlock)" in typeErr):
        if((("and" in articles) and ("then" in articles)) or (("et" in articles) and ("puis" in articles))):
            return True
    return False

def taches_dans_article(article,listedestaches):
    cpt = 0
    for i in listedestaches:
        if (i in article):
            cpt +=1
    if(cpt == len(listedestaches)):
        return True
    else:
        return False
def trouver_article(nom_fichier, nom_article ,typeErr,listeTaches):
    with open(nom_fichier, 'r', encoding='utf-8') as file:
        contenu = file.read()
        articles = re.findall(r'(Art\..*?)(?=(Art\.|\Z))', contenu, re.DOTALL)
    monArt = ""
    for i in nom_article:
            monArt += i
    mesArticles = []
    for titre in nom_article:
       print(titre)
       for article in articles:
            if(titre in article[0]):
                mesArticles.append(article[0])
    
    print( "test 1" + monArt)
    print(mesArticles)
    print("la liste est : " + listeTaches.__str__())
    print(taches_dans_article(mesArticles.__str__(),listeTaches))
    print(valide_type_err(typeErr,mesArticles.__str__()))
    print(mesArticles.__str__())
    if(("(Deterministic deadlock)" in typeErr) and (taches_dans_article(mesArticles.__str__(),listeTaches)) and (valide_type_err(typeErr,mesArticles.__str__()))):
            return "probleme dans either // or dans les aticles suivants : "+mesArticles.__str__()
    if(("(Deterministic lack of synchronization)" in typeErr) and (taches_dans_article(mesArticles.__str__(),listeTaches)) and (valide_type_err(typeErr,mesArticles.__str__()))):
            return "probleme dans and // or dans les articles suivants : "+mesArticles.__str__()
    if(("(Nondeterministic lack of synchronization)" in typeErr) and (taches_dans_article(mesArticles.__str__(),listeTaches)) and (valide_type_err(typeErr,mesArticles.__str__()))):
            return "probleme dans or // then dans les articles suivants: "+mesArticles.__str__()
    if(("(Nondeterministic deadlock)" in typeErr) and (taches_dans_article(mesArticles.__str__(),listeTaches)) and (valide_type_err(typeErr,mesArticles.__str__()))):
            return "probleme dans and // then dans les articles suivants : "+mesArticles.__str__()
    return "L'article spécifié n'a pas été trouvé dans le fichier."