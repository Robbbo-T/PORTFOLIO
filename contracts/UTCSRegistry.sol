// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/cryptography/ECDSA.sol";

/// @title UTCSRegistry - Universal Traceability and Canonical State Registry
/// @notice Registry for anchoring TFA manifest hashes with provenance and governance
/// @dev Implements access control, fee management, and comprehensive event logging
contract UTCSRegistry is AccessControl, ReentrancyGuard {
    using ECDSA for bytes32;

    // Roles
    bytes32 public constant ANCHOR_ROLE = keccak256("ANCHOR_ROLE");
    bytes32 public constant VALIDATOR_ROLE = keccak256("VALIDATOR_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    
    // Registry configuration
    struct RegistryConfig {
        uint256 anchorFee;           // Fee in wei for anchoring
        uint256 maxAnchorsPerBlock;  // Rate limiting
        bool paused;                 // Emergency pause
        address feeRecipient;        // Fee collection address
    }
    
    // Anchor record structure
    struct AnchorRecord {
        bytes32 canonicalHash;       // Canonical hash of the manifest
        address submitter;           // Address that submitted the anchor
        uint256 blockNumber;         // Block number when anchored
        uint256 timestamp;           // Timestamp of anchoring
        string domain;               // TFA domain (e.g., "AAA")
        string llcPath;              // LLC path (e.g., "TFA/ELEMENTS/FE")
        string manifestType;         // Type of manifest (e.g., "FE")
        bytes metadata;              // Additional metadata (ABI encoded)
        bool validated;              // Whether anchor was validator-approved
        address validator;           // Validator address (if validated)
    }
    
    // State variables
    RegistryConfig public config;
    mapping(bytes32 => AnchorRecord) public anchors;
    mapping(bytes32 => bool) public exists;
    mapping(uint256 => uint256) public anchorsPerBlock;
    
    // Arrays for enumeration
    bytes32[] public anchorHashes;
    mapping(address => bytes32[]) public submitterAnchors;
    
    // Events
    event AnchorRegistered(
        bytes32 indexed canonicalHash,
        address indexed submitter,
        string domain,
        string llcPath,
        string manifestType,
        uint256 blockNumber,
        uint256 timestamp
    );
    
    event AnchorValidated(
        bytes32 indexed canonicalHash,
        address indexed validator,
        uint256 timestamp
    );
    
    event ConfigUpdated(
        uint256 anchorFee,
        uint256 maxAnchorsPerBlock,
        bool paused,
        address feeRecipient
    );
    
    event ValidatorAdded(address indexed validator);
    event ValidatorRemoved(address indexed validator);
    
    // Errors
    error AlreadyAnchored(bytes32 canonicalHash);
    error AnchorNotFound(bytes32 canonicalHash);
    error InsufficientFee(uint256 required, uint256 provided);
    error RateLimitExceeded(uint256 current, uint256 max);
    error RegistryPaused();
    error InvalidSignature();
    error UnauthorizedValidator(address validator);
    
    /// @notice Constructor sets up roles and initial configuration
    /// @param initialAdmin Address to grant DEFAULT_ADMIN_ROLE
    /// @param initialConfig Initial registry configuration
    constructor(address initialAdmin, RegistryConfig memory initialConfig) {
        _grantRole(DEFAULT_ADMIN_ROLE, initialAdmin);
        _grantRole(GOVERNANCE_ROLE, initialAdmin);
        _grantRole(ANCHOR_ROLE, initialAdmin);
        
        config = initialConfig;
        emit ConfigUpdated(
            initialConfig.anchorFee,
            initialConfig.maxAnchorsPerBlock,
            initialConfig.paused,
            initialConfig.feeRecipient
        );
    }
    
    /// @notice Anchor a manifest hash to the registry
    /// @param canonicalHash The canonical hash of the manifest
    /// @param domain TFA domain identifier
    /// @param llcPath LLC path within the domain
    /// @param manifestType Type of manifest being anchored
    /// @param metadata Additional metadata (ABI encoded)
    function anchorManifest(
        bytes32 canonicalHash,
        string calldata domain,
        string calldata llcPath,
        string calldata manifestType,
        bytes calldata metadata
    ) external payable nonReentrant {
        if (config.paused) revert RegistryPaused();
        if (exists[canonicalHash]) revert AlreadyAnchored(canonicalHash);
        if (msg.value < config.anchorFee) revert InsufficientFee(config.anchorFee, msg.value);
        
        // Rate limiting
        uint256 currentBlockAnchors = anchorsPerBlock[block.number];
        if (currentBlockAnchors >= config.maxAnchorsPerBlock) {
            revert RateLimitExceeded(currentBlockAnchors, config.maxAnchorsPerBlock);
        }
        
        // Create anchor record
        AnchorRecord memory record = AnchorRecord({
            canonicalHash: canonicalHash,
            submitter: msg.sender,
            blockNumber: block.number,
            timestamp: block.timestamp,
            domain: domain,
            llcPath: llcPath,
            manifestType: manifestType,
            metadata: metadata,
            validated: false,
            validator: address(0)
        });
        
        // Store anchor
        anchors[canonicalHash] = record;
        exists[canonicalHash] = true;
        anchorHashes.push(canonicalHash);
        submitterAnchors[msg.sender].push(canonicalHash);
        anchorsPerBlock[block.number] = currentBlockAnchors + 1;
        
        // Transfer fee
        if (config.anchorFee > 0) {
            payable(config.feeRecipient).transfer(config.anchorFee);
            
            // Refund excess
            if (msg.value > config.anchorFee) {
                payable(msg.sender).transfer(msg.value - config.anchorFee);
            }
        }
        
        emit AnchorRegistered(
            canonicalHash,
            msg.sender,
            domain,
            llcPath,
            manifestType,
            block.number,
            block.timestamp
        );
    }
    
    /// @notice Validate an anchor (validator only)
    /// @param canonicalHash Hash to validate
    function validateAnchor(bytes32 canonicalHash) external onlyRole(VALIDATOR_ROLE) {
        if (!exists[canonicalHash]) revert AnchorNotFound(canonicalHash);
        
        AnchorRecord storage record = anchors[canonicalHash];
        record.validated = true;
        record.validator = msg.sender;
        
        emit AnchorValidated(canonicalHash, msg.sender, block.timestamp);
    }
    
    /// @notice Batch anchor multiple manifests (anchor role only)
    /// @param hashes Array of canonical hashes
    /// @param domains Array of domain identifiers
    /// @param llcPaths Array of LLC paths
    /// @param manifestTypes Array of manifest types
    /// @param metadataArray Array of metadata
    function batchAnchor(
        bytes32[] calldata hashes,
        string[] calldata domains,
        string[] calldata llcPaths,
        string[] calldata manifestTypes,
        bytes[] calldata metadataArray
    ) external onlyRole(ANCHOR_ROLE) nonReentrant {
        if (config.paused) revert RegistryPaused();
        
        require(
            hashes.length == domains.length &&
            hashes.length == llcPaths.length &&
            hashes.length == manifestTypes.length &&
            hashes.length == metadataArray.length,
            "Array length mismatch"
        );
        
        for (uint256 i = 0; i < hashes.length; i++) {
            bytes32 hash = hashes[i];
            if (exists[hash]) continue; // Skip already anchored
            
            AnchorRecord memory record = AnchorRecord({
                canonicalHash: hash,
                submitter: msg.sender,
                blockNumber: block.number,
                timestamp: block.timestamp,
                domain: domains[i],
                llcPath: llcPaths[i],
                manifestType: manifestTypes[i],
                metadata: metadataArray[i],
                validated: true, // Auto-validated for anchor role
                validator: msg.sender
            });
            
            anchors[hash] = record;
            exists[hash] = true;
            anchorHashes.push(hash);
            submitterAnchors[msg.sender].push(hash);
            
            emit AnchorRegistered(
                hash,
                msg.sender,
                domains[i],
                llcPaths[i],
                manifestTypes[i],
                block.number,
                block.timestamp
            );
            
            emit AnchorValidated(hash, msg.sender, block.timestamp);
        }
    }
    
    /// @notice Get anchor record by hash
    /// @param canonicalHash The canonical hash to lookup
    /// @return record The anchor record
    function getAnchor(bytes32 canonicalHash) external view returns (AnchorRecord memory record) {
        if (!exists[canonicalHash]) revert AnchorNotFound(canonicalHash);
        return anchors[canonicalHash];
    }
    
    /// @notice Get anchors by submitter
    /// @param submitter Address of the submitter
    /// @return hashes Array of canonical hashes submitted by the address
    function getAnchorsBySubmitter(address submitter) external view returns (bytes32[] memory hashes) {
        return submitterAnchors[submitter];
    }
    
    /// @notice Get total number of anchors
    /// @return count Total anchor count
    function getTotalAnchors() external view returns (uint256 count) {
        return anchorHashes.length;
    }
    
    /// @notice Get anchors in range (for pagination)
    /// @param start Start index
    /// @param limit Maximum number of results
    /// @return hashes Array of canonical hashes
    function getAnchorsRange(uint256 start, uint256 limit) 
        external view returns (bytes32[] memory hashes) {
        uint256 total = anchorHashes.length;
        if (start >= total) return new bytes32[](0);
        
        uint256 end = start + limit;
        if (end > total) end = total;
        
        hashes = new bytes32[](end - start);
        for (uint256 i = start; i < end; i++) {
            hashes[i - start] = anchorHashes[i];
        }
        
        return hashes;
    }
    
    /// @notice Update registry configuration (governance only)
    /// @param newConfig New configuration parameters
    function updateConfig(RegistryConfig calldata newConfig) 
        external onlyRole(GOVERNANCE_ROLE) {
        config = newConfig;
        emit ConfigUpdated(
            newConfig.anchorFee,
            newConfig.maxAnchorsPerBlock,
            newConfig.paused,
            newConfig.feeRecipient
        );
    }
    
    /// @notice Add validator (governance only)
    /// @param validator Address to grant validator role
    function addValidator(address validator) external onlyRole(GOVERNANCE_ROLE) {
        _grantRole(VALIDATOR_ROLE, validator);
        emit ValidatorAdded(validator);
    }
    
    /// @notice Remove validator (governance only)
    /// @param validator Address to revoke validator role
    function removeValidator(address validator) external onlyRole(GOVERNANCE_ROLE) {
        _revokeRole(VALIDATOR_ROLE, validator);
        emit ValidatorRemoved(validator);
    }
    
    /// @notice Emergency pause (governance only)
    function pause() external onlyRole(GOVERNANCE_ROLE) {
        config.paused = true;
        emit ConfigUpdated(
            config.anchorFee,
            config.maxAnchorsPerBlock,
            config.paused,
            config.feeRecipient
        );
    }
    
    /// @notice Resume operations (governance only)
    function unpause() external onlyRole(GOVERNANCE_ROLE) {
        config.paused = false;
        emit ConfigUpdated(
            config.anchorFee,
            config.maxAnchorsPerBlock,
            config.paused,
            config.feeRecipient
        );
    }
    
    /// @notice Check if hash exists in registry
    /// @param canonicalHash Hash to check
    /// @return exists Whether the hash is anchored
    function isAnchored(bytes32 canonicalHash) external view returns (bool) {
        return exists[canonicalHash];
    }
    
    /// @notice Get proof of anchor for external verification
    /// @param canonicalHash Hash to get proof for
    /// @return proof Proof data including block number, timestamp, submitter
    function getAnchorProof(bytes32 canonicalHash) 
        external view returns (
            uint256 blockNumber,
            uint256 timestamp,
            address submitter,
            bool validated,
            address validator
        ) {
        if (!exists[canonicalHash]) revert AnchorNotFound(canonicalHash);
        
        AnchorRecord memory record = anchors[canonicalHash];
        return (
            record.blockNumber,
            record.timestamp,
            record.submitter,
            record.validated,
            record.validator
        );
    }
}