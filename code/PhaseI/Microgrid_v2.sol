pragma solidity ^0.4.11;

contract TradingService {
    address private DSO;
    
    function TradingService() {
        DSO = msg.sender;
    }
    
    function test() public {
        addFinancialBalance(msg.sender, 1000);
        depositFinancial(msg.sender, 500);
        addFinancialBalance(msg.sender, 2000);
        depositFinancial(msg.sender, 1000);
        
        uint64 assetProd = createEnergyAsset(msg.sender, 100, 8, 10);
        uint64 assetCons = createEnergyAsset(msg.sender, -200, 9, 11);
        uint64 offer1 = postOffer(assetProd, 10);
        rescindOffer(offer1);
        uint64 offer2 = postOffer(assetProd, 5);
        acceptOffer(offer2, assetCons);
        depositEnergyAsset(assetProd);
        depositEnergyAsset(assetCons);
    }
    
    // Financial Assets
    
    mapping(address => uint64) private financialBalance;
    
    event FinancialWithdrawn(address prosumer, uint64 amount);
    event FinancialDeposited(address prosumer, uint64 amount);
    
    function addFinancialBalance(address prosumer, uint64 amount) public {
        require(msg.sender == DSO);
        financialBalance[prosumer] += amount;
        FinancialWithdrawn(prosumer, amount);
    }
    
    function depositFinancial(address prosumer, uint64 amount) public {
        require(financialBalance[msg.sender] >= amount);
        financialBalance[prosumer] -= amount;
        FinancialDeposited(prosumer, amount);
    }
    
    // Energy Assets
    
    enum AssetType { Production, Consumption }
    
    struct EnergyAsset {
        address owner;
        AssetType assetType;
        uint64 power; // amount of power to be produced or consumed 
        uint64 start; // first time interval in which energy is to be produced
        uint64 end;   // last time interval in which energy is to be produced
    }
    
    mapping(uint64 => EnergyAsset) private energyAssets;
    uint64 private nextEnergyAssetID = 0;
    
    event AssetWithdrawn(address prosumer, uint64 assetID, int64 power, uint64 start, uint64 end);
    event AssetDeposited(address prosumer, uint64 assetID, int64 power, uint64 start, uint64 end);
    event AssetCreated(address prosumer, uint64 assetID);

    function createEnergyAsset(address prosumer, int64 power, uint64 start, uint64 end) public returns(uint64 assetID) {
        require(msg.sender == DSO);
        energyAssets[nextEnergyAssetID] = EnergyAsset({
            assetType: power > 0 ? AssetType.Production : AssetType.Consumption,
            power: power > 0 ? uint64(power) : uint64(-power),
            start: start, 
            end: end, 
            owner: prosumer});
        AssetWithdrawn(prosumer, nextEnergyAssetID, power, start, end);
        return nextEnergyAssetID++;
    }
    
    function depositEnergyAsset(uint64 assetID) public {
        EnergyAsset storage asset = energyAssets[assetID];
        require(msg.sender == asset.owner);
        asset.owner = address(this);
        int64 power = asset.assetType == AssetType.Production ? int64(asset.power) : int64(-asset.power);
        AssetDeposited(msg.sender, assetID, power, asset.start, asset.end);
    }
    
    function splitAssetByStart(uint64 assetID, uint64 newStart) internal {
        EnergyAsset storage asset = energyAssets[assetID];
        if (asset.start < newStart && asset.end >= newStart) {
            uint64 newAssetID = nextEnergyAssetID++;
            energyAssets[newAssetID] = EnergyAsset({
                assetType: asset.assetType,
                power: asset.power, 
                start: asset.start, 
                end: newStart - 1, 
                owner: asset.owner});
            asset.start = newStart;
            AssetCreated(asset.owner, newAssetID);
        }
    }
    
    function splitAssetByEnd(uint64 assetID, uint64 newEnd) internal {
        EnergyAsset storage asset = energyAssets[assetID];
        if (asset.start <= newEnd && asset.end > newEnd) {
            uint64 newAssetID = nextEnergyAssetID++;
            energyAssets[newAssetID] = EnergyAsset({
                assetType: asset.assetType,
                power: asset.power, 
                start: newEnd + 1, 
                end: asset.end, 
                owner: asset.owner});
            asset.end = newEnd;
            AssetCreated(asset.owner, newAssetID);
        }
    }
    
    function splitAssetByPower(uint64 assetID, uint64 newPower) internal {
        EnergyAsset storage asset = energyAssets[assetID];
        if (asset.power > newPower) {
            uint64 newAssetID = nextEnergyAssetID++;
            energyAssets[newAssetID] = EnergyAsset({
                assetType: asset.assetType,
                power: asset.power - newPower, 
                start: asset.start, 
                end: asset.end, 
                owner: asset.owner});
            asset.power = newPower;
            AssetCreated(asset.owner, newAssetID);
        }
    }
    
    // Energy Ask and Bid Offers
    
    enum OfferType { Ask, Bid }
    enum OfferState { Open, Rescinded, Closed }

    struct Offer {
        address poster;
        OfferType offerType;
        uint64 assetID;
        uint64 price;
        OfferState state;
    }
    
    mapping (uint64 => Offer) offers;
    uint64 nextOfferID = 0;
    
    event OfferPosted(uint64 offerID, int64 power, uint64 start, uint64 end, uint64 price);
    event OfferRescinded(uint64 offerID);
    event OfferAccepted(uint64 offerID, uint64 transPower, uint64 transStart, uint64 transEnd, uint64 price);
    
    function postOffer(uint64 assetID, uint64 price) public returns (uint64 offerID) {
        EnergyAsset storage asset = energyAssets[assetID];
        uint64 cost = price * asset.power * (asset.end + 1 - asset.start);
        // Checks
        require(asset.owner == msg.sender);
        if (asset.assetType == AssetType.Consumption) 
            require(financialBalance[msg.sender] >= cost);
        // Effects
        asset.owner = address(this);
        if (asset.assetType == AssetType.Consumption) {
            financialBalance[msg.sender] -= cost;
            OfferType offerType = OfferType.Bid;
        }
        else {
            offerType = OfferType.Ask;
        }
        offers[nextOfferID] = Offer({
            poster: msg.sender, 
            offerType: offerType,
            assetID: assetID, 
            price: price,
            state: OfferState.Open
        });
        int64 power = asset.assetType == AssetType.Production ? int64(asset.power) : -int64(asset.power);
        OfferPosted(nextOfferID, power, asset.start, asset.end, price);
        return nextOfferID++;
    }
    
    function rescindOffer(uint64 offerID) public {
        Offer storage offer = offers[offerID];
        EnergyAsset storage asset = energyAssets[offer.assetID];
        // Checks
        require(offer.poster == msg.sender);
        require(offer.state == OfferState.Open);
        // Effects
        offer.state = OfferState.Rescinded;
        asset.owner = msg.sender;
        if (offer.offerType == OfferType.Bid)
          financialBalance[msg.sender] += offer.price * asset.power * (asset.end + 1 - asset.start);
        OfferRescinded(offerID);
    }
    
    function acceptOffer(uint64 offerID, uint64 assetID) public {
        Offer storage offer = offers[offerID];
        EnergyAsset storage offeredAsset = energyAssets[offer.assetID];
        EnergyAsset storage providedAsset = energyAssets[assetID];
        uint64 transStart = offeredAsset.start > providedAsset.start ? offeredAsset.start : providedAsset.start;
        uint64 transEnd = offeredAsset.end < providedAsset.end ? offeredAsset.end : providedAsset.end;
        uint64 transPower = offeredAsset.power < providedAsset.power ? offeredAsset.power : providedAsset.power;
        uint64 cost = offer.price * transPower * (transEnd + 1 - transStart);
        // Checks 
        require(offer.state == OfferState.Open);
        require(providedAsset.owner == msg.sender);
        require(!(offeredAsset.end < providedAsset.start && offeredAsset.start > providedAsset.end)); // assets overlap
        if (offer.offerType == OfferType.Ask) {
            require(providedAsset.assetType == AssetType.Consumption);
            require(financialBalance[msg.sender] >= cost);
        }
        else
            require(offeredAsset.assetType == AssetType.Production);
        // Effects
        // split assets
        offeredAsset.owner = offer.poster;  // assets inherit ownership
        splitAssetByStart(offer.assetID, transStart);
        splitAssetByStart(assetID, transStart);
        splitAssetByEnd(offer.assetID, transEnd);
        splitAssetByEnd(assetID, transEnd);
        splitAssetByPower(offer.assetID, transPower);
        splitAssetByPower(assetID, transPower);
        // transfer assets
        if (offer.offerType == OfferType.Ask) {
            financialBalance[msg.sender] -= cost;
            financialBalance[offer.poster] += cost;
        }
        else
            financialBalance[msg.sender] += cost;
        providedAsset.owner = offer.poster;
        offeredAsset.owner = msg.sender;
        offer.state = OfferState.Closed;
        OfferAccepted(offerID, transPower, transStart, transEnd, offer.price);
    }
}

