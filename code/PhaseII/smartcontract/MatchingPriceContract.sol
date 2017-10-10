contract MatchingContract {
    uint64 INTERVAL_LENGTH = 1;
    uint64 C_INT = 25000;
    uint64 C_EXT = 20000;
    
    mapping(uint64 => uint64) prosumerFeeder; // TODO: mapping(address => uint64) prosumerFeeder;
    
    function addProsumer(uint64 prosumer, uint64 feeder) public { // TODO: function addProsumer(address prosumer, uint64 feeder) public {
        prosumerFeeder[prosumer] = feeder;
    }
    
    struct Offer {
        uint64 prosumer; // TODO: address prosumer;
        uint64 startTime;
        uint64 endTime;
        uint64 energy;
        uint64 price;
    }
    
    mapping(uint64 => Offer) buyingOffers;
    uint64 numBuyingOffers = 0;
    mapping(uint64 => Offer) sellingOffers;
    uint64 numSellingOffers = 0;
    
    event BuyingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 price);
    event SellingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 price);
    
    function postBuyingOffer(uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 price) public { // TODO: function postBuyingOffer(uint64 startTime, uint64 endTime, uint64 energy, uint64 price) public {
        require(startTime <= endTime);
        BuyingOfferPosted(numBuyingOffers, prosumer, startTime, endTime, energy, price);
        buyingOffers[numBuyingOffers++] = Offer({
            prosumer: prosumer, // TODO: msg.sender
            startTime: startTime,
            endTime: endTime,
            energy: energy,
            price: price
        });
    }
    
    function postSellingOffer(uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 price) public { // TODO: function postSellingOffer(uint64 startTime, uint64 endTime, uint64 energy) public {
        require(startTime <= endTime);
        SellingOfferPosted(numSellingOffers, prosumer, startTime, endTime, energy, price);
        sellingOffers[numSellingOffers++] = Offer({
            prosumer: prosumer, // TODO: msg.sender
            startTime: startTime,
            endTime: endTime,
            energy: energy,
            price: price
        });
    }
    
    struct Trade {
        uint64 sellerID;
        uint64 buyerID;
        uint64 time;
        uint64 power;
        uint64 price;
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
    
    event SolutionCreated(uint64 ID);
    
    function createSolution() public returns (uint64 solutionID) {
        SolutionCreated(numSolutions);
        solutions[numSolutions] = Solution({
            numTrades: 0,
            objective: 0
        });
        if (numSolutions == 0)
            bestSolution = solutions[numSolutions];
        return numSolutions++;
    }
    
    event TradeAdded(uint64 solutionID, uint64 sellerID, uint64 buyerID, uint64 time, uint64 power, uint64 price, uint64 objective);
    
    function addTrade(uint64 solutionID, uint64 sellerID, uint64 buyerID, uint64 time, uint64 power, uint64 price) public {
        require(solutionID < numSolutions);
        require(sellerID < numSellingOffers);
        require(buyerID < numBuyingOffers);
        
        // check if buyer and seller are matchable
        require(price >= sellingOffers[sellerID].price);
        require(price <= buyingOffers[buyerID].price);
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
           power: power,
           price: price
        });
        
        solution.objective += power;
        if (solution.objective > bestSolution.objective)
            bestSolution = solution;
        TradeAdded(solutionID, sellerID, buyerID, time, power, price, solution.objective);
    }
}

