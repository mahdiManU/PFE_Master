# happensB.py
import spacy
from googletrans import Translator
# Charger le modèle de langue anglais de spaCy
nlp = spacy.load("en_core_web_sm")


def translate_if_french(text):
    translator = Translator()
    detected_lang = translator.detect(text).lang
    
    if detected_lang == 'fr':
        translated = translator.translate(text, src='fr', dest='en')
        return translated.text
    else:
        return text
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
    "fill out" : ["submit","Publish"],
    "complete" : ["submit"],
    "apply": ["review", "execute"],
    "negotiate": ["finalize", "agree"],
    "agree": ["execute", "complete"],
    "confirm": ["execute", "complete"],
    "notify": ["receive", "acknowledge"],
    "consult": ["decide", "execute"],
    "communicate": ["acknowledge", "act"],
    "act": ["review", "complete"],
    "écrire": ["envoyer", "soumettre", "publier", "réviser"],
    "rédiger": ["écrire", "éditer", "finaliser", "approuver"],
    "planifier": ["exécuter", "implémenter", "compléter", "réviser"],
    "préparer": ["démarrer", "exécuter", "terminer", "réviser"],
    "démarrer": ["continuer", "terminer", "compléter", "réviser"],
    "initier": ["démarrer", "procéder", "compléter", "réviser"],
    "commencer": ["continuer", "terminer", "compléter", "réviser"],
    "continuer": ["terminer", "compléter", "réviser"],
    "exécuter": ["compléter", "réviser"],
    "implémenter": ["compléter", "réviser"],
    "terminer": ["réviser", "soumettre", "publier"],
    "compléter": ["réviser", "soumettre", "publier"],
    "réviser": ["approuver", "soumettre", "publier"],
    "approuver": ["soumettre", "publier"],
    "soumettre": ["publier"],
    "publier": [],
    "remplir" : ["déposer"],
    "envoyer": ["recevoir", "accuser réception"],
    "recevoir": ["accuser réception", "traiter", "réviser"],
    "accuser réception": ["traiter", "réviser"],
    "traiter": ["réviser", "compléter"],
    "éditer": ["finaliser", "approuver", "soumettre"],
    "finaliser": ["approuver", "soumettre", "publier"],
    "rechercher": ["rédiger", "écrire", "publier"],
    "analyser": ["rapporter", "publier", "réviser"],
    "rapporter": ["réviser", "publier"],
    "organiser": ["planifier", "exécuter", "compléter"],
    "construire": ["compléter", "réviser"],
    "concevoir": ["rédiger", "finaliser", "approuver"],
    "tester": ["réviser", "approuver", "déployer"],
    "déployer": ["surveiller", "réviser"],
    "surveiller": ["réviser", "ajuster"],
    "ajuster": ["réviser", "finaliser"],
    "évaluer": ["réviser", "finaliser", "rapporter"],
    "décider": ["planifier", "exécuter", "compléter"],
    "former": ["exécuter", "évaluer"],
    "apprendre": ["appliquer", "réviser"],
    "appliquer": ["réviser", "exécuter"],
    "négocier": ["finaliser", "accepter"],
    "accepter": ["exécuter", "compléter"],
    "confirmer": ["exécuter", "compléter"],
    "notifier": ["recevoir", "accuser réception"],
    "consulter": ["décider", "exécuter"],
    "communiquer": ["accuser réception", "agir"],
    "agir": ["réviser", "compléter"]
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
    doc1 = nlp(translate_if_french(sent1))
    doc2 = nlp(translate_if_french(sent2))

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
