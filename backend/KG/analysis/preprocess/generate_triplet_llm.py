# use llama3 (70B groq) to generate KG triplets (follows OWL convention as much as possible)
import os, sys
import json
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import numpy as np
from langchain_text_splitters import TokenTextSplitter
from rdflib import Graph, URIRef, Literal, RDF, RDFS, Namespace
import csv
import re 

def llama3_70b_parse(nl_report): # context window of 8192 tokens

    # roughly check token length of eaac_report 
       
    text_splitter = TokenTextSplitter(chunk_size=8192, chunk_overlap=100)
    text_chunks = text_splitter.split_text(nl_report)
    

    concat=''
    for chunk in text_chunks:
        chat = ChatGroq(temperature=0, model_name="llama3-70b-8192")
        system = "You are an expert in OWL convention and knowledge graphs. Please generate knowledge graph triplets following OWL convention. Please only output the triplets."
        human = "{text}"
        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", human)])

        chain = prompt | chat
        response = chain.invoke({"text": f"{chunk}"})
        concat += '\n'+response.content

    return concat


def extract_triplets(nl_report):

    concat_str = llama3_70b_parse(nl_report)
    # Initialize a graph
    g = Graph()

    # Define the namespace for schema
    # SCHEMA = URIRef("http://schema.org/")

    NS = Namespace("http://eaac.org/") # for literal like predicates

    # Parse the string into RDF triples
    for line in concat_str.strip().split('\n'):
        line = line.strip()
        if re.search(r'\d.', line):
            line = line.split('.', 1)[1].strip()  # Remove the numbering part
        if '<' in line:
            # Split around the first '<' to get predicate and object

            subject_part, predicate_object_part = line.split('>', 1)
            subject_stripped= subject_part.strip('<>. ')
            subject = URIRef(subject_stripped.replace(' ', '_'))
            
            # Split predicate and object
            if '>' == predicate_object_part[-1]:
                predicate, object_ = predicate_object_part.rsplit('<', 1)
                predicate_stripped = predicate.strip(' ')
                predicate = predicate_stripped.strip('<>. ')
            else: 
                predicate, object_ = predicate_object_part.split('"', 1)
                predicate_stripped = predicate.strip(' ')
                predicate = predicate_stripped.strip('<>. ')
            
            if(':' in predicate):
                predicate = URIRef(predicate)
            else:
                predicate = NS[predicate]

            # Handle object, either as URI or literal
            if '>' in object_:
                object_stripped = object_.strip('<>. ')
                object_stripped = object_stripped.strip('" ')
                object_ = URIRef(object_stripped.replace(' ', '_'))
                

            else:
                # Correctly remove leading and trailing quotes and any surrounding spaces
                object_ = object_.strip().strip('". ')
                object_ = Literal(object_.replace(' ', '_'))

            g.add((subject, predicate, object_))
            print(subject, predicate, object_)
       
    rdf_serialized= g.serialize(format='pretty-xml', encoding='utf-8')
    return rdf_serialized


def convert_rdf_to_csv(rdf_path, csv_path):
    
    # Load your RDF data
    g = Graph()
    g.parse(f"{rdf_path}", format="xml")

    # Define the CSV output file
    with open(f'{csv_path}', 'w', newline='') as csvfile:
        fieldnames = ['subject', 'predicate', 'object']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()

        for s, p, o in g:
            print(s,p,o)
            # Assuming you only want to convert a subset or all triples to CSV
            writer.writerow({'subject': str(s), 'predicate': str(p), 'object': str(o)})
    print('Triples written to CSV file:', csv_path)