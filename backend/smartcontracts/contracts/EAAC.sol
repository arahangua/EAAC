// SPDX-License-Identifier: MIT
pragma solidity 0.8.20;
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";

contract EAAC is Initializable, OwnableUpgradeable {
    
    function initialize() public initializer {
        __Ownable_init(msg.sender);  // This initializes the owner to msg.sender
    }

    event Register(address indexed operator, string identifier);
    event Report(address indexed operator, string identifier, string report_hash);

    // Function to register an agent with a specific identifier
    function register_agent(address operator, string calldata identifier) public {
        emit Register(operator, identifier);        
    }

    // Overloaded function to register an agent with a generic identifier
    function register_agent_generic(address operator) public {
        emit Register(operator, "generic");
    }

    // Function to report an activity with a specific identifier and report hash
    function report_activity(address operator, string calldata identifier, string calldata report_hash) public {
        emit Report(operator, identifier, report_hash);
    }

    // Overloaded function to report an activity with a generic identifier
    function report_activity_generic(address operator, string calldata report_hash) public {
        emit Report(operator, "generic", report_hash);
    }
}
