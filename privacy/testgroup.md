**[Grouping of Feeders]{dir="ltr"}**

[]{dir="ltr"}

[Consider a simple feeder network consisting of n feeder branches
connected by a bus]{dir="ltr"}

[Let bi represent a feeder branch, where 0 \< i \<= n]{dir="ltr"}

[Let the load safety constraints of the branches be pi]{dir="ltr"}

[]{dir="ltr"}

[For a particular time interval T,]{dir="ltr"}

[Let C be the set of consumption offers and P the set of production
offers posted by all nodes present in the network]{dir="ltr"}

[]{dir="ltr"}

[C(b) and P(b) represent the consumption and production offers posted by
nodes present on the same feeder branch]{dir="ltr"}

[Also, C'(b) and P'(b) represent the consumption and production
solutions to the nodes present on the same feeder branch as provided by
the algorithm]{dir="ltr"}

[]{dir="ltr"}

[For all i, Sum of c belonging to C(bi) \<= pi ,and]{dir="ltr"}

[For all i, Sum of c' belonging to C'(bi) \<= pi, are the safety
constraint for the network]{dir="ltr"}

[]{dir="ltr"}

[When two or more feeder branches are grouped together, the group has a
constraint equal to the minima of the safety constraints of individual
branches i.e.]{dir="ltr"}

[]{dir="ltr"}

[Pi = min(pi,pj,pk..pm), where Pi represents safety constraint of Group
i consisting of branches bi,bj,bk\...bm]{dir="ltr"}

[]{dir="ltr"}

[Due to the new safety constraint on loads, and the grouping of multiple
feeders together, a new constraint is added to the matching
algorithm:]{dir="ltr"}

[]{dir="ltr"}

[Sigma C'(bi) + Sigma C'(bj) + Sigma C'(bk) + ..... + Sigma C'(bm) \<=
Pi]{dir="ltr"}

[]{dir="ltr"}

[Due to this constraint, the load that can be balanced by the producers
reduces, and the nodes are forced to satisfy the remaining amount by
buying power from the DSO, which is more expensive]{dir="ltr"}

[However, grouping provides privacy to the nodes as the nodes within a
group cannot be uniquely identified]{dir="ltr"}

[The extra amount that the nodes have to pay for satisfying the power
demand is thus the cost of privacy]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

**[Feeder Conversion Diagram]{dir="ltr"}**

![](media/image1.png){width="6.5in"
height="2.4166666666666665in"}[]{dir="ltr"}

[(For the purpose of diagrams, nodes below the line represent producers,
and those above represent consumers)]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

**[Analysis of Feeder Diagram with Prosumer offers for a particular
interval]{dir="ltr"}**

[]{dir="ltr"}

