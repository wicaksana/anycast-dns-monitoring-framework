from py2neo import Graph

graph = Graph(password='neo4jneo4j')

result = graph.run(
    "MATCH (n1)-[r:`TO_2001:500:2d::/48_1422748800`]->(n2) RETURN n1.label, n2.label LIMIT 25"
)

for node1, node2 in result:
    print('node1')