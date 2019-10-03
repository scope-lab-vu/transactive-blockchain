pragma solidity ^0.4.19;

contract MatchingContract {
    uint64 Cint; // maximum power produced (or consumed) within a feeder
    uint64 Cext; // maximum power outgoing from (incoming to) a feeder
    uint64 nextInterval; // next time interval to be finalized
    States private state = States.Init;

    enum States {
        Init,
        Offering,
        Solving
    }
    
    function setup(uint64 _Cint, uint64 _Cext, uint64 _nextInterval) public {
      Cint = _Cint;
      Cext = _Cext;
      nextInterval = _nextInterval;
      state = States.Offering;
      StartOffering(_nextInterval);
    }
    
    event StartOffering(uint64 interval);
    event ProsumerRegistered(uint64 prosumer, uint64 feeder);
    
    mapping(uint64 => uint64) prosumerFeeder; // TODO: mapping(address => uint64) prosumerFeeder;
    
    function registerProsumer(uint64 prosumer, uint64 feeder) public { // TODO: function addProsumer(address prosumer, uint64 feeder) public {
        prosumerFeeder[prosumer] = feeder;
        ProsumerRegistered(prosumer, feeder);
    }
    
    struct Offer {
        uint64 prosumer; // TODO: address prosumer;
        uint64 startTime;
        uint64 endTime;
        uint64 energy;
        uint64 value;
    }
    
    mapping(uint64 => Offer) buyingOffers;
    uint64 numBuyingOffers = 0;
    mapping(uint64 => Offer) sellingOffers;
    uint64 numSellingOffers = 0;
    
    event BuyingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 value);
    event SellingOfferPosted(uint64 ID, uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 value);
    
    function postBuyingOffer(uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 value) public { // TODO: function postBuyingOffer(uint64 startTime, uint64 endTime, uint64 energy) public {
        require(startTime <= endTime);
        require(state == States.Offering);

        BuyingOfferPosted(numBuyingOffers, prosumer, startTime, endTime, energy, value);
        buyingOffers[numBuyingOffers++] = Offer({
            prosumer: prosumer, // TODO: msg.sender
            startTime: startTime,
            endTime: endTime,
            energy: energy,
            value: value
        });
    }
    
    function postSellingOffer(uint64 prosumer, uint64 startTime, uint64 endTime, uint64 energy, uint64 value) public { // TODO: function postSellingOffer(uint64 startTime, uint64 endTime, uint64 energy) public {
        require(startTime <= endTime);
        require(state == States.Offering);

        SellingOfferPosted(numSellingOffers, prosumer, startTime, endTime, energy, value);
        sellingOffers[numSellingOffers++] = Offer({
            prosumer: prosumer, // TODO: msg.sender
            startTime: startTime,
            endTime: endTime,
            energy: energy,
            value: value
        });
    }  

    event Solve(uint64 interval);
    event ClearingPrice(uint64 interval, uint64 price);

    function startSolve(uint64 interval) public {
        state = States.Solving;
        Solve(interval);
    }

    function submitClearingPrice(uint64 interval, uint64 price) public {
        ClearingPrice(interval, price);
        nextInterval++;
        state = States.Offering;
        StartOffering(nextInterval);
    }
}

