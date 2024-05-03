import os,sys
from neo4j import GraphDatabase
from py2neo import Graph # a bit better syntax compared to neo4j module (for cypher query)
import pandas as pd


from dotenv import load_dotenv
load_dotenv(f'{os.path.dirname(__file__)}/../docker/.env')

URI = os.getenv('NEO4J_BOLT_URL')
USER = os.getenv('NEO4J_USER')
PASSWORD = os.getenv('NEO4J_PASSWORD')

class Neo4jService:
    def __init__(self, uri=URI, user=USER, password=PASSWORD):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

        # Connect to the graph database (py2neo)
        self._graph = Graph(uri, auth=(user, password))