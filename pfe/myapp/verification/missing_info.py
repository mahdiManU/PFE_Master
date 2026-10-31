"""
missing_info.py - missing-information errors (family "MI" in the thesis).

modify_bpmn_file() is the entry point. It finds, in this order:

    Missing condition   an exclusive gateway with no label (its branches have no condition)
    Missing role        a pool or lane (participant) with no name
    Negative event      a task followed by an intermediate catch event only
    Legal vacuum        a task with no outgoing flow (nothing happens after it)
    Missing interval    a gateway whose conditions use < > = but miss one of the cases

Every faulty element is coloured orange and renamed "erreur MI n" in the diagram.
Each error gives a message "Erreur MI n # type # legal text # recommendation"
(french and english lists); rapport.py splits it on "#".

To add a new kind of missing information: write a detector inside
modify_bpmn_file() (or a function it calls) and append one message to
`message` and one to `messageENG`.
"""
import re

from .structural import get_element_type, get_task
from .bpmn_utils import (supprimer_doublons, get_lane_id_from_flow_node,
                         color_task, PALETTE_MISSING_INFO)
from ..add import get_annotation_for_participant

# --- reading the diagram -------------------------------------------------
def get_nom_taches_role(bpmnfile,id):
   taches = []
   liste_elements = get_flow_node_refs_from_lane(bpmnfile,id)
   for i in liste_elements:
     print(i)
     print(get_element_type(i,bpmnfile))
     if("Activity" in i):
       taches.append(get_task(bpmnfile,i))
   return taches

def get_participant_id_for_task(file_path, task_id):
    # Lire le fichier XML ligne par ligne
    with open(file_path, 'r') as file:
        lines = file.readlines()
        xml_content = ''.join(lines)
    
    # Fonction pour extraire la valeur d'un attribut XML
    def extract_attribute(xml, attribute):
        attr_start = f'{attribute}="'
        start_idx = xml.find(attr_start)
        if start_idx != -1:
            start_idx += len(attr_start)
            end_idx = xml.find('"', start_idx)
            return xml[start_idx:end_idx]
        return None

    # Trouver la tâche avec l'ID donné
    task_start = f'<task id="{task_id}"'
    task_idx = xml_content.find(task_start)
    if task_idx == -1:
        return None
    
    # Trouver le processus contenant cette tâche
    process_start = '<process '
    process_end = '</process>'
    
    process_idx = xml_content.find(process_start)
    while process_idx != -1:
        process_end_idx = xml_content.find(process_end, process_idx) + len(process_end)
        process_xml = xml_content[process_idx:process_end_idx]
        
        # Vérifier si le processus contient cette tâche
        if task_start in process_xml:
            process_id = extract_attribute(process_xml, 'id')
            break
        process_idx = xml_content.find(process_start, process_end_idx)
    
    if process_id is None:
        return None
    
    # Trouver le participant contenant ce processus
    participant_start = '<participant '
    participant_end = '/>'
    
    participant_idx = xml_content.find(participant_start)
    while participant_idx != -1:
        participant_end_idx = xml_content.find(participant_end, participant_idx) + len(participant_end)
        participant_xml = xml_content[participant_idx:participant_end_idx]
        
        # Vérifier si le participant contient ce processus
        if f'processRef="{process_id}"' in participant_xml:
            return extract_attribute(participant_xml, 'id')
        
        participant_idx = xml_content.find(participant_start, participant_end_idx)
    
    return None

def get_flow_node_refs_from_lane(bpmn_file_path, lane_id):
    flow_node_refs = []
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    
    lane_start = False
    for line in lines:
        # Check for the start of the specific lane
        if f'<lane id="{lane_id}"' in line:
            lane_start = True
        
        # If within the lane, look for flowNodeRef elements
        if lane_start:
            if "<flowNodeRef>" in line:
                match = re.search(r'<flowNodeRef>(.*?)</flowNodeRef>', line)
                if match:
                    flow_node_refs.append(match.group(1))
            
            # Check for the end of the lane
            if "</lane>" in line:
                lane_start = False
    
    return flow_node_refs

def clean_list(string_list):
    # Utiliser un ensemble pour éliminer les doublons, puis filtrer les chaînes vides
    return list({s for s in string_list if s})

