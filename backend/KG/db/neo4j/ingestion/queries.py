import os,sys

def set_config_rdf():
    config_sql =  f"""
    CALL n10s.graphconfig.init({{
    handleVocabUris: "SHORTEN",
    handleMultival: "ARRAY",
    handleRDFTypes: "LABELS_AND_NODES",
    keepLangTag: true,
    multivalPropList: null
    }});
    """

    return config_sql

#  Import RDF data from a file serialized as Pretty-XML
def ingest_rdf(rdf_file_path):
    sql = f"""
        CALL n10s.rdf.import.fetch(
        "{rdf_file_path}",
        "RDF/XML" 
        );
    """
    return sql  

def ingest_csv(operator, identifier, csv_file_name, batch_size = 1000): 
    sql = f"""
    CALL apoc.periodic.iterate(
        "LOAD CSV WITH HEADERS FROM 'file:///{csv_file_name}' AS row RETURN row",
        "MERGE (n1:Entity {{id: row.subject}})
         MERGE (n2:Entity {{id: row.object}})
         MERGE (n1)-[r:RELATES {{type: row.predicate}}]->(n2)
         WITH n1, n2, r
         MERGE (g:Group {{name: '{operator}_{identifier}', importedOn: date()}})
         MERGE (g)-[:CONTAINS]->(n1)
         MERGE (g)-[:CONTAINS]->(n2)
         MERGE (g)-[:CONTAINS]->(rg)",
        {{batchSize: {batch_size}, iterateList: true}}
    );
    """

    return sql 

def set_constraints_rdf():
    sql = f"""
        CREATE CONSTRAINT FOR (n:Resource) REQUIRE n.uri IS UNIQUE;
        CREATE INDEX FOR :Resource(uri);

    """
    return sql

def set_constraints_csv():
    sql = [
        "CREATE CONSTRAINT FOR (e:Entity) REQUIRE e.id IS UNIQUE;",
        "CREATE CONSTRAINT FOR (rg:RelationshipGroup) REQUIRE rg.type IS UNIQUE;",
        "CREATE INDEX rel_type_index FOR ()-[r:RELATES]-() ON (r.type);",
        "CREATE INDEX group_importedon_index FOR (g:Group) ON (g.importedOn);"
    ]
    return sql


