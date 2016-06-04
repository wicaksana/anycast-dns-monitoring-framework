from py2neo import Graph, Node, Relationship

graph = Graph(password='neo4jneo4j')

# create nodes
arif = Node('Human', name='arif')
wicaksana = Node('Human', name='wicaksana')

aw = Relationship(arif, 'KNOWS', wicaksana)
graph.create(aw)
