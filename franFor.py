"""
 * smallWorldWattsStrogatz.py
 *
 * Copyright (c) 2026, Jordi-Lluis Figueras
 *
 * OpenAI Codex / ChatGPT 5.5 has been used in the editing of this file.
 *
"""

"""Explore clustering and path lengths in Watts-Strogatz networks.

Usage:
  python3 smallWorldWattsStrogatz.py
  python3 smallWorldWattsStrogatz.py --nodes 100 --neighbors 4 --trials 30
  python3 smallWorldWattsStrogatz.py --probabilities 0 0.01 0.05 0.1 0.5 1

The script prints average statistics over several random trials. The small-world
effect is visible when a small rewiring probability greatly reduces path length
while clustering remains relatively high.
"""

import argparse
import statistics

try:
  import networkx as nx
  import matplotlib.pyplot as plt
except ImportError as error:
  raise SystemExit(
    "This script requires NetworkX. On Debian/Ubuntu, use a virtual environment:\n"
    "  python3 -m venv .venv\n"
    "  source .venv/bin/activate\n"
    "  python3 -m pip install networkx"
  ) from error


defaultNodes = 200
defaultNeighbors = 6
defaultTrials = 20
defaultSeed = 2026
defaultProbabilities = [0.0, 0.01, 0.03, 0.05, 0.10, 0.30, 1.0]


def parseArguments():
  parser = argparse.ArgumentParser(description = "Explore the Watts-Strogatz small-world model")
  parser.add_argument("--nodes", type = int, default = defaultNodes, help = "number of nodes")
  parser.add_argument("--neighbors", type = int, default = defaultNeighbors, help = "number of ring neighbors per node")
  parser.add_argument("--trials", type = int, default = defaultTrials, help = "number of random trials per probability")
  parser.add_argument("--seed", type = int, default = defaultSeed, help = "base random seed")
  parser.add_argument(
    "--probabilities",
    nargs = "+",
    type = float,
    default = defaultProbabilities,
    help = "rewiring probabilities to test",
  )
  parser.add_argument("--decimals", type = int, default = 4, help = "number of decimals in printed statistics")
  args = parser.parse_args()

  if args.nodes <= 2:
    parser.error("--nodes must be larger than 2")

  if args.neighbors <= 0:
    parser.error("--neighbors must be positive")

  if args.neighbors >= args.nodes:
    parser.error("--neighbors must be smaller than --nodes")

  if args.neighbors % 2 != 0:
    parser.error("--neighbors must be even for the Watts-Strogatz ring construction")

  if args.trials <= 0:
    parser.error("--trials must be positive")

  if args.decimals < 0:
    parser.error("--decimals must be nonnegative")

  for probability in args.probabilities:
    if probability < 0 or probability > 1:
      parser.error("each rewiring probability must satisfy 0 <= p <= 1")

  return args


def largestConnectedSubgraph(graph):
  if nx.is_connected(graph):
    return graph, 1.0

  largestComponent = max(nx.connected_components(graph), key = len)
  componentFraction = len(largestComponent) / graph.number_of_nodes()
  return graph.subgraph(largestComponent).copy(), componentFraction


def computeTrialStatistics(nNodes, nNeighbors, probability, seed):
  graph = nx.watts_strogatz_graph(nNodes, nNeighbors, probability, seed = seed)
  connectedGraph, componentFraction = largestConnectedSubgraph(graph)

  nodes_list = [0 for _ in range(nNodes)]

  for i in range(nNodes):
    nodes_list[i] = graph.degree[i]
  
  return {
    "clustering": nx.average_clustering(graph),
    "pathLength": nx.average_shortest_path_length(connectedGraph),
    "diameter": nx.diameter(connectedGraph),
    "isconnected" : nx.is_connected(graph),
    "componentFraction": componentFraction,
    "numberofconnectedcomponents" : nx.number_connected_components(graph),
    "sizeoflargestcomponent" : len(max(nx.connected_components(graph), key = len)),
    "histogram data": nodes_list,
  }

