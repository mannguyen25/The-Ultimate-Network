"""
Creates edge lists for a directed weighted 2019 graph and for a bipartite graph
"""

import networkx as nx
from networkx.algorithms import bipartite

import pandas as pd
import numpy as np
import scipy.sparse as sp
import os
import re


def make_edge_list(csv_list):
    graph = nx.DiGraph()

    for csv in csv_list:
        df = pd.read_csv(csv)
        column_names = []
        for col in df:
            column_names.append(col)

        seed = re.compile('\s+\(\d+\)')
        for row in df.index:
            if df[column_names[0]][row] == 'Date':
                df.drop(row)
            for col in range(1,3):
                team = df[column_names[col]][row]
                loc = seed.search(team)
                if loc:
                    df = df.replace(to_replace=team, value=team[0:loc.start()])

        for i in df.index:
            weight1 = df[column_names[3]][i]
            weight2 = df[column_names[4]][i]
            if weight1 == 'W':
                weight1 = 15
                weight2 = 0
            if weight1 == 'L':
                weight1 = 0
                weight2 = 15
            graph.add_edge(df[column_names[1]][i], df[column_names[2]][i], weight=weight1)
            graph.add_edge(df[column_names[2]][i], df[column_names[1]][i], weight=weight2)

    edge_list = nx.to_pandas_edgelist(graph)
    edge_list.to_csv(path_or_buf="sanctioned_edgelist.csv", index=False)


def bipartite_graph(csv_list):
    graph = nx.Graph()

    for csv in csv_list:
        filename = csv[2:-4]
        df = pd.read_csv(csv)

        column_names = []
        for col in df:
            column_names.append(col)

        teams = []
        for row in df.index:
            home = df[column_names[1]][row]
            away = df[column_names[2]][row]
            if home not in teams:
                teams.append(home)
            if away not in teams:
                teams.append(away)

        graph.add_node(filename, bipartite=0)
        graph.add_nodes_from(teams, bipartite=1)
        for team in teams:
            graph.add_edge(filename, team)


# Create student and class projections
# student_nodes = {n for n, d in bipartite_graph.nodes(data=True) if d["bipartite"] == 0}
# class_nodes = set(bipartite_graph) - student_nodes
#
# student_graph = bipartite.projected_graph(bipartite_graph, student_nodes)
#
# class_graph = bipartite.projected_graph(bipartite_graph, class_nodes)


# Degree assortativity
# print(nx.algorithms.assortativity.degree_assortativity_coefficient(nationals_graph))


# Redundancy
# redundancies = bipartite.node_redundancy(student_graph)
# for name in redundancies:
#     print(f"{name} has redundancy {redundancies[name]}\\\\")


# k-components
# k_components = nx.algorithms.connectivity.k_components(nationals_graph)
# for num in k_components:
#     if num > 5:
#         print(f"The {num}-components are {k_components[num]}\\\\")


# Histograms
# degree_sequence = sorted([d for n, d in class_graph.degree()])
# bin_size = list(n for n in range(1, 150))
# plt.hist(degree_sequence, bins=bin_size)
# plt.savefig("Class Histogram2.png")

# p_k = list(0 for _ in range(degree_sequence[-1]))
# for i in range(degree_sequence[-1]):
#     sum = 0
#     for d in degree_sequence:
#         if d >= i:
#             sum += 1
#     p_k[i] = sum / len(degree_sequence)
#
# plt.loglog(p_k)
# plt.title('Class Graph')
# plt.ylabel('Cumulative Distribution Function')
# plt.xlabel('Degree')
# plt.savefig('Class loglog')

def main():
    sanctioned = './Sanctioned 2019'
    nonsanctioned = './Non-Sanctioned 2019'
    csv_list = []
    # csv_list = ['./sanctioned2019.csv', './nationals.csv']
    for file in os.scandir(sanctioned, nonsanctioned):
        csv_list.append(file)
        print(file)

    make_edge_list(csv_list)
    make_bipartite_edgelist(csv_list)


if __name__ == "__main__":
    main()