![](media/image4.png){width="6.5in"
height="4.416666666666667in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[Total consumption offers posted in the interval = 49 units]{dir="ltr"}

[Total production offers posted in the interval = 45 units]{dir="ltr"}

[Extra Energy to be purchased from DSO (Ed) = demand - energy
traded]{dir="ltr"}

[Cost of privacy (CoP) = Ed for group - Ed for no groups]{dir="ltr"}

[]{dir="ltr"}

**[No Groups:]{dir="ltr"}**

[Energy traded = 45]{dir="ltr"}

[Energy to be bought = 4]{dir="ltr"}

[]{dir="ltr"}

**[Grouping 1 and 2:]{dir="ltr"}**

[Energy traded = 33]{dir="ltr"}

[Energy to be bought = 16]{dir="ltr"}

[CoP = 12]{dir="ltr"}

[]{dir="ltr"}

[**Grouping 2 and 3:**]{dir="ltr"}

[Energy traded = 25]{dir="ltr"}

[Energy to be bought = 24]{dir="ltr"}

[CoP = 20]{dir="ltr"}

[]{dir="ltr"}

**[Grouping 1 and 3:]{dir="ltr"}**

[Energy traded = 25]{dir="ltr"}

[Energy to be bought = 24]{dir="ltr"}

[CoP = 20]{dir="ltr"}

[]{dir="ltr"}

**[Grouping 1, 2 and 3:]{dir="ltr"}**

[Energy traded = 10]{dir="ltr"}

[Energy to be bought = 39]{dir="ltr"}

[CoP = 35]{dir="ltr"}

[ ]{dir="ltr"}

[]{dir="ltr"}

**[TESTING AND RESULTS FOR OTHER TEST CASES]{dir="ltr"}**

[]{dir="ltr"}

[buying\_offers = \[]{dir="ltr"}

[Offer(0, 0, 1, 10, 45),]{dir="ltr"}

[Offer(1, 2, 1, 10, 46),]{dir="ltr"}

[Offer(2, 4, 1, 10, 45),]{dir="ltr"}

[Offer(3, 6, 1, 10, 41),]{dir="ltr"}

[Offer(4, 8, 1, 10, 43),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[C\_ext=\[4.0,4.0,4.0,4.0,4.0\] (External constraint)]{dir="ltr"}

[C\_int=\[4.0,4.0,4.0,4.0,4.0\] (Internal constraint)]{dir="ltr"}

[]{dir="ltr"}

[selling\_offers = \[]{dir="ltr"}

[Offer(5, 1, 1, 10, 38),]{dir="ltr"}

[Offer(6, 3, 1, 10, 35),]{dir="ltr"}

[Offer(7, 5, 1, 10, 37),]{dir="ltr"}

[Offer(8, 7, 1, 10, 32),]{dir="ltr"}

[Offer(9, 9, 1, 10, 39),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[Best groups are:]{dir="ltr"}

[Number of distinguishable groups: 1 Group: \[\[0, 1, 2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 2 Group: \[\[0, 1\], \[2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 3 Group: \[\[0, 1\], \[2, 3\],
\[4\]\]]{dir="ltr"}

[Number of distinguishable groups: 4 Group: \[\[0\], \[2\], \[1, 3\],
\[4\]\]]{dir="ltr"}

[]{dir="ltr"}

![](media/image8.png){width="6.0625in"
height="4.666666666666667in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[selling\_offers = \[]{dir="ltr"}

[Offer(5, 1, 1, 10, 11),]{dir="ltr"}

[Offer(6, 3, 1, 10, 12),]{dir="ltr"}

[Offer(7, 5, 1, 10, 13),]{dir="ltr"}

[Offer(8, 7, 1, 10, 14),]{dir="ltr"}

[Offer(9, 9, 1, 10, 15),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[Best groups are:]{dir="ltr"}

[Number of distinguishable groups: 1 Group: \[\[0, 1, 2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 2 Group: \[\[0, 1, 2\], \[3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 3 Group: \[\[0\], \[1, 2\], \[3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 4 Group: \[\[0\], \[1\], \[2\], \[3,
4\]\]]{dir="ltr"}

[]{dir="ltr"}

![](media/image7.png){width="6.052083333333333in"
height="4.5625in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[selling\_offers = \[]{dir="ltr"}

[Offer(5, 1, 1, 10, 20),]{dir="ltr"}

[Offer(6, 3, 1, 10, 30),]{dir="ltr"}

[Offer(7, 5, 1, 10, 20),]{dir="ltr"}

[Offer(8, 7, 1, 10, 30),]{dir="ltr"}

[Offer(9, 9, 1, 10, 20),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[Best groups are:]{dir="ltr"}

[Number of distinguishable groups: 1 Group: \[\[0, 1, 2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 2 Group: \[\[0, 1\], \[2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 3 Group: \[\[1\], \[0, 2\], \[3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 4 Group: \[\[0\], \[1\], \[3\], \[2,
4\]\]]{dir="ltr"}

[]{dir="ltr"}

![](media/image2.png){width="5.979166666666667in"
height="4.645833333333333in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[C\_ext=\[3.0,4.0,3.0,4.0,3.0\]]{dir="ltr"}

[C\_int=\[3.0,4.0,3.0,4.0,3.0\]]{dir="ltr"}

[]{dir="ltr"}

[selling\_offers = \[]{dir="ltr"}

[Offer(5, 1, 1, 10, 10),]{dir="ltr"}

[Offer(6, 3, 1, 10, 10),]{dir="ltr"}

[Offer(7, 5, 1, 10, 10),]{dir="ltr"}

[Offer(8, 7, 1, 10, 20),]{dir="ltr"}

[Offer(9, 9, 1, 10, 20),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[Best groups are:]{dir="ltr"}

[Number of distinguishable groups: 1 Group: \[\[0, 1, 2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 2 Group: \[\[0, 1, 2\], \[3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 3 Group: \[\[0\], \[2, 3\], \[1,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 4 Group: \[\[0\], \[1\], \[2, 3\],
\[4\]\]]{dir="ltr"}

[]{dir="ltr"}

![](media/image9.png){width="6.020833333333333in"
height="4.489583333333333in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[selling\_offers = \[]{dir="ltr"}

[Offer(5, 1, 1, 10, 20),]{dir="ltr"}

[Offer(6, 3, 1, 10, 20),]{dir="ltr"}

[Offer(7, 5, 1, 10, 20),]{dir="ltr"}

[Offer(8, 7, 1, 10, 10),]{dir="ltr"}

[Offer(9, 9, 1, 10, 10),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[Best groups are:]{dir="ltr"}

[Number of distinguishable groups: 1 Group: \[\[0, 1, 2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 2 Group: \[\[0, 1\], \[2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 3 Group: \[\[0\], \[2, 3\], \[1,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 4 Group: \[\[0\], \[1\], \[2\], \[3,
4\]\]]{dir="ltr"}

![](media/image5.png){width="6.0625in"
height="4.645833333333333in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[selling\_offers = \[]{dir="ltr"}

[Offer(5, 1, 1, 10, 20),]{dir="ltr"}

[Offer(6, 3, 1, 10, 10),]{dir="ltr"}

[Offer(7, 5, 1, 10, 20),]{dir="ltr"}

[Offer(8, 7, 1, 10, 10),]{dir="ltr"}

[Offer(9, 9, 1, 10, 20),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[Best groups are:]{dir="ltr"}

[Number of distinguishable groups: 1 Group: \[\[0, 1, 2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 2 Group: \[\[0, 1\], \[2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 3 Group: \[\[0\], \[1, 2\], \[3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 4 Group: \[\[0\], \[1\], \[2\], \[3,
4\]\]]{dir="ltr"}

![](media/image3.png){width="6.083333333333333in"
height="4.59375in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[selling\_offers = \[]{dir="ltr"}

[Offer(5, 1, 1, 10, 10),]{dir="ltr"}

[Offer(6, 3, 1, 10, 20),]{dir="ltr"}

[Offer(7, 5, 1, 10, 10),]{dir="ltr"}

[Offer(8, 7, 1, 10, 20),]{dir="ltr"}

[Offer(9, 9, 1, 10, 10),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[Best groups are:]{dir="ltr"}

[Number of distinguishable groups: 1 Group: \[\[0, 1, 2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 2 Group: \[\[1, 3\], \[0, 2,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 3 Group: \[\[0\], \[1, 2\], \[3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 4 Group: \[\[0\], \[1\], \[2\], \[3,
4\]\]]{dir="ltr"}

[]{dir="ltr"}

![](media/image10.png){width="5.947916666666667in"
height="4.552083333333333in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[selling\_offers = \[]{dir="ltr"}

[Offer(5, 1, 1, 10, 20),]{dir="ltr"}

[Offer(6, 3, 1, 10, 20),]{dir="ltr"}

[Offer(7, 5, 1, 10, 20),]{dir="ltr"}

[Offer(8, 7, 1, 10, 20),]{dir="ltr"}

[Offer(9, 9, 1, 10, 20),]{dir="ltr"}

[\]]{dir="ltr"}

[]{dir="ltr"}

[Best groups are:]{dir="ltr"}

[Number of distinguishable groups: 1 Group: \[\[0, 1, 2, 3,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 2 Group: \[\[1, 3\], \[0, 2,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 3 Group: \[\[0\], \[1, 3\], \[2,
4\]\]]{dir="ltr"}

[Number of distinguishable groups: 4 Group: \[\[0\], \[2\], \[1, 3\],
\[4\]\]]{dir="ltr"}

[]{dir="ltr"}

![](media/image6.png){width="6.135416666666667in"
height="4.510416666666667in"}[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

[]{dir="ltr"}

**[Script for analysing cost-privacy trade-offs while forming
groups]{dir="ltr"}**

[]{dir="ltr"}

-   [The script works by calculating all possible combinations for
    > grouping in the provided microgrid network]{dir="ltr"}

-   [A group is created by placing all nodes on the included feeders on
    > one feeder, which is chosen to be the one having the smallest
    > constraint value of the feeders in that group]{dir="ltr"}

-   [The energy traded is calculated for each configuration using the
    > matching solver, and the best groups are identified based on the
    > least difference in traded energies between the new network and
    > the original network]{dir="ltr"}

-   [These are then compared to each other based on the number of
    > distinct groups/feeders in each network]{dir="ltr"}

[]{dir="ltr"}

**[Heuristics for selecting Groups]{dir="ltr"}**

[]{dir="ltr"}

[The script would take a long time to find optimal groups in case of
large feeder networks. To make this faster, certain heuristics can be
used to group feeders, although the resulting groups may not be the
ideal solution]{dir="ltr"}

-   [Production value and constraint: The total production offers in a
    > group should be less than, but as close as possible to the new
    > constraint\
    > Let the constraint of a group be c, and the production offers of
    > the participating feeders be pi, pj.., then\
    > Sigma (pi,pj..) \<= c\
    > \|(c-Sigma(pi,pj...))\| is min\
    > The groups that can satisfy these properties are better. In cases
    > where the first condition cannot be satisfied, the second still
    > holds]{dir="ltr"}

<!-- -->

-   [Multiple groups: While making multiple groups, each group should
    > satisfy the first heuristic as closely as possible. However having
    > a more groups that fall under that heuristic is more important
    > than having a single group follow it perfectly]{dir="ltr"}
