pragma solidity ^0.4.19;

contract ResourceAllocation {
    uint private creationTime = now;

    //States definition
    enum States {
        InTransition,
        Init,
        Receive,
        Solve
    }
    States private state = States.Init;
    
    struct ResourceOffer {
        uint64 actorID; // ID of the resource provider
        uint64 architecture; // CPU architecture
        uint64 capCPU; // CPU capacity in instructions per second
        uint64 capRAM; // RAM capacity in MB
        uint64 capStorage; // drive storage capacity in MB
        uint64 price; // price per executed CPU instruction
        bool: posted;
    }
    
    struct ArchitectureJob {
        uint64 reqCPU; // CPU request in instructions per second
        uint64 reqRAM; // RAM request in MB
        uint64 reqStorage; // drive storage request in MB
        uint256 imageHash; // hash of the job image
    }
    
    struct JobOffer {
        uint64 actorID; // ID of the job provider
        mapping(uint64 => ArchitectureJob) architectures; // mapping from architectures to job descriptions
        uint64 timeLimit; // maximum time spent on the job in seconds
        uint64 price; // price for executing the job
        bool: posted;
    }
    
    ResourceOffer[] resourceOffers;
    JobOffer[] jobOffers;
    
    event ResourceOfferPosted(uint64 offerID, uint64 actorID, uint64 architecture, uint64 capCPU, uint64 capRAM, uint64 capStorage, uint64 price);
    event ResourceOfferCanceled(uint64 offerID);
    event JobOfferCreated(uint64 offerID, uint64 actorID, uint64 timeLimit, uint64 price);
    event JobOfferUpdated(uint64 offerID, uint64 architecture, uint64 reqCPU, uint64 reqRAM, uint64 reqStorage, uint256 imageHash);
    event JobOfferPosted(uint64 offerID);
    event jobOfferCanceled(uint64 offerID);

    function postResourceOffer(uint64 actorID, uint64 architecture, uint64 capCPU, uint64 capRAM, uint64 capStorage, uint64 price) public {
        require(state == States.Receive);
        //Actions
        resourceOffers.push(ResourceOffer({
            actorID: actorID,      
            architecture: architecture, 
            capCPU: capCPU,
            capRAM: capRAM,
            capStorage: capStorage,
            price: price,
            posted: true
        }));
        emit ResourceOfferPosted(uint64(resourceOffers.length - 1), actorID, architecture, capCPU, capRAM, capStorage, price);
    }

    function cancelResourceOffer(uint64 offerID) {
        require(state == States.Receive);
        //Actions
        resourceOffers[offerID].posted = false;
        emit ResourceOfferCanceled(offerID);
    }
}