def get_annotation_proxy(bpmnfile,id):
   loi = []
   id_list = []
   with open(bpmnfile, 'r') as file:
      lines = file.readlines()
   for line in lines:
      if((('sourceRef="'+id) in line) ):
         id_list.append(re.search(r'targetRef="([^"]+)"', line).group(1))
      if((('targetRef="'+id) in line)):
         id_list.append(re.search(r'sourceRef="([^"]+)"', line).group(1))
   id_lane = get_participant_id_for_task(bpmnfile,id)
   #print('basta' + id_lane)
   loi.append(get_annotation_for_participant(bpmnfile,id_lane))
    
   

   for i in id_list:
      loi.append(get_annotation2(bpmnfile,i))
   loi.append(get_annotation2(bpmnfile,id))
   loi.append(get_annotation2(bpmnfile,get_lane_id_from_flow_node(bpmnfile,id)))
   return supprimer_doublons(loi)

def get_annotation_role(bpmnfile,id):
   finale = []
   tache_liste = get_flow_node_refs_from_lane(bpmnfile,id)
   for i in tache_liste:
       finale.append(get_annotation3(bpmnfile,i))
       finale.append(get_annotation2(bpmnfile,i))
   return clean_list(finale)

def get_annotation(bpmn_file_path,id):
   msg = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<association" in line) and (id in line):
         match = re.search(r'targetRef="([^"]+)"', line)
         temp = match.group(1)
         for line2 in lines : 
             if temp in line2 and  '<textAnnotation' in line2:
                msg.append("missing information : "+re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1]).group(1))
   return msg

def get_annotation2(bpmn_file_path,id):
   msg = ""
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<association" in line) and (id in line):
         match = re.search(r'sourceRef="([^"]+)"', line)
         temp = match.group(1)
         for line2 in lines : 
             if temp in line2 and  '<textAnnotation' in line2:
                msg = re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1])
                if (msg):
                    return msg.group(1)
   return msg

def get_annotation3(bpmn_file_path,id):
   msg = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<association" in line) and (id in line):
         match = re.search(r'targetRef="([^"]+)"', line)
         temp = match.group(1)
         for line2 in lines : 
             if temp in line2 and  '<textAnnotation' in line2:
                return re.search(r'<text>(.*?)</text>', lines[lines.index(line2)+1]).group(1)

def get_all_tasks(bpmnfile):
    allTasks = []
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for i in lines:
        if("<task" in i):
            match = re.search(r'id="([^"]+)"', i)
            allTasks.append(match.group(1))
    return allTasks

def getids(bpmn_file_path):
   ids_list = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<exclusiveGateway" in line):
         match = re.search(r'id="([^"]+)"', line)
         ids_list.append(match.group(1))
   return ids_list

def getid_picine(bpmn_file_path):
   ids_list = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ((("<participant" in line) and ("name=" not in line)) or (("<lane " in line) and ("name=" not in line))):
         match = re.search(r'id="([^"]+)"', line)
         ids_list.append(match.group(1))
   return ids_list 

def getway_exclusive_valide(bpmnfile,id):
   cpt=0
   with open(bpmnfile, 'r') as file:
      lines = file.readlines()
   for line in lines:
      if(('targetRef="'+id+'"') in line):
         cpt+=1
   if(cpt > 1):
      return False
   else:
      return True
   
def getways_ids(bpmn_file_path):
   ids_list = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if ("<exclusiveGateway" in line) and (("name=" not in line)):
         match = re.search(r'id="([^"]+)"', line)
         if(getway_exclusive_valide(bpmn_file_path,match.group(1))):
            ids_list.append(match.group(1))
   return ids_list

# --- detectors -----------------------------------------------------------
def negative_event(bpmnfile):
   with open(bpmnfile, 'r') as file:
      lines = file.readlines()
   ids_list = []
   target_list=[]
   type_target = []
   list_finale = []
   for line in lines:
      if("<task" in line):
         match = re.search(r'id="([^"]+)"', line)
         ids_list.append(match.group(1))
   for id in ids_list:
      for line in lines:
         if((('sourceRef="'+id) in line)):
             target_list.append(re.search(r'targetRef="([^"]+)"', line).group(1))
      for i in target_list:
         
         type_target.append(get_element_type(i,bpmnfile))
      if(("intermediateCatchEvent" in type_target) and ("intermediateThrowEvent" not in type_target)):
         for i in target_list:
            
            if(get_element_type(i,bpmnfile) == "intermediateCatchEvent"):
               list_finale.append(i)
      target_list = []
      type_target = []
   return list_finale
     
def verif_logique(bpmnfile,maliste,id):
  # Use regular expression to find all numbers in the string
    numbers = re.findall(r'\d+', maliste)
    unique_numbers = set(map(int, numbers))
    num = len(unique_numbers) -2
    nb1 = maliste.count("&#62") + maliste.count("superieur")
    nb2 = maliste.count("&#60") + maliste.count("inferieur")
    nb3 = maliste.count("=") + maliste.count("egal")
    if(((nb1 + nb2 + nb3) != 6) and num ==2):
        if(get_annotation2(bpmnfile,id)):
           return "missing information : interval manquant voire article :"+get_annotation(bpmnfile,id).__str__()
        else:
           return "missing information : interval manquant"
    else:
        return 0

