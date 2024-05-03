# pip install -U spacy
# python -m spacy download en_core_web_sm 
# python -m spacy download en_core_web_trf 

# using spacy as it is considered faster than nltk in general
import spacy
from rdflib import Graph, Namespace, URIRef, RDF, Literal
from rdflib.namespace import FOAF, XSD

def extract_triplets(nl_eaac_report):
    # Text input
    nlp = spacy.load('en_core_web_trf')
    text = str(nl_eaac_report)

    # Process text
    doc = nlp(text)

    # Extract entities and relations
    triplets = []
    for token in doc:
        if token.dep_ == 'ROOT':
            predicate = token.text
            subject = [child.text for child in token.children if child.dep_ in ('nsubj', 'nsubjpass')]
            object = [child.text for child in token.children if child.dep_ in ('dobj', 'attr', 'prep')]
            if subject and object:
                triplets.append((subject[0], predicate, object[0]))

    # print(triplets)

    print("extracted entities:")
    ent_dict = {}
    for ent in doc.ents:
        print(ent.text, ent.label_)
        ent_dict[ent.text] = ent.label_
    
    return triplets, ent_dict


def generate_rdf(triplets, ent_dict):
    # Create a graph
    g = Graph()

    # Define a namespace
    n = Namespace("http://eaac.org/model#")

    # Add triples to the graph based on extracted data
    for subj, pred, obj in triplets:
        # Get entity types from dictionary or default to Organization
        subj_info = ent_dict.get(subj, {"type": FOAF.Organization, "value": subj})
        obj_info = ent_dict.get(obj, {"type": FOAF.Organization, "value": obj})

        # Handle URIs or literals based on type info
        if isinstance(subj_info, dict):
            subj_uri = Literal(subj_info["value"], datatype=subj_info["type"])
        else:
            subj_uri = URIRef(n + subj_info["value"].replace(" ", "_"))

        if "datatype" in obj_info:
            obj_uri = Literal(obj_info["value"], datatype=obj_info["datatype"])
        else:
            obj_uri = URIRef(n + obj_info["value"].replace(" ", "_"))

        pred_uri = URIRef(n + pred.replace(" ", "_"))

        # Add RDF types to the graph
        g.add((subj_uri, RDF.type, subj_info["type"]))
        g.add((obj_uri, RDF.type, obj_info["type"]))

        # Add the predicate (relationship)
        g.add((subj_uri, pred_uri, obj_uri))

    # Serialize the graph in RDF/XML format
    print(g.serialize(format="pretty-xml"))
    return g.serialize(format="pretty-xml")