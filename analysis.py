'''
Creates edge lists for a directed weighted 2019 graph and for a bipartite graph
of tournaments and participating teams.
'''

import networkx as nx
from networkx.algorithms import bipartite

import matplotlib
import matplotlib.pyplot as plt

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
            if weight1 == 'W' or weight2 == 'F' or weight2 == 'L':
                weight1 = 15
                weight2 = 0
            if weight1 == 'F' or weight1 == 'L' or weight2 == 'W':
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


def make_region_csv(csv_list):
    regions = pd.DataFrame()
    for csv in csv_list:
        df = pd.read_csv(csv)
        column_names = []
        for col in df:
            column_names.append(col)

        for row in df.index:
            regions = regions.append({'Name': df[column_names[1]][row], 'region': csv}, ignore_index=True)
            regions = regions.append({'Name': df[column_names[2]][row], 'region': csv}, ignore_index=True)

    regions = regions.drop_duplicates()
    # The output file requires cleaning
    regions.to_csv(path_or_buf='region_labels.csv', index=False)


def compare(l1, l2):
    t1 = []
    t2 = []

    for csv in l1:
        df = pd.read_csv(csv)
        column_names = []
        for col in df:
            column_names.append(col)

        for row in df.index:
            t1.append(df[column_names[1]][row])
            t1.append(df[column_names[2]][row])

    n1 = []
    [n1.append(x) for x in t1 if x not in n1]

    for csv in l2:
        df = pd.read_csv(csv)
        column_names = []
        for col in df:
            column_names.append(col)

        for row in df.index:
            t2.append(df[column_names[1]][row])
            t2.append(df[column_names[2]][row])

    n2 = []
    [n2.append(x) for x in t2 if x not in n2]

    dif = []
    # [dif.append(x) for x in n1 if x not in n2]
    [dif.append(x) for x in n2 if x not in n1]

    diff = []
    [diff.append(x) for x in dif if x not in diff]

    print(diff)


def analyze(graph, label, file_object=None):
    print(f'For the {label} graph:', file=file_object)

    # Degree assortativity
    assor = nx.algorithms.assortativity.degree_assortativity_coefficient(graph)
    print(f'\tThe degree assortativity is {assor}', file=file_object)

    centrality = nx.algorithms.eigenvector_centrality(graph)
    centrality = {key:val for key, val in sorted(centrality.items(), key=lambda item: item[1], reverse=True)}
    print(f'\tThe eigevector centralities are {centrality}', file=file_object)

    # centrality = nx.algorithms.betweenness_centrality(graph)
    # centrality = {key:val for key, val in sorted(centrality.items(), key=lambda item: item[1], reverse=True)}
    # print(f'\tThe betweennes centralities are {centrality}', file=file_object)

    # Create heatmaps of Laplacians and path matrices
    # matrix = sns.heatmap(bi_lap.toarray(), cmap='rocket_r')
    # fig = matrix.get_figure()
    # fig.savefig("Bipartite Laplacian.png")

    # k-components
    # k_components = nx.algorithms.connectivity.k_components(nationals_graph)
    # for num in k_components:
    #     if num > 5:
    #         print(f'The {num}-components are {k_components[num]}\\\\')


    # Check power law distribution
    ugraph = graph.to_undirected()
    nx.set_edge_attributes(ugraph, 1, 'weight')
    degree_sequence = sorted([d for n, d in ugraph.degree()])

    p_k = list(0 for _ in range(degree_sequence[-1]))
    for i in range(degree_sequence[-1]):
        sum = 0
        for d in degree_sequence:
            if d >= i:
                sum += 1
        p_k[i] = sum / len(degree_sequence)

    plt.loglog(p_k)
    plt.title(f'{label} graph ')
    plt.ylabel('Cumulative Distribution Function')
    plt.xlabel('Degree')
    plt.savefig(f'{label} loglog')
    plt.close()


def bianalyze(graph, file_object=None):
    # Redundancy
    redundancies = bipartite.node_redundancy(graph)
    print(f'\tThe average redundancy is {sum(redundancies)/len(redundancies)}', file=file_object)
    for name in redundancies:
        print(f'\t{name} has redundancy {redundancies[name]}', file=file_object)


