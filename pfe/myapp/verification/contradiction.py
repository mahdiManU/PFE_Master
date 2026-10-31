"""
contradiction.py - detection of contradictions (error family "C" in the thesis).

Four detectors, each returning (french_messages, english_messages):

    C1  detect_C1  two tasks inside parallel/inclusive gateways contradict each other
    C2  detect_C2  two tasks (or two events) on the same start-to-end path contradict each other
    C3  detect_C3  an exclusive gateway has opposite conditions leading to the same target
    C4  detect_C4  a task is placed before another one although their verbs say the opposite order

erreur_contradiction() runs the four detectors and numbers the results
("Erreur C 1", "Error C 1", ...). Every element involved is coloured purple in
the diagram. Messages use "#" as a separator: error # type # legal part #
recommendation (rapport.py splits on it).

To add a new kind of contradiction: write a detect_Cx(bpmnfile) function that
returns (french_list, english_list), then call it in erreur_contradiction().
"""
import spacy
from nltk.corpus import wordnet
import nltk
from ..mabib import *
from .temporal import happens_before
from .bpmn_utils import supprimer_doublons, get_lane_id_from_flow_node, color_task, PALETTE_CONTRADICTION
import re
# Assurez-vous que les ressources nécessaires de NLTK sont téléchargées
#nltk.download('wordnet')
#nltk.download('omw-1.4')

# --- graph helpers -------------------------------------------------------
def tout_chemin(xml_file, start_gateway_id, end_gateway_id):
    graph = {}
    with open(xml_file, 'r') as file:
        lines = file.readlines()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('<sequenceFlow') or line.startswith('<messageFlow'):
            # Extract sourceRef and targetRef
            sourceRef = extract_attribute(line, 'sourceRef')
            targetRef = extract_attribute(line, 'targetRef')
            
            if sourceRef not in graph:
                graph[sourceRef] = []
            graph[sourceRef].append(targetRef)
        
        i += 1

    all_paths = find_all_paths(graph, start_gateway_id, end_gateway_id)
    return all_paths

def extract_attribute(line, attribute_name):
    start_index = line.find(attribute_name + '="') + len(attribute_name) + 2
    end_index = line.find('"', start_index)
    return line[start_index:end_index]

def find_all_paths(graph, start, end):
    all_paths = []
    dfs([], graph, start, end, all_paths)
    return all_paths

def dfs(current_path, graph, node, end, all_paths):
    current_path.append(node)
    
    if node == end:
        all_paths.append(current_path[:])
    else:
        if node in graph:
            for neighbor in graph[node]:
                if neighbor not in current_path:  # Avoid cycles
                    dfs(current_path, graph, neighbor, end, all_paths)
    
    current_path.pop()  # Backtrack

    return all_paths

# --- BPMN reading helpers ------------------------------------------------
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
   
   

   for i in id_list:
      loi.append(get_annotation2(bpmnfile,i))
   loi.append(get_annotation2(bpmnfile,id))
   loi.append(get_annotation2(bpmnfile,get_lane_id_from_flow_node(bpmnfile,id)))
   return clean_list(supprimer_doublons(loi))

def avoir_type(bpmnfile,id):
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    for i in lines:
        if (('id="'+id+'"') in i):
            match = re.search(r'<(\w+)', i)
            if match:
              return match.group(1)
    return None

def get_event(bpmnfile,id_event):
   msg = None
   print(id_event)
   with open(bpmnfile, 'r') as file:
        lines = file.readlines()
   for line in lines:
        if (('id="Event' in line) and ('name="' in line)and (id_event in line)):
            print(id_event)
            msg = re.search(r'name="([^"]+)"', line)
   if msg:
     return msg.group(1)
   
def get_start_event_ids_from_file(bpmnfile):
    # Read the file
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    
    # Join lines to create a single string
    bpmn_xml = ''.join(lines)
    
    # Define the regex pattern to find startEvent elements and their ids
    pattern = re.compile(r'<startEvent[^>]*\sid="([^"]+)"')
    
    # Find all matches
    matches = pattern.findall(bpmn_xml)
    
    return matches

def get_end_event_ids_from_file(bpmnfile):
    # Read the file
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    
    # Join lines to create a single string
    bpmn_xml = ''.join(lines)
    
    # Define the regex pattern to find startEvent elements and their ids
    pattern = re.compile(r'<endEvent[^>]*\sid="([^"]+)"')
    
    # Find all matches
    matches = pattern.findall(bpmn_xml)
    
    return matches

