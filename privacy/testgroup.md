Grouping of Feeders

Consider a simple feeder network consisting of n feeder branches connected by a bus
Let bi represent a feeder branch, where 0 < i <= n
Let the load safety constraints of the branches be pi

For a particular time interval T,
Let C be the set of consumption offers and P the set of production offers posted by all nodes present in the network

C(b) and P(b) represent the consumption and production offers posted by nodes present on the same feeder branch
Also, C’(b) and P’(b) represent the consumption and production solutions to the nodes present on the same feeder branch as provided by the algorithm

For all i, Sum of c belonging to C(bi) <= pi ,and 
For all i, Sum of c’ belonging to C’(bi) <= pi,  are the safety constraint for the network

When two or more feeder branches are grouped together, the group has a constraint equal to the minima of the safety constraints of individual branches i.e.

Pi = min(pi,pj,pk..pm), where Pi represents safety constraint of Group i consisting of branches bi,bj,bk...bm

Due to the new safety constraint on loads, and the grouping of multiple feeders together, a new constraint is added to the matching algorithm:

Sigma C’(bi) + Sigma C’(bj) + Sigma C’(bk) + ….. + Sigma C’(bm) <= Pi

Due to this constraint, the load that can be balanced by the producers reduces, and the nodes are forced to satisfy the remaining amount by buying power from the DSO, which is more expensive
However, grouping provides privacy to the nodes as the nodes within a group cannot be uniquely identified
The extra amount that the nodes have to pay for satisfying the power demand is thus the cost of privacy






Feeder Conversion Diagram 

(For the purpose of diagrams, nodes below the line represent producers, and those above represent consumers)


Analysis of Feeder Diagram with Prosumer offers for a particular interval 




Total consumption offers posted in the interval = 49 units
Total production offers posted in the interval = 45 units
Extra Energy to be purchased from DSO (Ed) = demand - energy traded
Cost of privacy (CoP) = Ed for group - Ed for no groups

No Groups: 
Energy traded = 45
Energy to be bought = 4

Grouping 1 and 2: 
Energy traded = 33
Energy to be bought = 16
CoP = 12

Grouping 2 and 3: 
Energy traded = 25
Energy to be bought = 24
CoP = 20

Grouping 1 and 3: 
Energy traded = 25
Energy to be bought = 24
CoP = 20

Grouping 1, 2 and 3: 
Energy traded = 10
Energy to be bought = 39
CoP = 35
    

TESTING AND RESULTS FOR OTHER TEST CASES

buying_offers = [
Offer(0, 0, 1, 10, 45),
Offer(1, 2, 1, 10, 46),
Offer(2, 4, 1, 10, 45),
Offer(3, 6, 1, 10, 41),
Offer(4, 8, 1, 10, 43),
]

C_ext=[4.0,4.0,4.0,4.0,4.0] (External constraint)
C_int=[4.0,4.0,4.0,4.0,4.0] (Internal constraint)

selling_offers = [
Offer(5, 1, 1, 10, 38),
Offer(6, 3, 1, 10, 35),
Offer(7, 5, 1, 10, 37),
Offer(8, 7, 1, 10, 32),
Offer(9, 9, 1, 10, 39),
]

Best groups are:
Number of distinguishable groups:  1   Group:  [[0, 1, 2, 3, 4]]
Number of distinguishable groups:  2   Group:  [[0, 1], [2, 3, 4]]
Number of distinguishable groups:  3   Group:  [[0, 1], [2, 3], [4]]
Number of distinguishable groups:  4   Group:  [[0], [2], [1, 3], [4]]







selling_offers = [
Offer(5, 1, 1, 10, 11),
Offer(6, 3, 1, 10, 12),
Offer(7, 5, 1, 10, 13),
Offer(8, 7, 1, 10, 14),
Offer(9, 9, 1, 10, 15),
]

Best groups are:
Number of distinguishable groups:  1   Group:  [[0, 1, 2, 3, 4]]
Number of distinguishable groups:  2   Group:  [[0, 1, 2], [3, 4]]
Number of distinguishable groups:  3   Group:  [[0], [1, 2], [3, 4]]
Number of distinguishable groups:  4   Group:  [[0], [1], [2], [3, 4]]








selling_offers = [
Offer(5, 1, 1, 10, 20),
Offer(6, 3, 1, 10, 30),
Offer(7, 5, 1, 10, 20),
Offer(8, 7, 1, 10, 30),
Offer(9, 9, 1, 10, 20),
]

Best groups are:
Number of distinguishable groups:  1   Group:  [[0, 1, 2, 3, 4]]
Number of distinguishable groups:  2   Group:  [[0, 1], [2, 3, 4]]
Number of distinguishable groups:  3   Group:  [[1], [0, 2], [3, 4]]
Number of distinguishable groups:  4   Group:  [[0], [1], [3], [2, 4]]








