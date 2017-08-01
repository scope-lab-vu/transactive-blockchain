pragma solidity ^0.4.11;

contract TradingService {
    address private DSO;
    
    function TradingService() {
        DSO = msg.sender;
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
    
    function depositEnergyAsset(uint64 assetID) {
        EnergyAsset storage asset = energyAssets[assetID];
        require(msg.sender == asset.owner);
        asset.owner == DSO;
    }
    
    event AssetsDeposited(uint64 assetID, uint64 balance, address prosumer);
    
    function depositAssets(uint64 assetID, uint64 balance) {
        depositEnergyAsset(assetID);
        financialBalance[msg.sender] -= balance;
        AssetsDeposited(assetID, balance, msg.sender);
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
    
    event OfferPosted(uint64 offerID, uint64 price, uint64 assetID);
    
    function postOffer(uint64 assetID, uint64 price) returns (uint64 offerID) {
        EnergyAsset storage asset = energyAssets[assetID];
        // Checks
        require(asset.owner == msg.sender);
        if (asset.power < 0) 
            require(financialBalance[msg.sender] >= price);
        // Effects
        asset.owner = address(this);
        if (asset.power < 0) {
            financialBalance[msg.sender] -= price;
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
        OfferPosted(nextOfferID, price, assetID);
        return nextOfferID++;
    }
    
    function rescindOffer(uint64 offerID) {
        Offer storage offer = offers[offerID];
        // Checks
        require(offer.poster == msg.sender);
        require(offer.state == OfferState.Open);
        // Effects
        offer.state = OfferState.Rescinded;
        energyAssets[offer.assetID].owner = msg.sender;
        if (offer.offerType == OfferType.Bid)
          financialBalance[msg.sender] += offer.price;
    }
    
    event OfferAccepted(uint64 offerID);
    
    function acceptOffer(uint64 offerID, uint64 assetID) {
        Offer storage offer = offers[offerID];
        EnergyAsset storage offeredAsset = energyAssets[offer.assetID];
        EnergyAsset storage providedAsset = energyAssets[assetID];
        // Checks
        require(offer.state == OfferState.Open);
        require(providedAsset.owner == msg.sender);
        if (offer.offerType == OfferType.Ask) 
            require(financialBalance[msg.sender] >= offer.price);
        require(offeredAsset.power == -providedAsset.power);
        require(offeredAsset.start == providedAsset.start);
        require(offeredAsset.end == providedAsset.end);
        // Effects
        if (offer.offerType == OfferType.Ask) {
            financialBalance[msg.sender] -= offer.price;
            financialBalance[offer.poster] += offer.price;
        }
        else {
            financialBalance[msg.sender] += offer.price;
        }
        providedAsset.owner = offer.poster;
        offeredAsset.owner = msg.sender;
        offer.state = OfferState.Closed;
        OfferAccepted(offerID);
    }
}

