pragma solidity ^0.4.11;

contract Regulator {
    address DSO;
    
    function Regulator() {
        DSO = msg.sender;
    }
    
    mapping(address => bool) smartMeters;
    
    function authorizeSmartMeter(address meter) {
        require(msg.sender == DSO);
        smartMeters[meter] = true;
    }

    function banSmartMeter(address meter) {
        require(msg.sender == DSO);
        smartMeters[meter] = false;
    }
    
    function isAuthorized(address meter) constant returns (bool authorized) {
        return smartMeters[meter];
    }
}

contract SmartMeter {
    address prosumer;
    AssetStorage assetStorage;
    mapping (uint64 => uint64) productionWithdrawn;
    mapping (uint64 => uint64) consumptionWithdrawn;
    uint64 productionLimit;
    uint64 consumptionLimit;
    mapping (uint64 => int64) balance;
    
    function SmartMeter(AssetStorage _assetStorage, address _prosumer, uint64 _productionLimit, uint64 _consumptionLimit) {
        assetStorage = _assetStorage;
        prosumer = _prosumer;
        productionLimit = _productionLimit;
        consumptionLimit = _consumptionLimit;
    }
    
    function withdraw(int64 power, uint64 start, uint64 end) returns (uint64 assetID) {
        require(msg.sender == prosumer);
        
        if (power >= 0) { // withdrawing energy production asset
            uint64 absPower = uint64(power);
            for (uint64 time = start; time <= end; time++)
                require(absPower + productionWithdrawn[time] < productionLimit); 
            for (time = start; time <= end; time++) {
                productionWithdrawn[time] += absPower; 
                balance[time] -= power; 
            }
            return assetStorage.createEnergyAsset(power, start, end, prosumer);
        }
        else { 
            absPower = uint64(-power);
            for (time = start; time <= end; time++) 
                require(absPower + consumptionWithdrawn[time] < consumptionLimit); 
            for (time = start; time <= end; time++)
                consumptionWithdrawn[time] += absPower;
            return assetStorage.createEnergyAsset(power, start, end, prosumer);
        }
    }
    
    function deposit(uint64 assetID) {
        require(msg.sender == prosumer);
        var (power, start, end, owner) = assetStorage.getEnergyAsset(assetID);
        require(owner == prosumer);
        assetStorage.destroyEnergyAsset(assetID);
        // TODO: decrease withdrawn amounts as well
        if (power >= 0)
            for (uint64 time = start; time < end; time++)
                balance[time] += power;
    }
}

contract AssetStorage {
    Regulator DSO;
    
    function AssetStorage(Regulator _DSO) {
        DSO = _DSO;
    }
    
    struct EnergyAsset {
        int64 power; // amount of power to be produced or consumed
        uint64 start; // first time interval in which energy is to be produced
        uint64 end;   // last time interval in which energy is to be produced
        address owner;
    }
    
    mapping(uint64 => EnergyAsset) energyAssets;
    uint64 nextEnergyAssetID = 0;
    
    function createEnergyAsset(int64 power, uint64 start, uint64 end, address owner) returns (uint64 assetID) {
        require(DSO.isAuthorized(msg.sender));
        energyAssets[nextEnergyAssetID] = EnergyAsset({power: power, start: start, end: end, owner: owner});
        return nextEnergyAssetID++;
    }
    
    function getEnergyAsset(uint64 assetID) constant returns (int64 power, uint64 start, uint64 end, address owner) {
        EnergyAsset asset = energyAssets[assetID];
        return (asset.power, asset.start, asset.end, asset.owner);
    }
    
    function destroyEnergyAsset(uint64 assetID) {
        require(DSO.isAuthorized(msg.sender));
        energyAssets[assetID].owner = address(this);
    }
    
    struct Transaction {
        address seller;
        uint64 sellerAsset;
        uint64 sellerPayment;
        uint64 buyerAsset;
        uint64 buyerPayment;
        bool finished;
    }
    
    mapping(uint64 => Transaction) transactions;
    uint64 nextTransactionID = 0;
    
    modifier costs(uint64 price) {
        if (msg.value >= price) {
            _;
        }
    }
    
    function beginTransaction(uint64 sellerAsset, uint64 sellerPayment, uint64 buyerAsset, uint64 buyerPayment) payable costs(sellerPayment) returns (uint64 transactionID) {
        require(msg.sender == energyAssets[sellerAsset].owner);
        // trading is limited to simle exchanges (for now)
        require(energyAssets[sellerAsset].start == energyAssets[buyerAsset].start);
        require(energyAssets[sellerAsset].end == energyAssets[buyerAsset].end);
        require(energyAssets[sellerAsset].power == -energyAssets[buyerAsset].power);
        energyAssets[sellerAsset].owner = address(this);
        transactions[nextTransactionID] = Transaction({seller: msg.sender, sellerAsset: sellerAsset, sellerPayment: sellerPayment, buyerAsset: buyerAsset, buyerPayment: buyerPayment, finished: false});
        return nextTransactionID++;
    }
    
    function cancelTransaction(uint64 transactionID) {
        require(msg.sender == transactions[transactionID].seller);
        require(transactions[transactionID].finished == false);
        transactions[transactionID].finished = true;
        energyAssets[transactions[transactionID].sellerAsset].owner = msg.sender;
        msg.sender.transfer(transactions[transactionID].sellerPayment);
    }
    
    function finishTransaction(uint64 transactionID) payable costs(transactions[transactionID].buyerPayment) payable costs(transactions[transactionID].buyerPayment) {
        Transaction tran = transactions[transactionID];
        require(msg.sender == energyAssets[tran.buyerAsset].owner);
        require(tran.finished == false);
        transactions[transactionID].finished == true;
        // process assets
        energyAssets[tran.sellerAsset].owner = msg.sender;
        energyAssets[tran.buyerAsset].owner = tran.seller;
        // process payments
        msg.sender.transfer(tran.sellerPayment);
        tran.seller.transfer(tran.buyerPayment);
    }
}

contract BiddingService {
    AssetStorage assetStorage;
    
    function BiddingService(AssetStorage _assetStorage) {
        assetStorage = _assetStorage;    
    }
    
    event BidPosted (uint64 bidID);
    event BidRemoved (uint64 bidID);

    struct Bid {
        uint64 assetID;
        int64 price;
        address poster;
    }
    
    mapping(uint64 => Bid) bids;
    uint64 nextBidID = 0;
    
    function postBid(uint64 assetID, int64 price) returns (uint64 bidID) {
        var (, , , owner) = assetStorage.getEnergyAsset(assetID);
        require(msg.sender == owner);
        bids[nextBidID] = Bid({assetID: assetID, price: price, poster: msg.sender});
        BidPosted(nextBidID);
        return nextBidID++;
    }
    
    function removeBid(uint64 bidID) {
        require(msg.sender == bids[bidID].poster);
        BidRemoved(bidID);
    }
}




