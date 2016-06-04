from py2neo import Graph, Node, Relationship

graph = Graph(password='neo4jneo4j')

# create nodes
arif = Node('Human', name='arif')
wicaksana = Node('Human', name='wicaksana')

aw = Relationship(arif, 'KNOWS', wicaksana)
aw['from'] = '2015'
graph.create(aw)

aw2 = Relationship(arif, 'KNOWS', wicaksana)
aw2['from'] = '2017'
graph.create(aw2)
