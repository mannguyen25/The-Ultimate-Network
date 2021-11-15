'''
Creates edge lists for a directed weighted 2019 graph and for a bipartite graph
of tournaments and participating teams.
'''

import networkx as nx
from networkx.algorithms import bipartite

import pandas as pd
import numpy as np
import scipy.sparse as sp
import os
import re


def make_team_graph(csv_list):
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
            if weight1 == 'F' or weight1 == 'L':
                weight1 = 0
                weight2 = 15
            graph.add_edge(df[column_names[1]][i], df[column_names[2]][i], weight=weight1)
            graph.add_edge(df[column_names[2]][i], df[column_names[1]][i], weight=weight2)

    edge_list = nx.to_pandas_edgelist(graph)
    edge_list.to_csv(path_or_buf='games_edgelist.csv', index=False)
    return graph


def make_bipartite_graph(csv_list):
    bigraph = nx.Graph()
    edge_ids = pd.DataFrame()

    for csv in csv_list:
        filename = csv[2:-4]
        edge_ids = edge_ids.append({'id': filename, 'category': 'tournament'}, ignore_index=True)

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

        bigraph.add_node(filename, bipartite=0)
        bigraph.add_nodes_from(teams, bipartite=1)
        for team in teams:
            bigraph.add_edge(filename, team)
            edge_ids = edge_ids.append({'id': team, 'category': 'team'}, ignore_index=True)

    edge_ids.to_csv(path_or_buf='bipartite_labels.csv', index=False)
    edge_list = nx.to_pandas_edgelist(bigraph)
    edge_list.to_csv(path_or_buf='bipartite_edgelist.csv', index=False)

    # Create student and class projections
    tournaments = {n for n, d in bigraph.nodes(data=True) if d['bipartite'] == 0}
    teams = set(bigraph) - tournaments
    team_graph = bipartite.projected_graph(bigraph, teams)
    tournament_graph = bipartite.projected_graph(bigraph, tournaments)

    return bigraph, team_graph, tournament_graph


def analyze(graph, file_object=None):
    # Degree assortativity
    assor = nx.algorithms.assortativity.degree_assortativity_coefficient(graph)
    print(f'\tThe degree assortativity is {assor}', file=file_object)

    # k-components
    # k_components = nx.algorithms.connectivity.k_components(nationals_graph)
    # for num in k_components:
    #     if num > 5:
    #         print(f'The {num}-components are {k_components[num]}\\\\')


# Histograms
# degree_sequence = sorted([d for n, d in class_graph.degree()])
# bin_size = list(n for n in range(1, 150))
# plt.hist(degree_sequence, bins=bin_size)
# plt.savefig('Class Histogram2.png')

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


def bianalyze(graph, file_object=None):
    # Redundancy
    redundancies = bipartite.node_redundancy(graph)
    print(f'\tThe average redundancy is {sum(redundancies)/len(redundancies)}', file=file_object)
    for name in redundancies:
        print(f'\t{name} has redundancy {redundancies[name]}', file=file_object)


def main():
    sanctioned = './Sanctioned 2019'
    nonsanctioned = './Non-Sanctioned 2019'
    csv_list = ['./D-I College Championships.csv', './nationals.csv']
    # csv_list = ['./sanctioned2019.csv', './nationals.csv']
    for entry in os.scandir(sanctioned):
        if entry.path.endswith('.csv'):
            csv_list.append(entry.path)
    for entry in os.scandir(nonsanctioned):
        if entry.path.endswith('.csv'):
            csv_list.append(entry.path)

    games = make_team_graph(csv_list)
    part, tour, team = make_bipartite_graph(csv_list)

    label = ['games', 'bipartite', 'tournaments', 'teams']
    graphs = [games, part, tour, team]

    with open('Analysis Results.txt', 'w') as file_object:
        for index, graph in enumerate(graphs):
            print(f'For the {label[index]} graph:', file=file_object)
            analyze(graph, file_object)
        # print('For the bipartite graph:', file=file_object)
        # bianalyze(part, file_object)


if __name__ == '__main__':
    main()
