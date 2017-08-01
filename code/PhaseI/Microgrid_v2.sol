pragma solidity ^0.4.11;

contract TradingService {
    address private DSO;
    
    function TradingService() {
        DSO = msg.sender;
    }
    
    function abs(int64 value) internal constant returns (uint64 absoluteValue) {
        if (value < 0)
            return uint64(-value);
        else
            return uint64(value);
    }
    
    mapping(address => uint64) private financialBalance;
    
    function addBalance(uint64 amount, address prosumer) {
        require(msg.sender == DSO);
        financialBalance[prosumer] += amount;
    }
    
    // Energy Assets
    
    struct EnergyAsset {
        int64 power; // amount of power to be produced or consumed (positive for production asset, negative for consumption asset)
        uint64 start; // first time interval in which energy is to be produced
        uint64 end;   // last time interval in which energy is to be produced
        address owner;
    }
    
    mapping(uint64 => EnergyAsset) private energyAssets;
    uint64 private nextEnergyAssetID = 0;
    
    function createEnergyAsset(int64 power, uint64 start, uint64 end, address prosumer) returns (uint64 assetID) {
        require(msg.sender == DSO);
        energyAssets[nextEnergyAssetID] = EnergyAsset({power: power, start: start, end: end, owner: prosumer});
        return nextEnergyAssetID++;
    }
    
    event AssetsWithdrawn(uint64 assetID, uint64 balance, address prosumer);
    
    function createAssets(int64 power, uint64 start, uint64 end, uint64 balance, address prosumer) returns (uint64 _assetID) {
        addBalance(balance, prosumer);
        uint64 assetID = createEnergyAsset(power, start, end, prosumer);
        AssetsWithdrawn(assetID, balance, prosumer);
        return assetID;
    }
    
    function depositEnergyAsset(uint64 assetID) internal {
        EnergyAsset storage asset = energyAssets[assetID];
        require(msg.sender == asset.owner);
        asset.owner == DSO;
    }
    
    event AssetsDeposited(uint64 assetID, uint64 balance, address prosumer);
    
    function depositAssets(uint64 assetID, uint64 balance) public {
        depositEnergyAsset(assetID);
        financialBalance[msg.sender] -= balance;
        AssetsDeposited(assetID, balance, msg.sender);
    }
    
    event AssetCreated(uint64 assetID, address owner);
    
    function splitAssetByStart(uint64 assetID, uint64 newStart) internal {
        EnergyAsset storage asset = energyAssets[assetID];
        if (asset.start < newStart && asset.end >= newStart) {
            uint64 newAssetID = nextEnergyAssetID++;
            energyAssets[newAssetID] = EnergyAsset({
                power: asset.power, 
                start: asset.start, 
                end: newStart - 1, 
                owner: asset.owner});
            asset.start = newStart;
            AssetCreated(newAssetID, asset.owner);
        }
    }
    
    function splitAssetByEnd(uint64 assetID, uint64 newEnd) internal {
        EnergyAsset storage asset = energyAssets[assetID];
        if (asset.start <= newEnd && asset.end > newEnd) {
            uint64 newAssetID = nextEnergyAssetID++;
            energyAssets[newAssetID] = EnergyAsset({
                power: asset.power, 
                start: newEnd + 1, 
                end: asset.end, 
                owner: asset.owner});
            asset.end = newEnd;
            AssetCreated(newAssetID, asset.owner);
        }
    }
    
    function splitAssetByPower(uint64 assetID, uint64 newPower) internal {
        EnergyAsset storage asset = energyAssets[assetID];
        if (abs(asset.power) > newPower) {
            uint64 newAssetID = nextEnergyAssetID++;
            energyAssets[newAssetID] = EnergyAsset({
                power: asset.power > 0 ? asset.power - int64(newPower) : asset.power + int64(newPower), 
                start: asset.start, 
                end: asset.end, 
                owner: asset.owner});
            asset.power = asset.power > 0 ? int64(newPower) : -int64(newPower);
            AssetCreated(newAssetID, asset.owner);
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
    
    event OfferPosted(uint64 offerID);
    
    function postOffer(uint64 assetID, uint64 price) public returns (uint64 offerID) {
        EnergyAsset storage asset = energyAssets[assetID];
        uint64 cost = price * abs(asset.power) * (asset.end + 1 - asset.start);
        // Checks
        require(asset.owner == msg.sender);
        if (asset.power < 0) 
            require(financialBalance[msg.sender] >= cost);
        // Effects
        asset.owner = address(this);
        if (asset.power < 0) {
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
        OfferPosted(nextOfferID);
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
          financialBalance[msg.sender] += offer.price * abs(asset.power) * (asset.end + 1 - asset.start);
    }
    
    event OfferAccepted(uint64 offerID);
    
    function acceptOffer(uint64 offerID, uint64 assetID) public {
        Offer storage offer = offers[offerID];
        EnergyAsset storage offeredAsset = energyAssets[offer.assetID];
        EnergyAsset storage providedAsset = energyAssets[assetID];
        uint64 cost = offer.price * abs(offeredAsset.power) * (offeredAsset.end + 1 - offeredAsset.start);
        // Checks
        require(offer.state == OfferState.Open);
        require(providedAsset.owner == msg.sender);
        if (offer.offerType == OfferType.Ask) 
            require(financialBalance[msg.sender] >= cost);
        require(offeredAsset.power == -providedAsset.power);
        require(offeredAsset.start == providedAsset.start);
        require(offeredAsset.end == providedAsset.end);
        // Effects
        if (offer.offerType == OfferType.Ask) {
            financialBalance[msg.sender] -= cost;
            financialBalance[offer.poster] += cost;
        }
        else
            financialBalance[msg.sender] += cost;
        providedAsset.owner = offer.poster;
        offeredAsset.owner = msg.sender;
        offer.state = OfferState.Closed;
        OfferAccepted(offerID);
    }
    
    function acceptOfferPartial(uint64 offerID, uint64 assetID) public {
        Offer storage offer = offers[offerID];
        EnergyAsset storage offeredAsset = energyAssets[offer.assetID];
        EnergyAsset storage providedAsset = energyAssets[assetID];
        uint64 transStart = offeredAsset.start > providedAsset.start ? offeredAsset.start : providedAsset.start;
        uint64 transEnd = offeredAsset.end < providedAsset.end ? offeredAsset.end : providedAsset.end;
        uint64 transPower = abs(offeredAsset.power) < abs(providedAsset.power) ? abs(offeredAsset.power) : abs(providedAsset.power);
        uint64 cost = offer.price * transPower * (transEnd + 1 - transStart);
        // Checks 
        require(offer.state == OfferState.Open);
        require(providedAsset.owner == msg.sender);
        require(!(offeredAsset.end < providedAsset.start && offeredAsset.start > providedAsset.end)); // assets overlap
        if (offer.offerType == OfferType.Ask) {
            require(offeredAsset.power < 0);
            require(financialBalance[msg.sender] >= cost);
        }
        else
            require(offeredAsset.power > 0);
        // Effects
        // split assets
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
        OfferAccepted(offerID);
    }
}

