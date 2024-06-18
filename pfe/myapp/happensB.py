import spacy

# Charger le modèle de langue anglais de spaCy
nlp = spacy.load("en_core_web_sm")

# Dictionnaire des relations temporelles des verbes
temporal_relations = {
    "write": ["send", "submit", "publish", "review"],
    "draft": ["write", "edit", "finalize", "approve"],
    "plan": ["execute", "implement", "complete", "review"],
    "prepare": ["start", "execute", "finish", "review"],
    "start": ["continue", "finish", "complete", "review"],
    "initiate": ["start", "proceed", "complete", "review"],
    "begin": ["continue", "finish", "complete", "review"],
    "continue": ["finish", "complete", "review"],
    "execute": ["complete", "review"],
    "implement": ["complete", "review"],
    "finish": ["review", "submit", "publish"],
    "complete": ["review", "submit", "publish"],
    "review": ["approve", "submit", "publish"],
    "approve": ["submit", "publish"],
    "submit": ["publish"],
    "publish": [],
    "send": ["receive", "acknowledge"],
    "receive": ["acknowledge", "process", "review"],
    "acknowledge": ["process", "review"],
    "process": ["review", "complete"],
    "edit": ["finalize", "approve", "submit"],
    "finalize": ["approve", "submit", "publish"],
    "schedule": ["start", "execute", "complete"],
    "research": ["draft", "write", "publish"],
    "analyze": ["report", "publish", "review"],
    "report": ["review", "publish"],
    "organize": ["plan", "execute", "complete"],
    "construct": ["complete", "review"],
    "design": ["draft", "finalize", "approve"],
    "test": ["review", "approve", "deploy"],
    "deploy": ["monitor", "review"],
    "monitor": ["review", "adjust"],
    "adjust": ["review", "finalize"],
    "evaluate": ["review", "finalize", "report"],
    "decide": ["plan", "execute", "complete"],
    "train": ["execute", "evaluate"],
    "learn": ["apply", "review"],
    "apply": ["review", "execute"],
    "negotiate": ["finalize", "agree"],
    "agree": ["execute", "complete"],
    "confirm": ["execute", "complete"],
    "notify": ["receive", "acknowledge"],
    "consult": ["decide", "execute"],
    "communicate": ["acknowledge", "act"],
    "act": ["review", "complete"]
}

def extract_svo(doc):
    """Extract the subject, verb, and object/adverb from a given spaCy doc."""
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

def happens_before(sent1, sent2):
    """
    Detect if sent1 happens before sent2 using a predefined dictionary of temporal relations,
    and ensure both sentences have the same subject and the same object/adverb.
    :param sent1: str - The first sentence
    :param sent2: str - The second sentence
    :return: bool - True if sent1 happens before sent2, False otherwise
    """
    doc1 = nlp(sent1)
    doc2 = nlp(sent2)

    # Extraire le sujet, le verbe et l'objet/adverbe de chaque phrase
    subject1, verb1, obj1 = extract_svo(doc1)
    subject2, verb2, obj2 = extract_svo(doc2)
    
    # Vérifier si les sujets, verbes et objets/adverbes des deux phrases sont les mêmes
    if subject1 == subject2 and obj1 == obj2:
        for v1 in [verb1] if verb1 else []:
            for v2 in [verb2] if verb2 else []:
                # Vérifier si v1 se produit avant v2 dans le dictionnaire
                if v1 in temporal_relations and v2 in temporal_relations[v1]:
                    return True
                # Vérifier si v2 se produit avant v1 dans le dictionnaire
                if v2 in temporal_relations and v1 in temporal_relations[v2]:
                    return False
    
    return None  # Si les sujets, verbes ou objets/adverbes diffèrent, impossible de déterminer

# Exemple d'utilisation
#sent1 = "Write the report."
#sent2 = "Send the report."

#print(happens_before(sent1, sent2))  # Devrait retourner True

#sent3 = "Write the report."
#sent4 = "Send the document."

#print(happens_before(sent3, sent4))  # Devrait retourner None
