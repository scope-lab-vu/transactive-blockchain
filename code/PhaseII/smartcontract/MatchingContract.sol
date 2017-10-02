contract MatchingContract {
    uint64 INTERVAL_LENGTH = 1;
    uint64 C_INT = 20 * 1000;
    uint64 C_EXT = 25 * 1000;
    
    mapping(address => uint64) prosumerFeeder;
    
    function addProsumer(address prosumer, uint64 feeder) public {
        prosumerFeeder[prosumer] = feeder;
    }
    
    struct Offer {
        uint64 startTime;
        uint64 endTime;
        uint64 energy;
        address prosumer;
    }
    
    mapping(uint64 => Offer) buyingOffers;
    uint64 numBuyingOffers = 0;
    mapping(uint64 => Offer) sellingOffers;
    uint64 numSellingOffers = 0;
    
    function postBuyingOffer(uint64 startTime, uint64 endTime, uint64 energy) public {
        require(startTime <= endTime);
        buyingOffers[numBuyingOffers++] = Offer({
            startTime: startTime,
            endTime: endTime,
            energy: energy,
            prosumer: msg.sender
        });
    }
    
    function postSellingOffer(uint64 startTime, uint64 endTime, uint64 energy) public {
        require(startTime <= endTime);
        sellingOffers[numSellingOffers++] = Offer({
            startTime: startTime,
            endTime: endTime,
            energy: energy,
            prosumer: msg.sender
        });
    }
    
    struct Trade {
        uint64 sellerID;
        uint64 buyerID;
        uint64 time;
        uint64 power;
    }
    
    struct Solution {
        mapping(uint64 => Trade) trades;
        uint64 numTrades;
        uint64 objective;
        mapping(uint64 => uint64) sellerProduction;
        mapping(uint64 => uint64) buyerConsumption;
        mapping(uint64 => mapping(uint64 => uint64)) feederProduction;
        mapping(uint64 => mapping(uint64 => uint64)) feederConsumption;
    }
    
    mapping(uint64 => Solution) solutions;
    uint64 numSolutions = 0;
    Solution bestSolution;
    
    function createSolution() public returns (uint64 solutionID) {
        solutions[numSolutions] = Solution({
            numTrades: 0,
            objective: 0
        });
        if (numSolutions == 0)
            bestSolution = solutions[numSolutions];
        return numSolutions++;
    }
    
    function addTrade(uint64 solutionID, uint64 sellerID, uint64 buyerID, uint64 time, uint64 power) public {
        require(solutionID < numSolutions);
        require(sellerID < numSellingOffers);
        require(buyerID < numBuyingOffers);
        
        // check if buyer and seller are matchable
        require(time >= sellingOffers[sellerID].startTime);
        require(time <= sellingOffers[sellerID].endTime);
        require(time >= buyingOffers[buyerID].startTime);
        require(time <= buyingOffers[buyerID].endTime);

        // notation        
        Solution storage solution = solutions[solutionID];
        uint64 energy = power * INTERVAL_LENGTH;
        uint64 sellingFeeder = prosumerFeeder[sellingOffers[sellerID].prosumer];
        uint64 buyingFeeder = prosumerFeeder[buyingOffers[buyerID].prosumer];
        
        // update seller, buyer, seller feeder, and buyer feeder production and consumption
        solution.sellerProduction[sellerID] += energy;
        solution.buyerConsumption[buyerID] += energy;
        solution.feederProduction[sellingFeeder][time] += power;
        solution.feederConsumption[buyingFeeder][time] += power;

        // eq:constrEnergyProd        
        require(solution.sellerProduction[sellerID] <= sellingOffers[sellerID].energy);
        // eq:constrEnergyCons       
        require(solution.buyerConsumption[buyerID] <= buyingOffers[buyerID].energy);
        // eq:constrIntProd
        require(solution.feederProduction[sellingFeeder][time] <= C_INT);
        // eq:constrIntCons
        require(solution.feederConsumption[buyingFeeder][time] <= C_INT);
        // eq:constrExtProd
        require(solution.feederProduction[sellingFeeder][time] - solution.feederConsumption[sellingFeeder][time] <= C_EXT);
        // eq:constrExtCons
        require(solution.feederConsumption[buyingFeeder][time] - solution.feederConsumption[buyingFeeder][time] <= C_EXT);
        
        // add trade to solution
        solution.trades[solution.numTrades++] = Trade({
           sellerID: sellerID,
           buyerID: buyerID,
           time: time,
           power: power
        });
        
        solution.objective += power;
        if (solution.objective > bestSolution.objective)
            bestSolution = solution;
    }
}

