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

    uint64 NUM_TYPES = 1;
    uint64 PRECISION = 4294967296;
    uint64 MAX_QUANTITY = 1;
    struct Offer {
        bool providing; // true: providing offer, false: consumption offer
        uint64 prosumer;
        bool posted;
        mapping(uint64 => uint64) quantity;
        mapping(uint64 => uint64) value;
    }
    Offer[] offers;
    event OfferCreated(uint64 ID, bool providing, uint64 misc, uint64 prosumer);
    event OfferUpdated(uint64 ID, uint64 resourceType, uint64 quantity, uint64 value);
    event OfferPosted(uint64 ID);
    event OfferCanceled(uint64 ID);
    event Debug(string Description, uint64 value, bool boolean, uint64 state);
    event FinalizeRequested(string Description, uint64 state);
    event FinalizeComplete(string Description, uint64 state);

    struct Assignment {
        uint64 providingOfferID;
        uint64 consumingOfferID;
        uint64 resourceType;
        uint64 quantity;
        uint64 value;
    }
    struct Solution {
        mapping(uint64 => Assignment) assignments;
        uint64 numAssignments;
        uint64 objective;
        mapping(uint64 => uint256) allocated;
    }

    Solution[] solutions;
    uint64 bestSolution = 0;
    event SolutionCreated(uint64 ID, uint64 misc);
    event AssignmentAdded(uint64 ID, uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value, uint64 objective);
    event AssignmentFinalized(uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value);

        function check() public
    {
        // emit Debug("str check finalize", 0, false, uint64(state));
        // emit Debug("str state==States.Solve", 0, state==States.Solve, uint64(state));
        // emit Debug("str solutions.length>0", 1, solutions.length > 0, uint64(state));
        emit Debug("str addAssgn", 0, state == States.Solve, uint64(state)) ;
    }

    //Transitions
    function addAssignment (uint64 ID, uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value) public
    {
        require(state == States.Solve);
       //Debug Guards
       //Guards
        // require(ID < solutions.length &&
        // providingOfferID < offers.length &&
        // consumingOfferID < offers.length &&
        // resourceType < NUM_TYPES &&
        // offers[providingOfferID].providing &&
        // offers[providingOfferID].posted &&
        // offers[providingOfferID].quantity[resourceType] > 0
        // && !offers[consumingOfferID].providing &&
        // offers[consumingOfferID].posted &&
        // offers[consumingOfferID].quantity[resourceType] > 0 &&
        // solutions[ID].allocated[providingOfferID] + (uint256(quantity) * PRECISION) / offers[providingOfferID].quantity[resourceType] <= PRECISION
        // && solutions[ID].allocated[consumingOfferID] +(uint256(quantity) * PRECISION) / offers[consumingOfferID].quantity[resourceType] <= PRECISION
        // && value >= offers[providingOfferID].value[resourceType]
        // && value <= offers[consumingOfferID].value[resourceType]);
        //State change
        state = States.InTransition;
        //Actions
        solutions[ID].assignments[solutions[ID].numAssignments] = Assignment({
            providingOfferID: providingOfferID,
            consumingOfferID: consumingOfferID,
            resourceType: resourceType,
            quantity: quantity,
            value: value
        });
        solutions[ID].numAssignments += 1;

        solutions[ID].objective += quantity;
        if (solutions[ID].objective > solutions[bestSolution].objective)
            bestSolution = ID;

        emit AssignmentAdded(ID, providingOfferID, consumingOfferID, resourceType, quantity, value, solutions[ID].objective);

        //State change
        state = States.Solve;
    }

    function cancelOffer (  uint64 ID) public

    {
        require(state == States.Receive);
       //Guards
        require(ID < offers.length && offers[ID].posted);
        //State change
        state = States.InTransition;
        //Actions
        offers[ID].posted = false;
        emit OfferCanceled(ID);

        //State change
        state = States.Receive;
    }

    function close () public

    {
        require(state == States.Receive);

        //State change
        state = States.Solve;
    }

    function createOffer (bool providing, uint64 misc, uint64 prosumer) public

    {
        require(state == States.Receive);

        //State change
        state = States.InTransition;
        //Actions
        offers.push(Offer({      providing: providing,      prosumer: prosumer,      posted: false    }));
        emit OfferCreated(uint64(offers.length - 1), providing, misc, prosumer);

        //State change
        state = States.Receive;
    }

    function checkcreateSolution() public
    {
        //state = States.Solve;
        emit Debug("str ccs state==States.Solve", 0, state==States.Solve, uint64(state));
    }

    function createSolution (  uint64 misc) public

    {
        require(state == States.Solve);
        emit Debug("str Start createSolution", 0, false, uint64(state));
        //State change
        state = States.InTransition;
        //Actions
        solutions.push(Solution({
            numAssignments: 0,
            objective: 0
        }));

        emit SolutionCreated(uint64(solutions.length - 1), misc);
        //State change
        state = States.Solve;
    }


    function finalize () public

    {
        emit FinalizeRequested("str State: ", uint64(state));
        require(state == States.Solve);
       //Guards
        require(solutions.length > 0);
        //State change
        state = States.InTransition;
        //Actions
        Solution storage solution = solutions[bestSolution];
        for (uint64 i = 0; i < solution.numAssignments; i++) {
            Assignment memory assignment = solution.assignments[i];
            emit AssignmentFinalized(assignment.providingOfferID, assignment.consumingOfferID, assignment.resourceType, assignment.quantity, assignment.value);
        }

        //State change
        state = States.Receive;
        emit FinalizeComplete("str State: ", uint64(state));
    }

    function postOffer (  uint64 ID) public

    {
        require(state == States.Receive);
       //Guards
        require(ID < offers.length && !offers[ID].posted);
        //State change
        state = States.InTransition;
        //Actions
        offers[ID].posted = true;
        emit OfferPosted(ID);

        //State change
        state = States.Receive;
    }

    function setup (uint64 numTypes, uint64 precision, uint64 maxQuantity) public

    {
        require(state == States.Init);

        //State change
        state = States.InTransition;
        //Actions
        NUM_TYPES = numTypes;
        PRECISION = precision;
        MAX_QUANTITY = maxQuantity;
        //State change
        state = States.Receive;
    }

    function updateOffer (  uint64 ID, uint64 resourceType, uint64 quantity, uint64 value) public
     {
        require(state == States.Receive);
       //Guards
        require(ID < offers.length && !offers[ID].posted && resourceType < NUM_TYPES && quantity > 0 && quantity <= MAX_QUANTITY);
        //State change
        state = States.InTransition;
        //Actions
        offers[ID].quantity[resourceType] = quantity;
        offers[ID].value[resourceType] = value;

        emit OfferUpdated(ID, resourceType, quantity, value);

        //State change
        state = States.Receive;
    }

}