def randcsvs(games, bipart, tournaments, teams):

    deg_seq = bipart.degree
    deg_seq = {key: val for key, val in deg_seq}
    tournament_seq = tournaments.degree
    tournament_seq = [val for key, val in tournament_seq]
    team_seq = teams.degree
    team_seq = [val for key, val in team_seq]

    part1_seq = []
    part2_seq = []

    [part1_seq.append(val) for key, val in deg_seq.items() if key in tournaments.nodes]
    [part2_seq.append(val) for key, val in deg_seq.items() if key in teams.nodes]

    rand_bipartite = nx.Graph()
    rand_tournaments = nx.Graph()
    rand_teams = nx.Graph()

    for i in range(100):
        birand = bipartite.configuration_model(part1_seq, part2_seq, create_using=bipart)
        rand_bipartite = nx.disjoint_union(rand_bipartite, birand)
        tournrand = nx.configuration_model(tournament_seq, create_using=tournaments)
        rand_tournaments = nx.disjoint_union(rand_tournaments, tournrand)
        teamrand = nx.configuration_model(team_seq, create_using=teams)
        rand_teams = nx.disjoint_union(rand_teams, teamrand)

    edges = nx.to_pandas_edgelist(rand_bipartite)
    edges.to_csv(path_or_buf='birand_edgelist.csv', index=False)
    edges = nx.to_pandas_edgelist(rand_tournaments)
    edges.to_csv(path_or_buf='tournrand_edgelist.csv', index=False)
    edges = nx.to_pandas_edgelist(rand_teams)
    edges.to_csv(path_or_buf='teamrand_edgelist.csv', index=False)

    nodes = pd.DataFrame()
    for node, label in birand.nodes.data('bipartite'):
        if label == 0:
            nodes = nodes.append({'Id': node, 'category': 'tournament'}, ignore_index=True)
        else:
            nodes = nodes.append({'Id': node, 'category': 'team'}, ignore_index=True)

    nodes.to_csv(path_or_buf='sing_birand_partition.csv', index=False) #node IDs are not integers?
    edges = nx.to_pandas_edgelist(birand)
    edges.to_csv(path_or_buf='sing_birand_edgelist.csv', index=False)
    edges = nx.to_pandas_edgelist(tournrand)
    edges.to_csv(path_or_buf='sing_tournrand_edgelist.csv', index=False)
    edges = nx.to_pandas_edgelist(teamrand)
    edges.to_csv(path_or_buf='sing_teamrand_edgelist.csv', index=False)


def main():
    sanctioned = './Sanctioned 2019'
    nonsanctioned = './Non-Sanctioned 2019'
    csv_list1 = ['./D-I College Championships.csv', './nationals.csv']
    csv_list2 = []

    for entry in os.scandir(sanctioned):
        if entry.path.endswith('.csv'):
            csv_list1.append(entry.path)
    # make_region_csv(csv_list)
    for entry in os.scandir(nonsanctioned):
        if entry.path.endswith('.csv'):
            csv_list1.append(entry.path)
            csv_list2.append(entry.path)

    # compare(csv_list1, csv_list2)

    game = make_team_graph(csv_list1)
    part, team, tour = make_bipartite_graph(csv_list1)

    df = pd.read_csv('./sanctioned_edgelist.csv')
    sanctioned = nx.from_pandas_edgelist(df)
    df = pd.read_csv('./nonsanctioned_edgelist.csv')
    nonsanctioned = nx.from_pandas_edgelist(df)

    label = ['games', 'bipartite', 'tournaments', 'teams', 'sanctioned', 'nonsanctioned']
    graphs = [game, part, tour, team, sanctioned, nonsanctioned]

    randcsvs(game, part, tour, team)

    with open('Analysis Results.txt', 'w') as file_object:
        for index, graph in enumerate(graphs):
            analyze(graph, label[index], file_object)
        # print('For the bipartite graph:', file=file_object)
        # bianalyze(part, file_object)


if __name__ == '__main__':
    main()
