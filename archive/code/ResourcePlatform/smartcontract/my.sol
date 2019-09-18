pragma solidity ^0.4.25;

contract ResourceAllocation {
    // State definitions and events

    enum States {
        Offer,
        Solve
    }

    States private state = States.Offer;

    event Closed();
    event Debug(string Description, uint64 value, bool boolean, uint64 state, uint256 e256);

    // Resource offer structures, events, and functions

    struct ResourceOffer {
        uint64 actorID; // ID of the resource provider
        uint64 architecture; // CPU architecture
        uint64 capCPU; // CPU capacity in instructions per second
        uint64 capRAM; // RAM capacity in MB
        uint64 capStorage; // drive storage capacity in MB
        uint64 price; // price per executed CPU instruction
        bool posted;
    }

    ResourceOffer[] resourceOffers;

    event ResourceOfferPosted(uint64 offerID, uint64 actorID, uint64 architecture, uint64 capCPU, uint64 capRAM, uint64 capStorage, uint64 price);
    event ResourceOfferCanceled(uint64 offerID);

    function postResourceOffer(uint64 actorID, uint64 architecture, uint64 capCPU, uint64 capRAM, uint64 capStorage, uint64 price) public {
        require(state == States.Offer);
        require(capCPU > 0);
        require(capRAM > 0);
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

    function cancelResourceOffer(uint64 offerID) public {
        require(state == States.Offer);
        require(offerID < resourceOffers.length);
        require(resourceOffers[offerID].posted);
        //Actions
        resourceOffers[offerID].posted = false;
        emit ResourceOfferCanceled(offerID);
    }

    // Job offer structures, events, and functions

    struct ArchitectureJob { // architecture specific job description
        uint64 reqCPU; // CPU request in instructions per second
        uint64 reqRAM; // RAM request in MB
        uint64 reqStorage; // drive storage request in MB
        uint256 imageHash; // hash of the job image
    }

    struct JobOffer {
        uint64 actorID; // ID of the job provider
        mapping(uint64 => ArchitectureJob) desc; // mapping from architectures to job descriptions
        uint64 timeLimit; // maximum time spent on the job in seconds
        uint64 price; // price for executing the job
        bool posted;
    }

    JobOffer[] jobOffers;

    event JobOfferCreated(uint64 offerID, uint64 actorID, uint64 timeLimit, uint64 price, uint64 ioid);
    event JobOfferUpdated(uint64 offerID, uint64 architecture, uint64 reqCPU, uint64 reqRAM, uint64 reqStorage, uint256 imageHash);
    event JobOfferPosted(uint64 offerID);
    event JobOfferCanceled(uint64 offerID);

    function createJobOffer(uint64 actorID, uint64 timeLimit, uint64 price, uint64 ioid) public {
        // emit Debug("str cJO", offerID, state == States.Offer, uint64(state), 0) ;
        require(state == States.Offer);
        //Actions
        uint64 offerID = uint64(jobOffers.length);
        jobOffers.push(JobOffer({
            actorID: actorID,
            timeLimit: timeLimit,
            price: price,
            posted: false
        }));
        emit JobOfferCreated(offerID, actorID, timeLimit, price, ioid);
    }

    function updateJobOffer(uint64 offerID, uint64 architecture, uint64 reqCPU, uint64 reqRAM, uint64 reqStorage, uint256 imageHash) public {
        //emit Debug("str uJO", offerID, state == States.Offer, uint64(state)) ;
        require(state == States.Offer);
        require(offerID < jobOffers.length);
        require(!jobOffers[offerID].posted);
        require(reqCPU > 0);
        require(reqRAM > 0);
        // Actions
        jobOffers[offerID].desc[architecture] = ArchitectureJob({
            reqCPU: reqCPU,
            reqRAM: reqRAM,
            reqStorage: reqStorage,
            imageHash: imageHash
        });
        emit JobOfferUpdated(offerID, architecture, reqCPU, reqRAM, reqStorage, imageHash);
    }

    function testHash(uint256 imageHash) public{
        emit Debug("str testHash", 0, true, 0, imageHash) ;
    }

    function postJobOffer(uint64 offerID) public {
        require(state == States.Offer);
        require(offerID < jobOffers.length);
        require(!jobOffers[offerID].posted);
        //Actions
        jobOffers[offerID].posted = true;
        emit JobOfferPosted(offerID);
    }

    function postJobCanceled(uint64 offerID) public {
        require(state == States.Offer);
        require(offerID < jobOffers.length);
        require(jobOffers[offerID].posted);
        //Actions
        jobOffers[offerID].posted = false;
        emit JobOfferCanceled(offerID);
    }

    function close() public {
        require(state == States.Offer);
        //Actions
        state = States.Solve;
        emit Closed();
    }

    // Solution structures, events, and functions

    struct Assignment {
        uint64 jobOfferID;
        uint64 resourceOfferID;
    }

    struct Solution {
        uint64 actorID; // ID of the solver
        mapping(uint64 => Assignment) assignments;
        uint64 numAssignments;
        uint64 objective;
        mapping(uint64 => bool) jobAssigned; // true if the job has been assigned in this solution
        mapping(uint64 => uint64) assignedCapCPU; // amount of CPU capacity from a resource offer that has been assigned in this solution
        mapping(uint64 => uint64) assignedCapRAM; // amount of RAM capacity from a resource offer that has been assigned in this solution
        mapping(uint64 => uint64) assignedCapStorage; // amount of storage capacity from a resource offer that has been assigned in this solution
    }

    Solution[] solutions;
    uint64 bestSolution = 0;
    uint64 bestObjective = 0;

    uint256 finalizedResourceOffers = 0;
    uint256 finalizedJobOffers = 0;
    uint256 finalizedSolutions = 0;

    event SolutionCreated(uint64 solutionID, uint64 actorID);
    event AssignmentAdded(uint64 solutionID, uint64 jobOfferID, uint64 resourceOfferID);
    event AssignmentFinalized(uint64 jobOfferID, uint64 resourceOfferID);

    function createSolution(uint64 actorID) public {
        require(state == States.Solve);
        //Actions
        solutions.push(Solution({
            actorID: actorID,
            numAssignments: 0,
            objective: 0
        }));
        emit SolutionCreated(uint64(solutions.length - 1), actorID);
    }

    function addAssignment(uint64 solutionID, uint64 jobOfferID, uint64 resourceOfferID) public {
        require(state == States.Solve);
        require(solutionID < solutions.length);
        require(solutionID >= finalizedSolutions);
        require(jobOfferID >= finalizedJobOffers);
        require(resourceOfferID >= finalizedResourceOffers);
        //Actions
        Solution storage solution = solutions[solutionID];
        require(!solution.jobAssigned[jobOfferID]);
        ResourceOffer storage resourceOffer = resourceOffers[resourceOfferID];
        JobOffer storage jobOffer = jobOffers[jobOfferID];
        ArchitectureJob storage description = jobOffer.desc[resourceOffer.architecture];
        require(description.reqCPU > 0); // check if architecture specific job description exists
        require(jobOffer.price > resourceOffer.price * description.reqCPU * jobOffer.timeLimit);
        solution.assignedCapCPU[resourceOfferID] += description.reqCPU;
        solution.assignedCapRAM[resourceOfferID] += description.reqRAM;
        solution.assignedCapStorage[resourceOfferID] += description.reqStorage;
        require(solution.assignedCapCPU[resourceOfferID] <= resourceOffer.capCPU);
        require(solution.assignedCapRAM[resourceOfferID] <= resourceOffer.capRAM);
        require(solution.assignedCapStorage[resourceOfferID] <= resourceOffer.capStorage);
        solution.assignments[solution.numAssignments] = Assignment({
            jobOfferID: jobOfferID,
            resourceOfferID: resourceOfferID
        });
        solution.numAssignments += 1;
        solution.jobAssigned[jobOfferID] = true;
        solution.objective += jobOffer.price;
        if (solution.objective > bestObjective) {
            bestSolution = solutionID;
            bestObjective = solution.objective;
        }
        emit AssignmentAdded(solutionID, jobOfferID, resourceOfferID);
    }

    function finalize() public {
        require(state == States.Solve);
        //Actions
        if (bestObjective > 0) {
            Solution storage solution = solutions[bestSolution];
            for (uint64 i = 0; i < solution.numAssignments; i++)
                emit AssignmentFinalized(solution.assignments[i].jobOfferID, solution.assignments[i].resourceOfferID);
        }
        bestSolution = 0;
        bestObjective = 0;
        finalizedResourceOffers = resourceOffers.length;
        finalizedJobOffers = jobOffers.length;
        finalizedSolutions = solutions.length;
        state = States.Offer;
    }
}