# --- text comparison -----------------------------------------------------
def oppsite(chaine1,chaine2):
   opposites = {
    "=": ["!=", "différent de", "not equal to"],
    "!=": ["=", "égale à", "equal to"],
    "&#60;": ["&#62;", "&#62;=", "supérieur à", "supérieur ou égal à", "greater than", "greater than or equal to"],
    "&#62;": ["&#60;", "&#60;=", "inférieur à", "inférieur ou égal à", "less than", "less than or equal to"],
    "&#60;=": ["&#62;", "&#62;=", "supérieur à", "supérieur ou égal à", "greater than", "greater than or equal to"],
    "&#62;=": ["&#60;", "&#60;=", "inférieur à", "inférieur ou égal à", "less than", "less than or equal to"],
    "==": ["!=", "différent de", "not equal to"],
    "!==": ["===", "strictement égale à", "strictly equal to"],
    "===": ["!==", "strictement différent de", "strictly not equal to"],
    "égal à": ["différent de", "!=", "not equal to"],
    "différent de": ["égal à", "=", "equal to"],
    "supérieur à": ["inférieur à", "&#60;", "less than"],
    "inférieur à": ["supérieur à", "&#62;", "greater than"],
    "supérieur ou égal à": ["inférieur ou égal à", "&#60;=", "less than or equal to"],
    "inférieur ou égal à": ["supérieur ou égal à", "&#62;=", "greater than or equal to"],
    "not equal to": ["equal to", "=", "égal à"],
    "equal to": ["not equal to", "!=", "différent de"],
    "greater than": ["less than", "&#60;", "inférieur à"],
    "less than": ["greater than", "&#62;", "supérieur à"],
    "greater than or equal to": ["less than or equal to", "&#60;=", "inférieur ou égal à"],
    "less than or equal to": ["greater than or equal to", "&#62;=", "supérieur ou égal à"],
    "strictly equal to": ["strictly not equal to", "!==", "strictement différent de"],
    "strictly not equal to": ["strictly equal to", "===", "strictement égale à"]
   }


   for i in opposites:
       if (i in chaine1):
         for j in opposites[i]:
           if(j in chaine2):
             return True
   return False

def get_antonyms(word):
    if not word:
        return []
    antonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            if lemma.antonyms():
                for antonym in lemma.antonyms():
                    antonyms.append(antonym.name())
    return antonyms

def detect_contradiction(sent1, sent2):
    doc1 = nlp(sent1)
    doc2 = nlp(sent2)
    
    # Extraire le sujet, le verbe et l'objet/adverbe de chaque phrase
    def extract_svo(doc):
        subject = None
        verb = None
        obj = None
        for token in doc:
            if token.dep_ == "nsubj":
                subject = token.lemma_
            if token.pos_ == "VERB":
                verb = token.lemma_
            if token.dep_ == "dobj" or token.dep_ == "advmod":
                obj = token.lemma_
        return subject, verb, obj
    
    subject1, verb1, obj1 = extract_svo(doc1)
    subject2, verb2, obj2 = extract_svo(doc2)
    
    # Vérifier la négation
    def has_negation(doc):
        for token in doc:
            if token.dep_ == "neg":
                return True
        return False
    
    negation1 = has_negation(doc1)
    negation2 = has_negation(doc2)
    
    # Détection de contradiction par négation
    if subject1 == subject2 and obj1 == obj2:
        if (negation1 and not negation2 and verb1 == verb2) or (negation2 and not negation1 and verb1 == verb2):
            return True
    
    # Détection de contradiction par antonyme
    antonyms1 = get_antonyms(verb1)
    if subject1 == subject2 and obj1 == obj2:
        if verb2 in antonyms1:
            return True
    
    return False

def applatire(liste_taches):
    finale = []
    for i in liste_taches:
        for j in i:
            if('Activity' in j):
                finale.append(j)
    return finale

def no_event_betwen(bpmnfile,task1,task2):
    chemin = tout_chemin(bpmnfile,task1,task2)
    for i in chemin:
        for j in i:
         if('Event' in j):
            return False
    return True

def no_task_betwen(bpmnfile,event1,event2):
    chemin = tout_chemin(bpmnfile,event1,event2)
    for i in chemin:
        for j in i:
         if('Activity' in j):
            return False
    return True

