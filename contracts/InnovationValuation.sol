// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

/// @title InnovationValuation - TeknIA Token Innovation Valuation Engine
/// @notice Implements innovation valuation algorithms for aerospace technology assessment
/// @dev Calculates innovation value based on technical merit, market potential, and implementation complexity
contract InnovationValuation is AccessControl, ReentrancyGuard {
    using SafeMath for uint256;

    // Roles
    bytes32 public constant ASSESSOR_ROLE = keccak256("ASSESSOR_ROLE");
    bytes32 public constant ORACLE_ROLE = keccak256("ORACLE_ROLE");
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");

    // Innovation metrics structure
    struct InnovationMetrics {
        uint256 technicalScore;           // 0-1000: Technical innovation score
        uint256 marketPotential;          // 0-1000: Market size and opportunity
        uint256 implementationComplexity; // 0-1000: Implementation difficulty (inverse)
        uint256 timeToMarket;             // Months to market readiness
        uint256 ipStrength;               // 0-1000: Intellectual property strength
        uint256 teamCapability;           // 0-1000: Team expertise and track record
        uint256 competitiveAdvantage;     // 0-1000: Competitive moat strength
        uint256 riskFactor;               // 0-1000: Overall risk assessment
    }

    // Valuation parameters
    struct ValuationParameters {
        uint256 technicalWeight;          // Weight for technical score (basis points)
        uint256 marketWeight;             // Weight for market potential (basis points)
        uint256 complexityWeight;         // Weight for implementation complexity (basis points)
        uint256 timeWeight;               // Weight for time to market (basis points)
        uint256 ipWeight;                 // Weight for IP strength (basis points)
        uint256 teamWeight;               // Weight for team capability (basis points)
        uint256 competitiveWeight;        // Weight for competitive advantage (basis points)
        uint256 riskWeight;               // Weight for risk factor (basis points)
        uint256 maxTimeToMarket;          // Maximum reasonable time to market (months)
        uint256 baseValuation;            // Base valuation amount
        uint256 scalingFactor;            // Scaling factor for final calculation
    }

    // Innovation assessment record
    struct InnovationAssessment {
        string utcsId;                    // UTCS identifier for the innovation
        InnovationMetrics metrics;        // Innovation metrics
        uint256 calculatedValue;          // Calculated innovation value
        uint256 timestamp;                // Assessment timestamp
        address assessor;                 // Assessor address
        bool validated;                   // Whether assessment is validated
        address validator;                // Validator address
        string metadata;                  // Additional metadata (IPFS hash, etc.)
    }

    // State variables
    ValuationParameters public parameters;
    mapping(string => InnovationAssessment) public assessments;
    mapping(string => bool) public exists;
    string[] public innovationIds;
    mapping(address => string[]) public assessorInnovations;

    // Market data from oracles
    mapping(string => uint256) public marketSizeData;      // Market size by sector
    mapping(string => uint256) public competitorData;      // Competitor analysis data
    mapping(string => uint256) public technologyTrends;    // Technology trend indicators

    // Events
    event InnovationAssessed(
        string indexed utcsId,
        uint256 calculatedValue,
        address indexed assessor,
        uint256 timestamp
    );

    event AssessmentValidated(
        string indexed utcsId,
        address indexed validator,
        uint256 timestamp
    );

    event ParametersUpdated(
        uint256 technicalWeight,
        uint256 marketWeight,
        uint256 baseValuation
    );

    event MarketDataUpdated(
        string indexed sector,
        uint256 marketSize,
        address indexed oracle
    );

    // Errors
    error InvalidUTCSId(string utcsId);
    error AssessmentExists(string utcsId);
    error AssessmentNotFound(string utcsId);
    error InvalidMetrics(string reason);
    error InvalidParameters(string reason);
    error UnauthorizedOracle(address oracle);

    constructor(address initialAdmin, ValuationParameters memory initialParams) {
        _grantRole(DEFAULT_ADMIN_ROLE, initialAdmin);
        _grantRole(GOVERNANCE_ROLE, initialAdmin);
        _grantRole(ASSESSOR_ROLE, initialAdmin);
        
        // Validate initial parameters
        _validateParameters(initialParams);
        parameters = initialParams;
        
        emit ParametersUpdated(
            initialParams.technicalWeight,
            initialParams.marketWeight,
            initialParams.baseValuation
        );
    }

    /// @notice Calculate innovation value using proprietary algorithm
    /// @param metrics Innovation metrics to evaluate
    /// @return value Calculated innovation value in TEK tokens
    function calculateInnovationValue(InnovationMetrics memory metrics)
        public view returns (uint256 value) {
        
        // Validate metrics
        _validateMetrics(metrics);
        
        // Core innovation score (weighted average of key metrics)
        uint256 coreScore = _calculateCoreScore(metrics);
        
        // Apply time to market adjustment
        uint256 timeAdjustment = _calculateTimeAdjustment(metrics.timeToMarket);
        
        // Apply risk adjustment
        uint256 riskAdjustment = _calculateRiskAdjustment(metrics.riskFactor);
        
        // Calculate base value
        uint256 baseValue = parameters.baseValuation
            .mul(coreScore)
            .div(10000); // Convert from basis points
        
        // Apply adjustments
        value = baseValue
            .mul(timeAdjustment)
            .mul(riskAdjustment)
            .div(10000)  // Time adjustment
            .div(10000); // Risk adjustment
        
        // Apply scaling factor
        value = value.mul(parameters.scalingFactor).div(10000);
        
        return value;
    }

    /// @notice Submit innovation assessment
    /// @param utcsId UTCS identifier for the innovation
    /// @param metrics Innovation metrics
    /// @param metadata Additional metadata (IPFS hash, etc.)
    function assessInnovation(
        string calldata utcsId,
        InnovationMetrics calldata metrics,
        string calldata metadata
    ) external onlyRole(ASSESSOR_ROLE) nonReentrant {
        if (bytes(utcsId).length == 0) revert InvalidUTCSId(utcsId);
        if (exists[utcsId]) revert AssessmentExists(utcsId);
        
        // Calculate innovation value
        uint256 calculatedValue = calculateInnovationValue(metrics);
        
        // Create assessment record
        InnovationAssessment memory assessment = InnovationAssessment({
            utcsId: utcsId,
            metrics: metrics,
            calculatedValue: calculatedValue,
            timestamp: block.timestamp,
            assessor: msg.sender,
            validated: false,
            validator: address(0),
            metadata: metadata
        });
        
        // Store assessment
        assessments[utcsId] = assessment;
        exists[utcsId] = true;
        innovationIds.push(utcsId);
        assessorInnovations[msg.sender].push(utcsId);
        
        emit InnovationAssessed(utcsId, calculatedValue, msg.sender, block.timestamp);
    }

    /// @notice Validate an innovation assessment
    /// @param utcsId UTCS identifier to validate
    function validateAssessment(string calldata utcsId) 
        external onlyRole(ASSESSOR_ROLE) {
        if (!exists[utcsId]) revert AssessmentNotFound(utcsId);
        
        InnovationAssessment storage assessment = assessments[utcsId];
        require(assessment.assessor != msg.sender, "Cannot validate own assessment");
        
        assessment.validated = true;
        assessment.validator = msg.sender;
        
        emit AssessmentValidated(utcsId, msg.sender, block.timestamp);
    }

    /// @notice Batch assess multiple innovations
    /// @param utcsIds Array of UTCS identifiers
    /// @param metricsArray Array of innovation metrics
    /// @param metadataArray Array of metadata strings
    function batchAssess(
        string[] calldata utcsIds,
        InnovationMetrics[] calldata metricsArray,
        string[] calldata metadataArray
    ) external onlyRole(ASSESSOR_ROLE) nonReentrant {
        require(
            utcsIds.length == metricsArray.length &&
            utcsIds.length == metadataArray.length,
            "Array length mismatch"
        );
        
        for (uint256 i = 0; i < utcsIds.length; i++) {
            string calldata utcsId = utcsIds[i];
            
            if (bytes(utcsId).length == 0 || exists[utcsId]) {
                continue; // Skip invalid or existing
            }
            
            uint256 calculatedValue = calculateInnovationValue(metricsArray[i]);
            
            InnovationAssessment memory assessment = InnovationAssessment({
                utcsId: utcsId,
                metrics: metricsArray[i],
                calculatedValue: calculatedValue,
                timestamp: block.timestamp,
                assessor: msg.sender,
                validated: false,
                validator: address(0),
                metadata: metadataArray[i]
            });
            
            assessments[utcsId] = assessment;
            exists[utcsId] = true;
            innovationIds.push(utcsId);
            assessorInnovations[msg.sender].push(utcsId);
            
            emit InnovationAssessed(utcsId, calculatedValue, msg.sender, block.timestamp);
        }
    }

    /// @notice Update market data (oracle only)
    /// @param sector Market sector identifier
    /// @param marketSize Market size data
    function updateMarketData(string calldata sector, uint256 marketSize)
        external onlyRole(ORACLE_ROLE) {
        marketSizeData[sector] = marketSize;
        emit MarketDataUpdated(sector, marketSize, msg.sender);
    }

    /// @notice Get innovation assessment
    /// @param utcsId UTCS identifier
    /// @return assessment The innovation assessment
    function getAssessment(string calldata utcsId)
        external view returns (InnovationAssessment memory assessment) {
        if (!exists[utcsId]) revert AssessmentNotFound(utcsId);
        return assessments[utcsId];
    }

    /// @notice Get assessments by assessor
    /// @param assessor Assessor address
    /// @return utcsIds Array of UTCS IDs assessed by the address
    function getAssessmentsByAssessor(address assessor)
        external view returns (string[] memory utcsIds) {
        return assessorInnovations[assessor];
    }

    /// @notice Get total number of assessments
    /// @return count Total assessment count
    function getTotalAssessments() external view returns (uint256 count) {
        return innovationIds.length;
    }

    /// @notice Update valuation parameters (governance only)
    /// @param newParams New valuation parameters
    function updateParameters(ValuationParameters calldata newParams)
        external onlyRole(GOVERNANCE_ROLE) {
        _validateParameters(newParams);
        parameters = newParams;
        
        emit ParametersUpdated(
            newParams.technicalWeight,
            newParams.marketWeight,
            newParams.baseValuation
        );
    }

    /// @notice Add oracle (governance only)
    /// @param oracle Address to grant oracle role
    function addOracle(address oracle) external onlyRole(GOVERNANCE_ROLE) {
        _grantRole(ORACLE_ROLE, oracle);
    }

    /// @notice Remove oracle (governance only)
    /// @param oracle Address to revoke oracle role
    function removeOracle(address oracle) external onlyRole(GOVERNANCE_ROLE) {
        _revokeRole(ORACLE_ROLE, oracle);
    }

    /// @notice Calculate core innovation score
    /// @param metrics Innovation metrics
    /// @return score Weighted core score
    function _calculateCoreScore(InnovationMetrics memory metrics)
        internal view returns (uint256 score) {
        
        score = metrics.technicalScore.mul(parameters.technicalWeight)
            .add(metrics.marketPotential.mul(parameters.marketWeight))
            .add(metrics.implementationComplexity.mul(parameters.complexityWeight))
            .add(metrics.ipStrength.mul(parameters.ipWeight))
            .add(metrics.teamCapability.mul(parameters.teamWeight))
            .add(metrics.competitiveAdvantage.mul(parameters.competitiveWeight));
        
        // Total weight should equal 10000 (100%)
        return score.div(10000);
    }

    /// @notice Calculate time to market adjustment
    /// @param timeToMarket Time to market in months
    /// @return adjustment Time adjustment factor (basis points)
    function _calculateTimeAdjustment(uint256 timeToMarket)
        internal view returns (uint256 adjustment) {
        
        if (timeToMarket == 0) return 10000; // Immediate market entry
        if (timeToMarket >= parameters.maxTimeToMarket) return 5000; // Max penalty
        
        // Linear decay from 10000 to 5000 over maxTimeToMarket months
        uint256 decay = timeToMarket.mul(5000).div(parameters.maxTimeToMarket);
        return uint256(10000).sub(decay);
    }

    /// @notice Calculate risk adjustment factor
    /// @param riskFactor Risk factor (0-1000)
    /// @return adjustment Risk adjustment factor (basis points)
    function _calculateRiskAdjustment(uint256 riskFactor)
        internal pure returns (uint256 adjustment) {
        
        // Higher risk = lower adjustment
        // Risk 0 = 10000 (no discount)
        // Risk 1000 = 5000 (50% discount)
        if (riskFactor >= 1000) return 5000;
        
        uint256 discount = riskFactor.mul(5000).div(1000);
        return uint256(10000).sub(discount);
    }

    /// @notice Validate innovation metrics
    /// @param metrics Metrics to validate
    function _validateMetrics(InnovationMetrics memory metrics) internal pure {
        if (metrics.technicalScore > 1000) revert InvalidMetrics("Technical score > 1000");
        if (metrics.marketPotential > 1000) revert InvalidMetrics("Market potential > 1000");
        if (metrics.implementationComplexity > 1000) revert InvalidMetrics("Implementation complexity > 1000");
        if (metrics.ipStrength > 1000) revert InvalidMetrics("IP strength > 1000");
        if (metrics.teamCapability > 1000) revert InvalidMetrics("Team capability > 1000");
        if (metrics.competitiveAdvantage > 1000) revert InvalidMetrics("Competitive advantage > 1000");
        if (metrics.riskFactor > 1000) revert InvalidMetrics("Risk factor > 1000");
    }

    /// @notice Validate valuation parameters
    /// @param params Parameters to validate
    function _validateParameters(ValuationParameters memory params) internal pure {
        uint256 totalWeight = params.technicalWeight
            .add(params.marketWeight)
            .add(params.complexityWeight)
            .add(params.ipWeight)
            .add(params.teamWeight)
            .add(params.competitiveWeight);
        
        if (totalWeight != 10000) revert InvalidParameters("Weights must sum to 10000");
        if (params.maxTimeToMarket == 0) revert InvalidParameters("Max time to market cannot be 0");
        if (params.baseValuation == 0) revert InvalidParameters("Base valuation cannot be 0");
        if (params.scalingFactor == 0) revert InvalidParameters("Scaling factor cannot be 0");
    }
}