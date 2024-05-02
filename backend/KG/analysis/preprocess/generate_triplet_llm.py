# use llama3 (70B groq) to generate KG triplets (follows OWL convention as much as possible)
import os, sys
import json
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
import numpy as np
from langchain_text_splitters import TokenTextSplitter
from rdflib import Graph, URIRef, Literal, RDF, RDFS
import csv

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

    
    # Parse the string into RDF triples
    for line in concat_str.strip().split('\n'):
        if('<' in line):
            subject, predicate, object_ = line.strip('.').split(' ', 2)
            
            subject = URIRef(subject.strip('<>'))
            predicate = URIRef(predicate.strip('<>'))
            object_ = object_.strip()
    
            if object_.startswith('<'):
                object_ = URIRef(object_.strip('<>'))
            else:
                # Remove leading and trailing quotes from literals
                object_ = Literal(object_.strip('"'))
            g.add((subject, predicate, object_))
            print(subject, predicate, object_)


    # Serialize the graph to RDF/XML format
    # print(g.serialize(format='pretty-xml'))
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