import spacy

nlp = spacy.load("en_core_web_sm")


def find_entities(text):
    """Text me se naam, jagah, company, date nikalo.

    Return: [(text, label), ...]
    """
    doc = nlp(text)

    entities = []
    for ent in doc.ents:
        entities.append((ent.text, ent.label_))

    return entities
