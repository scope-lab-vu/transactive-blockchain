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
