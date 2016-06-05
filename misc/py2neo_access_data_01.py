from py2neo import Graph

graph = Graph(password='neo4jneo4j')

results = graph.run(
    'MATCH (s:asn)-[r:TO]->(d:asn) '
    'RETURN s.name as source, r as relationship, d.name as dest '
    'LIMIT 100'
)

for source, relationship, dest in results:
    print('source: {} dest: {} relationship: {}'.format(source, dest, relationship))