def meanStatistic(statisticsList, key):
  return statistics.mean(item[key] for item in statisticsList)

def connectedpercent(statisticsList):
  connectedPercent = (sum(item["isconnected"] for item in statisticsList)/len(statisticsList))
  return connectedPercent


def printHeader(args):
  print("Watts-Strogatz small-world experiment")
  print(f"  nodes: {args.nodes}")
  print(f"  neighbors per node in initial ring: {args.neighbors}")
  print(f"  trials per probability: {args.trials}")
  print()
  print("p        clustering   path length   diameter   fully connected (%)   largest component (%)  avr. groups   nodes in largest")
  print("--------------------------------------------------------------------------------------------------------------------------")

def printStatisticsRow(probability, statisticsList, decimals):
  clustering = meanStatistic(statisticsList, "clustering")
  pathLength = meanStatistic(statisticsList, "pathLength")
  diameter = meanStatistic(statisticsList, "diameter")
  connectedpercent1 = connectedpercent(statisticsList)
  componentFraction = meanStatistic(statisticsList, "componentFraction")
  numberofconnectedcomponents = meanStatistic(statisticsList, "numberofconnectedcomponents")
  sizeoflargestcomponent = meanStatistic(statisticsList, "sizeoflargestcomponent")
  nodesDegrees = []



  for trail in statisticsList:
    nodesDegrees.extend(trail["histogram data"])

  max_degree = max(nodesDegrees)
  nodesPerDegrees = [0 for x in range(max_degree+1)]

  for i in nodesDegrees:
    nodesPerDegrees[i] += 1

  numberOfTrails = len(statisticsList)
  for i in range(len(nodesPerDegrees)):
    nodesPerDegrees[i]/= numberOfTrails

  plt.bar(range(len(nodesPerDegrees)), nodesPerDegrees, color='skyblue', edgecolor='black')

  # Adding labels and title
  plt.xlabel('Degrees ')
  plt.ylabel('Average frequency')
  plt.title(f'Average degree distrubution when p= {probability}')

  # Display the plot
  plt.show()

  print(
    f"{probability:<8.3g} "
    f"{clustering:>10.{decimals}f} "
    f"{pathLength:>11.{decimals}f} "
    f"{diameter:>12.{decimals}f} "
    f"{connectedpercent1:>17.{decimals}f} "
    f"{componentFraction:>18.{decimals}f} "
    f"{numberofconnectedcomponents:>18.{decimals}f} "
    f"{sizeoflargestcomponent:>18.{decimals}f} "
  )

def finalPlots(probabilities, clusteringPlot, pathLengthPlot):
  dividedClustering = [x / clusteringPlot[0] for x in clusteringPlot]
  dividedPathLength = [x / pathLengthPlot[0] for x in pathLengthPlot]

  plt.figure() 
  plt.plot(probabilities, dividedClustering, 'o-')
  plt.title("Average Clustering Coefficient vs p")
  plt.xlabel("Probability of rewire p")
  plt.ylabel("Average Clustering Coefficient C(p) / C(0)")
  
  plt.figure() 
  plt.plot(probabilities, dividedPathLength, 's-')
  plt.title("Average Path Length vs p")
  plt.xlabel("Probability of rewire p")
  plt.ylabel("l(p) / l(0)")

  plt.show()

def main():
  args = parseArguments()
  printHeader(args)

  clusteringPlot = []
  pathLengthPlot = []

  for probabilityIndex, probability in enumerate(args.probabilities):
    statisticsList = []
    for trial in range(args.trials):
      seed = args.seed + 1000 * probabilityIndex + trial
      trialStatistics = computeTrialStatistics(args.nodes, args.neighbors, probability, seed)
      statisticsList.append(trialStatistics)

    printStatisticsRow(probability, statisticsList, args.decimals)
    clusteringPlot.append(meanStatistic(statisticsList, "clustering"))
    pathLengthPlot.append(meanStatistic(statisticsList, "pathLength"))

  finalPlots(args.probabilities,clusteringPlot,pathLengthPlot)


if __name__ == "__main__":
  main()