def getways_ids2(bpmn_file_path,err):
   ids_list = []
   content = []
   messageENG = []
   with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
   ids_list = getids(bpmn_file_path)
   message = []
   for i in ids_list:
       for j in lines:
         if(("<sequenceFlow" in j) and (i in j)):
            test = re.search(r'name="([^"]+)"', j)
            if test:
             content.append(test.group(1))
       if(("&#62" in content.__str__()) or ("&#60" in content.__str__()) or ("=" in content.__str__()) or ("superieur" in content.__str__()) or ("inferieur" in content.__str__()) or ("egale" in content.__str__())):
          if("&#62" not in content.__str__() and ("superieur" not in content.__str__())):
            err += 1 
            messageENG.append("Error MI"+str(err)+"# the upper case is missing# see the article "+get_annotation(bpmn_file_path,i).__str__())
            message.append("erreur MI"+str(err)+"# il manque le cas de superieur# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
          if("&#60" not in content.__str__() and ("inferieur" not in content.__str__())):
            err += 1
            messageENG.append("Error MI"+str(err)+"# the lower case is missing# see the article "+get_annotation(bpmn_file_path,i).__str__()) 
            message.append("erreur MI"+str(err)+"#: il manque le cas de inferieur# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
          if("=" not in content.__str__() and ("egale" not in content.__str__())):
            err += 1 
            print("belkacem")
            messageENG.append("Error MI "+str(err)+"# the case of equal is missing# see the article "+get_annotation(bpmn_file_path,i).__str__()) 
            message.append("Erreur MI "+str(err)+"# il manque le cas de egale# voire l'article "+get_annotation(bpmn_file_path,i).__str__())
            colorier_task(bpmn_file_path,i)
       if(verif_logique(bpmn_file_path,content.__str__(),i)):
          
          message.append(verif_logique(bpmn_file_path,content.__str__(),i))
       content = []        
   return message , messageENG

def colorier_task(bpmnfile, id_task):
    """Colour an element orange (missing information)."""
    color_task(bpmnfile, id_task, PALETTE_MISSING_INFO)

def colorier_picine(id,liste):
   for i in liste:
      if((id in i) and ("<bpmndi:BPMNShape" in i)):
        i= i[:-2]+' bioc:stroke="#831311" bioc:fill="#ffcdd2" color:background-color="#ffcdd2" color:border-color="#831311">\n'
   return liste

def modify_bpmn_file(bpmn_file_path):
    print('hello')
    err = 0
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    id_values = getways_ids(bpmn_file_path)
    ids_picine = getid_picine(bpmn_file_path)
    
    modified_lines = []
    message = []
    messageENG =[]
    for id in id_values:
       err += 1
       with open(bpmn_file_path, 'r') as file:
         lines = file.readlines()
       for line in lines:
           if (id in line)and("<exclusiveGateway" in line):
               if ("name=""" in line):
                  modified_line = re.sub(r'name=""', r'name="erreur MI'+str(err)+'"', line)
                  modified_lines.append(modified_line)
               elif ("name=""" not in line):
                  modified_line =re.sub(r'(id="[^"]+")', r'\1 name="erreur MI'+str(err)+'"', line)
                  modified_lines.append(modified_line)
           if ("<bpmndi:BPMNShape" in line) and (id in line):
                line = line[:-2]+' bioc:stroke="#6b3c00" bioc:fill="#ffe0b2" color:background-color="#ffe0b2" color:border-color="#6b3c00">\n'
                modified_lines.append(line)
           elif ("<exclusiveGateway" not in line) or (id not in line):
              modified_lines.append(line) 
       if(get_annotation_proxy(bpmn_file_path,id).__len__() > 0):
          messageENG.append("Error MI " +str(err)+"# Missing condition #"+"Condition not specified in the article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+"#Revise the article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+" and Add the appropriate condition") 
          message.append("Erreur MI " +str(err)+"# Condition manquante #"+"Condition non preciser dans l'article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+"#Reviser l'article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+" et Ajouter la condition adéquate")  
       else:
          messageENG.append("Error MI " +str(err)+"# Missing condition #This part is not annotated on the diagram#Add the correct condition")
          message.append("Erreur MI " +str(err)+"# Condition manquante #Cette partie est Non annoter sur le diagramme#Ajouter la condition adéquate")
       with open(bpmn_file_path, 'w') as file:
            file.truncate(0)
            file.writelines(modified_lines)
       modified_lines = []
    with open(bpmn_file_path, 'r') as file:
      lines2 = file.readlines()
    modified_lines = []
    if(ids_picine.__len__()>0):
      for i in ids_picine:
            with open(bpmn_file_path, 'r') as file:
                 lines2 = file.readlines()
            modified_lines = []
            for j in lines2:
              if((i in j) and ("<bpmndi:BPMNShape" in j)):
                err +=1
                modified_line =j[:-2]+' bioc:stroke="#6b3c00" bioc:fill="#ffe0b2" color:background-color="#ffe0b2" color:border-color="#6b3c00">\n'
                
                modified_lines.append(modified_line)
                if(get_annotation_role(bpmn_file_path,i).__len__() >0):
                 print("chikour" + get_annotation_role(bpmn_file_path,i).__str__() )
                 messageENG.append("Error MI " +str(err)+"# Missing role # Role not specified in the article : "+get_annotation_role(bpmn_file_path,i).__str__()+"#Revise the article : "+get_annotation_role(bpmn_file_path,i).__str__()+" Add the appropriate role to these tasks :"+get_nom_taches_role(bpmn_file_path,i).__str__())
                 message.append("Erreur MI " +str(err)+"# Role manquant # Role non précisé dans l'article : "+get_annotation_role(bpmn_file_path,i).__str__()+"#Reviser l'article : "+get_annotation_role(bpmn_file_path,i).__str__()+" Ajouter le rôle adéquat a ces taches :"+get_nom_taches_role(bpmn_file_path,i).__str__())
                else:
                 messageENG.append("Error MI " +str(err)+"# Missing role #Cette partie est Non annoter sur le diagramme#Add the correct role" )
                 message.append("Erreur MI " +str(err)+"# Role manquant #Cette partie est Non annoter sur le diagramme#Ajouter le rôle adéquat" )
              else:
                modified_lines.append(j)
      
            with open(bpmn_file_path, 'w') as file:
              file.truncate(0)
              file.writelines(modified_lines)
              modified_lines = []
    with open(bpmn_file_path, 'r') as file:
      lines3 = file.readlines()
    negative = negative_event(bpmn_file_path)
    print(negative)
    for id in negative:
       for line in lines3:
          if(("<intermediateCatchEvent" in line)and(id in line)):
             print("hahahaha")
             err += 1
             modified_line = re.sub(r'name=""', r'name="erreur MI'+str(err)+'"', line)
             #message.append("erreur MI #" +str(err)+" negative event")
             message.append("Erreur MI " +str(err)+"# Negative event #"+"negative event dans l'article : "+get_annotation_proxy(bpmn_file_path,id).__str__()+"#Reviser l'article : "+get_annotation_proxy(bpmn_file_path,id).__str__())  
             modified_lines.append(modified_line)
          elif ("<bpmndi:BPMNShape" in line) and (id in line):
                line = line[:-2]+' bioc:stroke="#6b3c00" bioc:fill="#ffe0b2" color:background-color="#ffe0b2" color:border-color="#6b3c00">\n'
                modified_lines.append(line)
          else:
             modified_lines.append(line)
    if(modified_lines):
     with open(bpmn_file_path, 'w') as file:
         file.truncate(0)
         file.writelines(modified_lines)
    with open(bpmn_file_path, 'r') as file:
        lines = file.readlines()
    modified_lines = []
    all_tasks = get_all_tasks(bpmn_file_path)
    for i in all_tasks:
        cpt = 0
        for line in lines:
            if(('sourceRef="'+i+'"') in line):
                cpt += 1
        if(cpt == 0):
            err+=1
            messageENG.append("Error MI " +str(err)+"# Legal vacuum #"+"Legal vacuum in the article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+"#Revise the article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+" and Add adequate information")  
            message.append("Erreur MI " +str(err)+"# Vide juridique #"+"Vide juridique dans l'article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+"#Reviser l'article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+" et Ajouter des informations adéquates")  
            #message.append("Erreur MI " +str(err)+"# Vide juridique # Vide juridique dans l'article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+" # Reviser l'article : "+get_annotation_proxy(bpmn_file_path,i).__str__()+" Ajouter des information à :"+get_annotation_proxy(bpmn_file_path,i).__str__())
            print(message.__str__())
            colorier_task(bpmn_file_path,i)
    message1 , message2= getways_ids2(bpmn_file_path,err)
    return message1 + message , message2+messageENG 