def colorier_task(bpmnfile, id_task):
    """Colour an element purple (contradiction)."""
    color_task(bpmnfile, id_task, PALETTE_CONTRADICTION)

# English language model of spaCy, loaded once when the module is imported
# (takes a moment). Used by detect_contradiction() to find subject, verb,
# object and negation in task labels.    
nlp = spacy.load("en_core_web_sm")

# --- detectors -----------------------------------------------------------
def detect_between(bpmnfile,para1,para2):
    tache_col = []
    liste_des_taches = tout_chemin(bpmnfile,para1,para2)  
    print("hello")
    finale = applatire(liste_des_taches)
    for i in finale:
        for j in finale:
            if(i != j):
                if(detect_contradiction(get_task(bpmnfile,i),get_task(bpmnfile,j))):
                    tache_col.append(i)
                    tache_col.append(j)
                    return  'Contradiction entre : '+get_task(bpmnfile,i)+get_task(bpmnfile,j)+"#Contradiction dans l'article : "+get_annotation_proxy(bpmnfile,i).__str__()+"#Reviser "+get_annotation_proxy(bpmnfile,i).__str__(),tache_col , 'Contradiction between : '+get_task(bpmnfile,i)+get_task(bpmnfile,j)+"#Contradiction in the article : "+get_annotation_proxy(bpmnfile,i).__str__()+"#Revise "+get_annotation_proxy(bpmnfile,i).__str__()
    return False   
                
def detect_C1(bpmnfile):
    finale = []
    finaleENG = []
    tache = []
    liste_parallel = get_all_parallelG(bpmnfile)
    for i in liste_parallel:
        for j in liste_parallel:
            if(i != j):
                if(detect_between(bpmnfile,i,j)):
                    message,tache_col , messageENG = detect_between(bpmnfile,i,j)
                    for i in tache_col:
                        tache.append(i)
                    finale.append(message)
                    finaleENG.append(messageENG)
    liste_inclusive = get_all_inclusiveG(bpmnfile)
    for i in liste_inclusive:
        for j in liste_inclusive:
            if(i != j):
                if(detect_between(bpmnfile,i,j)):
                     message,tache_col ,messageENG = detect_between(bpmnfile,i,j)
                     for i in tache_col:
                        tache.append(i)
                     finale.append(message)
                     finaleENG.append(messageENG)
    for i in tache:
        colorier_task(bpmnfile,i)
    return finale ,finaleENG

def detect_C2(bpmnfile):
     finale = []
     tache = []
     finaleENG = []
     liste_start = get_start_event_ids_from_file(bpmnfile)
     liste_end = get_end_event_ids_from_file(bpmnfile)
     for i in liste_start:
         for j in liste_end:
             mes_chemin = tout_chemin(bpmnfile,i,j)
             for k in mes_chemin:
                 for tache1 in k:
                     for tache2 in k:
                         if((k.index(tache2) > k.index(tache1)) and (tache1 != tache2) and (no_event_betwen(bpmnfile,tache1,tache2)) and ("Activity" in tache1) and ("Activity" in tache2)):
                          
                             if(detect_contradiction(get_task(bpmnfile,tache1),get_task(bpmnfile,tache2))):
                                 tache.append(tache1)
                                 tache.append(tache2)
                                 finaleENG.append("Contradiction between "+get_task(bpmnfile,tache1)+get_task(bpmnfile,tache2)+"#Contradiction in the following article : "+get_annotation_proxy(bpmnfile,tache1)+"#Revise the  article : "+get_annotation_proxy(bpmnfile,tache1))
                                 finale.append("contradiction entre "+get_task(bpmnfile,tache1)+get_task(bpmnfile,tache2)+"#Contradiction dans l'article : "+get_annotation_proxy(bpmnfile,tache1)+"#Reviser l'article : "+get_annotation_proxy(bpmnfile,tache1))
                         if((k.index(tache2) > k.index(tache1)) and (tache1 != tache2) and (no_task_betwen(bpmnfile,tache1,tache2)) and ("Event" in tache1) and ("Event" in tache2) and (avoir_type(bpmnfile,tache1)!="endEvent") and (avoir_type(bpmnfile,tache2)!="endEvent")):
                             if(detect_contradiction(get_event(bpmnfile,tache1),get_event(bpmnfile,tache2))):
                                 tache.append(tache1)
                                 tache.append(tache2)
                                 finaleENG.append("Contradiction between "+get_task(bpmnfile,tache1)+get_task(bpmnfile,tache2)+"#Contradiction in the following article : "+get_annotation_proxy(bpmnfile,tache1)+"#Revise the  article : "+get_annotation_proxy(bpmnfile,tache1))
                                 finale.append("contradiction entre "+get_event(bpmnfile,tache1)+get_event(bpmnfile,tache2)+"#Contradiction dans l'article : "+get_annotation_proxy(bpmnfile,tache1)+"#Reviser l'article : "+get_annotation_proxy(bpmnfile,tache1))
     for i in tache:
         colorier_task(bpmnfile,i)
     return finale  , finaleENG                                
                          
