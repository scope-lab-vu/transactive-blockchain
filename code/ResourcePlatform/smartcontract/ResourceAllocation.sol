pragma solidity ^0.4.19;

contract ResourceAllocation {     
    uint64 NUM_TYPES = 1;
    uint64 PRECISION = 4294967296;
    uint64 MAX_QUANTITY = 1;

    function setup(uint64 numTypes, uint64 precision, uint64 maxQuantity) public {
        NUM_TYPES = numTypes;
        PRECISION = precision;
        MAX_QUANTITY = maxQuantity;
    }
       
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
    
    function createOffer(bool providing, uint64 misc, uint64 prosumer) public {
        offers.push(Offer({
            providing: providing,
            prosumer: prosumer,
            posted: false
        }));
        
        emit OfferCreated(uint64(offers.length - 1), providing, misc, prosumer);
    }
    
    function updateOffer(uint64 ID, uint64 resourceType, uint64 quantity, uint64 value) public {
        require(ID < offers.length);
        require(!offers[ID].posted);
        require(resourceType < NUM_TYPES);
        require(quantity > 0);
        require(quantity <= MAX_QUANTITY);
        
        offers[ID].quantity[resourceType] = quantity;
        offers[ID].value[resourceType] = value;
        
        emit OfferUpdated(ID, resourceType, quantity, value);
    }
    
    function postOffer(uint64 ID) public {
        require(ID < offers.length);
        require(!offers[ID].posted);
        
        offers[ID].posted = true;
        
        emit OfferPosted(ID);
    }
    
    function cancelOffer(uint64 ID) public {
        require(ID < offers.length);
        require(offers[ID].posted);
        
        offers[ID].posted = false;
        
        emit OfferCanceled(ID);
    }
    
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
    
    function createSolution(uint64 misc) public {
        solutions.push(Solution({
            numAssignments: 0,
            objective: 0
        }));
        
        emit SolutionCreated(uint64(solutions.length - 1), misc);
    }
    
    function addAssignment(uint64 ID, uint64 providingOfferID, uint64 consumingOfferID, uint64 resourceType, uint64 quantity, uint64 value) public {
        require(ID < solutions.length);
        require(providingOfferID < offers.length);
        require(consumingOfferID < offers.length);
        require(resourceType < NUM_TYPES);
        require(offers[providingOfferID].providing);
        require(offers[providingOfferID].posted);
        require(offers[providingOfferID].quantity[resourceType] > 0);
        require(!offers[consumingOfferID].providing);
        require(offers[consumingOfferID].posted);
        require(offers[consumingOfferID].quantity[resourceType] > 0);
        
        Solution storage solution = solutions[ID];
        solution.allocated[providingOfferID] += (uint256(quantity) * PRECISION) / offers[providingOfferID].quantity[resourceType];
        solution.allocated[consumingOfferID] += (uint256(quantity) * PRECISION) / offers[consumingOfferID].quantity[resourceType];
        require(solution.allocated[providingOfferID] <= PRECISION);
        require(solution.allocated[consumingOfferID] <= PRECISION);
        require(value >= offers[providingOfferID].value[resourceType]);
        require(value <= offers[consumingOfferID].value[resourceType]);
        
        solution.assignments[solution.numAssignments] = Assignment({
            providingOfferID: providingOfferID,
            consumingOfferID: consumingOfferID,
            resourceType: resourceType,
            quantity: quantity,
            value: value
        });
        solution.numAssignments += 1;
        
        solution.objective += quantity;
        if (solution.objective > solutions[bestSolution].objective)
            bestSolution = ID;

        emit AssignmentAdded(ID, providingOfferID, consumingOfferID, resourceType, quantity, value, solution.objective);
    }
    
    function finalize() public {
        require(solutions.length > 0);
        
        Solution storage solution = solutions[bestSolution];
        for (uint64 i = 0; i < solution.numAssignments; i++) {
            Assignment memory assignment = solution.assignments[i];
            emit AssignmentFinalized(assignment.providingOfferID, assignment.consumingOfferID, assignment.resourceType, assignment.quantity, assignment.value);
        }
    }
}

