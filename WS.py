import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

#number of nodes
N = 10
#degree of node
k = 4
#probability
#p = [0,0.001,0.003,0.01,0.1,0.3,1]
p = 0.1



G = nx.Graph()

for i in range(N):
    G.add_node(i)

r = int(k/2)
for i in range(N):
    for j in range(1,r+1):
        if(i+j<0):
            G.add_edge(i,N+i+j)
        elif(i+j>N-1):
            G.add_edge(i,i+j-N)
        else:
            G.add_edge(i,j+i)


# nx.random_reference(G, p, False, None)

existing_edges = list(G.edges)

for i in existing_edges:
    if (np.random.random()<p):
        index = (i+np.random.randint(1,N))%N
        if(index)
        G.add_edge(index)


# Circular Layout
nx.draw_circular(G, with_labels=True)
plt.savefig("outputq.png")