C_ext=[3.0,4.0,3.0,4.0,3.0]
C_int=[3.0,4.0,3.0,4.0,3.0]

selling_offers = [
Offer(5, 1, 1, 10, 10),
Offer(6, 3, 1, 10, 10),
Offer(7, 5, 1, 10, 10),
Offer(8, 7, 1, 10, 20),
Offer(9, 9, 1, 10, 20),
]

Best groups are:
Number of distinguishable groups:  1   Group:  [[0, 1, 2, 3, 4]]
Number of distinguishable groups:  2   Group:  [[0, 1, 2], [3, 4]]
Number of distinguishable groups:  3   Group:  [[0], [2, 3], [1, 4]]
Number of distinguishable groups:  4   Group:  [[0], [1], [2, 3], [4]]






selling_offers = [
Offer(5, 1, 1, 10, 20),
Offer(6, 3, 1, 10, 20),
Offer(7, 5, 1, 10, 20),
Offer(8, 7, 1, 10, 10),
Offer(9, 9, 1, 10, 10),
]

Best groups are:
Number of distinguishable groups:  1   Group:  [[0, 1, 2, 3, 4]]
Number of distinguishable groups:  2   Group:  [[0, 1], [2, 3, 4]]
Number of distinguishable groups:  3   Group:  [[0], [2, 3], [1, 4]]
Number of distinguishable groups:  4   Group:  [[0], [1], [2], [3, 4]]








selling_offers = [
Offer(5, 1, 1, 10, 20),
Offer(6, 3, 1, 10, 10),
Offer(7, 5, 1, 10, 20),
Offer(8, 7, 1, 10, 10),
Offer(9, 9, 1, 10, 20),
]

Best groups are:
Number of distinguishable groups:  1   Group:  [[0, 1, 2, 3, 4]]
Number of distinguishable groups:  2   Group:  [[0, 1], [2, 3, 4]]
Number of distinguishable groups:  3   Group:  [[0], [1, 2], [3, 4]]
Number of distinguishable groups:  4   Group:  [[0], [1], [2], [3, 4]]








selling_offers = [
Offer(5, 1, 1, 10, 10),
Offer(6, 3, 1, 10, 20),
Offer(7, 5, 1, 10, 10),
Offer(8, 7, 1, 10, 20),
Offer(9, 9, 1, 10, 10),
]

Best groups are:
Number of distinguishable groups:  1   Group:  [[0, 1, 2, 3, 4]]
Number of distinguishable groups:  2   Group:  [[1, 3], [0, 2, 4]]
Number of distinguishable groups:  3   Group:  [[0], [1, 2], [3, 4]]
Number of distinguishable groups:  4   Group:  [[0], [1], [2], [3, 4]]








selling_offers = [
Offer(5, 1, 1, 10, 20),
Offer(6, 3, 1, 10, 20),
Offer(7, 5, 1, 10, 20),
Offer(8, 7, 1, 10, 20),
Offer(9, 9, 1, 10, 20),
]

Best groups are:
Number of distinguishable groups:  1   Group:  [[0, 1, 2, 3, 4]]
Number of distinguishable groups:  2   Group:  [[1, 3], [0, 2, 4]]
Number of distinguishable groups:  3   Group:  [[0], [1, 3], [2, 4]]
Number of distinguishable groups:  4   Group:  [[0], [2], [1, 3], [4]]









Script for analysing cost-privacy trade-offs while forming groups

The script works by calculating all possible combinations for grouping in the provided microgrid network
A group is created by placing all nodes on the included feeders on one feeder, which is chosen to be the one having the smallest constraint value of the feeders in that group
The energy traded is calculated for each configuration using the matching solver, and the best groups are identified based on the least difference in traded energies between the new network and the original network
These are then compared to each other based on the number of distinct groups/feeders in each network

Heuristics for selecting Groups

The script would take a long time to find optimal groups in case of large feeder networks. To make this faster, certain heuristics can be used to group feeders, although the resulting groups may not be the ideal solution
Production value and constraint: The total production offers in a group should be less than, but as close as possible to the new constraint
Let the constraint of a group be c, and the production offers of the participating feeders be pi, pj.., then
Sigma (pi,pj..) <= c
|(c-Sigma(pi,pj…))| is min
The groups that can satisfy these properties are better. In cases where the first condition cannot be satisfied, the second still holds 
Multiple groups: While making multiple groups, each group should satisfy the first heuristic as closely as possible. However having a more groups that fall under that heuristic is more important than having a single group follow it perfectly
