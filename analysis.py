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


def make_team_graph(csv_lists):
    edge_lists = []
    for csv_list in csv_lists:
        graph = nx.DiGraph()

        for csv in csv_list:
            df = pd.read_csv(csv)
            column_names = []
            for col in df:
                column_names.append(col)

            for row in df.index:
                if df[column_names[0]][row] == 'Date':
                    df.drop(row)

            for i in df.index:
                weight1 = df[column_names[2]][i]
                weight2 = df[column_names[3]][i]
                if weight1 == 'W' or weight2 == 'F' or weight2 == 'L':
                    weight1 = 15
                    weight2 = 0
                if weight1 == 'F' or weight1 == 'L' or weight2 == 'W':
                    weight1 = 0
                    weight2 = 15
                graph.add_edge(df[column_names[0]][i], df[column_names[1]][i], weight=weight1)
                graph.add_edge(df[column_names[1]][i], df[column_names[0]][i], weight=weight2)

        edge_list = nx.to_pandas_edgelist(graph)
        edge_lists.append(edge_list)

    edge_lists[0].to_csv(path_or_buf='nonsanctioned_edgelist.csv', index=False)
    edge_lists[1].to_csv(path_or_buf='sanctioned_edgelist.csv', index=False)
    edge_lists[2].to_csv(path_or_buf='games_edgelist.csv', index=False)
    return graph


def make_bipartite_graph(csv_list):
    bigraph = nx.Graph()
    edge_ids = pd.DataFrame()
    regions = pd.read_csv('./region_labels.csv')
    region_col_names = []
    for col in regions:
        region_col_names.append(col)

    for csv in csv_list:
        filename = csv[31:-4]
        edge_ids = edge_ids.append({'id': filename, 'category': 'tournament'}, ignore_index=True)

        df = pd.read_csv(csv)

        column_names = []
        for col in df:
            column_names.append(col)

        teams = []
        for row in df.index:
            home = df[column_names[0]][row]
            away = df[column_names[1]][row]
            if home not in teams:
                teams.append(home)
            if away not in teams:
                teams.append(away)

        team_regions = {}
        file_region = None
        for row in regions.index:
            if filename == regions[region_col_names[0]][row]:
                file_region = regions[region_col_names[4]][row]
        for index, team in enumerate(teams):
            for row in regions.index:
                if team == regions[region_col_names[0]][row]:
                    team_regions[team] = regions[region_col_names[4]][row]
                elif team[:-2] == regions[region_col_names[0]][row]:
                    team_regions[team[:-2]] = regions[region_col_names[4]][row]

        # print(filename)
        # print(len(teams))
        # print(len(team_regions))

        bigraph.add_node(filename, bipartite=0, region=file_region)
        for team in teams:
            bigraph.add_node(team, bipartite=1, region=team_regions[team])
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
    print(f'\tThe degree assortativity is {assor}\n', file=file_object)

    centrality = nx.algorithms.eigenvector_centrality(graph, max_iter=500)
    centrality = {key:val for key, val in sorted(centrality.items(), key=lambda item: item[1], reverse=True)}
    print(f'\tThe eigevector centralities are {centrality}\n', file=file_object)

    centrality = nx.algorithms.closeness_centrality(graph)
    centrality = {key:val for key, val in sorted(centrality.items(), key=lambda item: item[1], reverse=True)}
    print(f'\tThe closeness centralities are {centrality}\n', file=file_object)

    # centrality = nx.algorithms.betweenness_centrality(graph)
    # centrality = {key:val for key, val in sorted(centrality.items(), key=lambda item: item[1], reverse=True)}
    # print(f'\tThe betweennes centralities are {centrality}', file=file_object)

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


def bianalyze(part, team, tour, file_object=None):
    print(f'Region analysis:', file=file_object)

    # print(nx.get_node_attributes(part, 'region'), file=file_object)

    region_assor = nx.attribute_assortativity_coefficient(part, 'region')
    team_assor = nx.attribute_assortativity_coefficient(team, 'region')
    tour_assor = nx.attribute_assortativity_coefficient(tour, 'region')

    print(f'\tThe bipartite region assortativity is {region_assor}', file=file_object)
    print(f'\tThe team region assortativity is {team_assor}', file=file_object)
    print(f'\tThe tournament region assortativity is {tour_assor}', file=file_object)


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
    sanctioned = './New Files with Updated RegEx/Sanctioned Games'
    nonsanctioned = './New Files with Updated RegEx/Non-Sanctioned'
    csv_list1 = []
    csv_list2 = []
    csv_list3 = []

    for entry in os.scandir(sanctioned):
        if entry.path.endswith('.csv'):
            csv_list1.append(entry.path)
            csv_list2.append(entry.path)
    # make_region_csv(csv_list)
    for entry in os.scandir(nonsanctioned):
        if entry.path.endswith('.csv'):
            csv_list1.append(entry.path)
            csv_list3.append(entry.path)

    # compare(csv_list2, csv_list3)

    game = make_team_graph([csv_list3, csv_list2, csv_list1])
    part, team, tour = make_bipartite_graph(csv_list1)

    df = pd.read_csv('./sanctioned_edgelist.csv')
    sanctioned = nx.from_pandas_edgelist(df)
    df = pd.read_csv('./nonsanctioned_edgelist.csv')
    nonsanctioned = nx.from_pandas_edgelist(df)

    label = ['games', 'bipartite', 'tournaments', 'teams', 'sanctioned', 'nonsanctioned']
    graphs = [game, part, tour, team, sanctioned, nonsanctioned]

    # randcsvs(game, part, tour, team)

    with open('Analysis Results.txt', 'w') as file_object:
        for index, graph in enumerate(graphs):
            analyze(graph, label[index], file_object)
        bianalyze(part, team, tour, file_object)


if __name__ == '__main__':
    main()