def detect_C3(bpmnfile):
    liste_exclu = get_all_exclusiveG(bpmnfile)
    exclu = []
    message = []
    messageENG = []
    with open(bpmnfile, 'r') as file:
        lines = file.readlines()
    
    for i in liste_exclu:
       content = []
       my_dict = {}
       for j in lines:
         if(("<sequenceFlow" in j) and (i in j)):
            test = re.search(r'name="([^"]+)"', j)
            test2 = re.search(r'targetRef="([^"]+)"', j)
            if test and test2:
             content.append(test.group(1))
             my_dict[test.group(1)] = test2.group(1)
       for k in content:
           print(my_dict)
           for p in content:
               t = oppsite(k,p) and (my_dict[k]==my_dict[p])
               if(t):
                   exclu.append(i)
                   messageENG.append("Interval contradiction#Contradiction the article : "+get_annotation_proxy(bpmnfile,i).__str__()+"#Revise the article : "+get_annotation_proxy(bpmnfile,i).__str__())
                   message.append("Contradiction d'interval#Contradiction dans l'article : "+get_annotation_proxy(bpmnfile,i).__str__()+"#Reviser l'article : "+get_annotation_proxy(bpmnfile,i).__str__())
                   colorier_task(bpmnfile,i)
                   break 
           if(t):
               break   
    return message , messageENG

def detect_C4(bpmnfile):
    liste_start = get_start_event_ids_from_file(bpmnfile)
    liste_end = get_end_event_ids_from_file(bpmnfile)
    tache = []
    message = []
    messageENG = []
    for i in liste_start:
        chemin = []
        for j in liste_end:
           chemin = tout_chemin(bpmnfile,i,j)
           chemin = supprimer_doublons(chemin)
           print(chemin.__str__())
           for t in chemin:
               for actuel, suivant in zip(t, t[1:]):
                   if(("Activity" in actuel) and ("Activity" in suivant) and (happens_before(get_task(bpmnfile,suivant),get_task(bpmnfile,actuel)))):
                       print("mahdi" + actuel +" " +suivant )
                       tache.append(suivant)
                       tache.append(actuel)
                       messageENG.append("Contradiction, the task " +get_task(bpmnfile,suivant)+" happens befor "+get_task(bpmnfile,actuel)+"#Contradiction in the article "+get_annotation_proxy(bpmnfile,actuel).__str__()+"#Revise "+get_annotation_proxy(bpmnfile,actuel).__str__())
                       message.append("Contradiction, la tache " +get_task(bpmnfile,suivant)+" se deroule avant "+get_task(bpmnfile,actuel)+"#Contradiction dans l'article "+get_annotation_proxy(bpmnfile,actuel).__str__()+"#Reviser "+get_annotation_proxy(bpmnfile,actuel).__str__())
    for i in tache:
        colorier_task(bpmnfile,i)
    return message , messageENG

def erreur_contradiction(bpmnfile):
    finale = []
    finaleENG = []
    cpt=0
    contradictionENG = []
    contradiction = []
    contradiction, contradictionENG = detect_C1(bpmnfile)

# For the other functions, extend the lists appropriately
    result1, result2 = detect_C2(bpmnfile)
    contradiction += result1
    contradictionENG += result2

    result1, result2 = detect_C3(bpmnfile)
    contradiction += result1
    contradictionENG += result2

    result1, result2 = detect_C4(bpmnfile)
    contradiction += result1
    contradictionENG += result2
    for i in contradiction:
        cpt +=1
        finale.append("Erreur C "+str(cpt)+"#"+i)
    cpt = 0
    for i in contradictionENG:
        cpt +=1
        finaleENG.append("Error C "+str(cpt)+"#"+i)
    return finale , finaleENG

#print(get_all_parallelG('last.bpmn').__str__())

#colorier_task("dada.bpmn","Task_1hcentk")


