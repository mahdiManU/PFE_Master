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
        print(has_no_next(bpmnfile,start))
        
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
    for sequenceFlow in root.findall('.//{http://www.omg.org/spec/BPMN/20100524/MODEL}sequenceFlow'):
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
    print(exclu)
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
    print(exclu)
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
    print(exclu)
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
                    print("imene")
                    nv_line = re.sub(r'name="([^"]+)"', r'name="erreur '+nouveau_nom+'"', line)
                    print(nv_line)
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
    print(chemin)
    final = []
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for i in chemin:
        for j in i:
            for k in j:
                for t in lines:
                    if((k in t) and ("<bpmndi:BPMNShape" in t) and (' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n' not in t)):
                        print(t)
                        t= t[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
                        print(t)
                        final.append(t)
                        print(k)
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
def message(bpmnfile):
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