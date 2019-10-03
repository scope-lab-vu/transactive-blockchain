pragma solidity ^0.4.19;

contract MatchingContract {
    uint64 Cint; // maximum power produced (or consumed) within a feeder
    uint64 Cext; // maximum power outgoing from (incoming to) a feeder
    uint64 nextInterval; // next time interval to be finalized
    
    function setup(uint64 _Cint, uint64 _Cext, uint64 _nextInterval) public {
      Cint = _Cint;
      Cext = _Cext;
      nextInterval = _nextInterval;
    }
    
    event ProsumerRegistered(uint64 prosumer, uint64 feeder);
    
    mapping(uint64 => uint64) prosumerFeeder; // TODO: mapping(address => uint64) prosumerFeeder;
    
    function registerProsumer(uint64 prosumer, uint64 feeder) public { // TODO: function addProsumer(address prosumer, uint64 feeder) public {
        prosumerFeeder[prosumer] = feeder;
        emit ProsumerRegistered(prosumer, feeder);
    }
    
    struct Offer {
        uint64 prosumer; // TODO: address prosumer;
        uint64 startTime;
        uint64 endTime;
        uint64 energy;
    }
    
    mapping(uint64 => Offer) buyingOffers;
    uint64 numBuyingOffers = 0;
    mapping(uint64 => Offer) sellingOffers;
    uint64 numSellingOffers = 0;
    
    event BuyingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy);
    event SellingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy);
    
    function postBuyingOffer(uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy) public { // TODO: function postBuyingOffer(uint64 startTime, uint64 endTime, uint64 energy) public {
        require(startTime <= endTime);
        emit BuyingOfferPosted(numBuyingOffers, prosumer, startTime, endTime, energy);
        buyingOffers[numBuyingOffers++] = Offer({
            prosumer: prosumer, // TODO: msg.sender
            startTime: startTime,
            endTime: endTime,
            energy: energy
        });
    }
    
    function postSellingOffer(uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy) public { // TODO: function postSellingOffer(uint64 startTime, uint64 endTime, uint64 energy) public {
        require(startTime <= endTime);
        emit SellingOfferPosted(numSellingOffers, prosumer, startTime, endTime, energy);
        sellingOffers[numSellingOffers++] = Offer({
            prosumer: prosumer, // TODO: msg.sender
            startTime: startTime,
            endTime: endTime,
            energy: energy
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
    int64 bestSolution = -1;
        
    event SolutionCreated(uint64 solutionID, uint64 solverID);
    
    function createSolution(uint64 solverID) public {
        solutions[numSolutions] = Solution({
            numTrades: 0,
            objective: 0
        });
        emit SolutionCreated(numSolutions, solverID);
        numSolutions += 1;
    }
    
    event TradeAdded(uint64 solutionID, uint64 sellerID, uint64 buyerID, uint64 time, uint64 power, uint64 objective);
    event Test(uint64 an_int);
    
    function addTrade(uint64 solutionID, uint64 sellerID, uint64 buyerID, uint64 time, uint64 power) public {
        emit Test(1);
        require(solutionID < numSolutions);
        require(sellerID < numSellingOffers);
        require(buyerID < numBuyingOffers);
        
        require(time >= nextInterval);
        
    //     // check if buyer and seller are matchable
    //     require(time >= sellingOffers[sellerID].startTime);
    //     require(time <= sellingOffers[sellerID].endTime);
    //     require(time >= buyingOffers[buyerID].startTime);
    //     require(time <= buyingOffers[buyerID].endTime);

    //     // notation        
    //     Solution storage solution = solutions[solutionID];
    //     uint64 energy = power; // assume interval to be unit length for power to energy conversion
    //     uint64 sellingFeeder = prosumerFeeder[sellingOffers[sellerID].prosumer];
    //     uint64 buyingFeeder = prosumerFeeder[buyingOffers[buyerID].prosumer];
        
    //     // update seller, buyer, seller feeder, and buyer feeder production and consumption
    //     solution.sellerProduction[sellerID] += energy;
    //     solution.buyerConsumption[buyerID] += energy;
    //     solution.feederProduction[sellingFeeder][time] += power;
    //     solution.feederConsumption[buyingFeeder][time] += power;

    //     // eq:constrEnergyProd        
    //     require(solution.sellerProduction[sellerID] <= sellingOffers[sellerID].energy);
    //     // eq:constrEnergyCons       
    //     require(solution.buyerConsumption[buyerID] <= buyingOffers[buyerID].energy);
    //     // eq:constrIntProd
    //     require(solution.feederProduction[sellingFeeder][time] <= Cint);
    //     // eq:constrIntCons
    //     require(solution.feederConsumption[buyingFeeder][time] <= Cint);
    //     // eq:constrExtProd
    //     require(solution.feederProduction[sellingFeeder][time] - solution.feederConsumption[sellingFeeder][time] <= Cext);
    //     // eq:constrExtCons
    //     require(solution.feederConsumption[buyingFeeder][time] - solution.feederConsumption[buyingFeeder][time] <= Cext);
        
    //     // add trade to solution
    //     solution.trades[solution.numTrades++] = Trade({
    //        sellerID: sellerID,
    //        buyerID: buyerID,
    //        time: time,
    //        power: power
    //     });
        
    //     solution.objective += power;
    //     if ((bestSolution < 0) || (solution.objective > solutions[uint64(bestSolution)].objective))
    //         bestSolution = int64(solutionID);

    //     emit TradeAdded(solutionID, sellerID, buyerID, time, power, solution.objective);
    }
    
    event Finalized(uint64 interval, int64 bestSolution);
    event TradeFinalized(uint64 sellerID, uint64 buyerID, uint64 time, uint64 power);
    
    function finalize(uint64 interval) public {
        require(interval == nextInterval);
      
        emit Finalized(interval, bestSolution);
      
        if (bestSolution >= 0) {
            Solution storage solution = solutions[uint64(bestSolution)];
        
            for (uint64 i = 0; i < solution.numTrades; i++) {
                Trade storage trade = solution.trades[i];
                if (trade.time == nextInterval) {
                    uint64 energy = trade.power; // assume interval to be unit length for power to energy conversion
                    sellingOffers[trade.sellerID].energy -= energy;
                    buyingOffers[trade.buyerID].energy -= energy;
                    emit TradeFinalized(trade.sellerID, trade.buyerID, trade.time, trade.power);
                }
            }
        
            bestSolution = -1;
        }
      
        nextInterval++;
    }
}

