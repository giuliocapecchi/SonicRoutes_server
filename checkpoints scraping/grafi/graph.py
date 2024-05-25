import csv
import networkx as nx

# Funzione per caricare i nodi da un file CSV e restituire un dizionario di nodi
def load_nodes(filename):
    nodes = {}
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            node_id = int(row['index'])  # Converti l'ID del nodo in intero
            # Crea un dizionario per i valori del nodo escludendo l'ID
            node_values = {key: value for key, value in row.items() if key != 'index'}
            nodes[node_id] = node_values  # Aggiungi il nodo al dizionario
    return nodes

# Funzione per caricare gli archi da un file CSV e restituire una lista di archi ordinata
def load_edges(filename):
    edges = []
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source = int(row['Source'])  # Converti l'ID di origine in intero
            target = int(row['Target'])  # Converti l'ID di destinazione in intero
            # Aggiungi l'arco alla lista degli archi
            edges.append((source, target))
            # Se gli archi non hanno una direzione, aggiungi anche l'arco opposto
            edges.append((target, source))
    edges = list(set(edges))  # Rimuovi eventuali archi duplicati
    edges.sort()  # Ordina gli archi in base al nodo di origine e poi al nodo di destinazione
    return edges

# Carica i nodi
nodes = load_nodes('python/grafi/nodi.csv')

# Carica gli archi ordinati
edges = load_edges('python/grafi/archi.csv')

# Crea un grafo
graph = nx.Graph()

# Aggiungi i nodi al grafo
for node_id, node_attrs in nodes.items():
    graph.add_node(node_id, **node_attrs)

# Aggiungi gli archi al grafo
graph.add_edges_from(edges)

print(graph.nodes)

# Ora graph contiene il grafo completo di nodi e archi
nx.write_graphml(graph, 'python/grafi/grafo_completo.graphml')
