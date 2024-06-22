def get_annotation_for_participant(file_path, participant_id):
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
    
    # Trouver l'association liée au participant
    association_start = '<association '
    association_end = '/>'
    
    association_idx = xml_content.find(association_start)
    annotation_id = None
    
    while association_idx != -1:
        association_end_idx = xml_content.find(association_end, association_idx) + len(association_end)
        association_xml = xml_content[association_idx:association_end_idx]
        
        # Vérifier si l'association concerne le participant
        if f'sourceRef="{participant_id}"' in association_xml:
            annotation_id = extract_attribute(association_xml, 'targetRef')
            break
        association_idx = xml_content.find(association_start, association_end_idx)
    
    if annotation_id is None:
        return None
    
    # Trouver l'annotation avec l'ID donné
    annotation_start = f'<textAnnotation id="{annotation_id}"'
    annotation_end = '</textAnnotation>'
    
    annotation_idx = xml_content.find(annotation_start)
    if annotation_idx == -1:
        return None
    
    annotation_end_idx = xml_content.find(annotation_end, annotation_idx) + len(annotation_end)
    annotation_xml = xml_content[annotation_idx:annotation_end_idx]
    
    # Extraire le texte de l'annotation
    text_start = '<text>'
    text_end = '</text>'
    
    text_start_idx = annotation_xml.find(text_start)
    if text_start_idx != -1:
        text_start_idx += len(text_start)
        text_end_idx = annotation_xml.find(text_end, text_start_idx)
        return annotation_xml[text_start_idx:text_end_idx]
    
    return None