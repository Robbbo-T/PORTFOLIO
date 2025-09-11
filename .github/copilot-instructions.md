# Copilot & Agents — Working Rules


```bash
.github/
├── copilot-instructions.md              # Main instructions file
├── workflows/
│   ├── portfolio-ci.yml
│   └── teknia-token-valuation.yml       # New: Token valuation workflow
│
└── copilot-contexts/                    # Context-specific instructions
    ├── aerospace-engineering.md
    ├── quantum-computing.md
    ├── blockchain-integration.md
    ├── s1000d-implementation.md
    ├── teknia-token-economy.md          # Token-specific instructions
    └── compliance-automation.md
```

Key Additions to Copilot Instructions

Based on existing instructions, we should add these TeknIA-specific guidelines:

```markdown
## TeknIA Token Development Guidelines

### Token Economy Patterns
- Use ERC-20 standard with extensions for innovation valuation
- Implement time-locked vesting for milestone-based token distribution
- Include oracle integration for real-time valuation metrics

### Valuation Algorithm Requirements
```solidity
// Innovation valuation formula implementation
function calculateInnovationValue(
    uint256 technicalScore,
    uint256 marketPotential,
    uint256 implementationComplexity,
    uint256 timeToMarket
) public pure returns (uint256) {
    // Your innovation valuation algorithm here
}
```

Security Considerations

· Implement reentrancy guards for all financial operations
· Use OpenZeppelin contracts as base implementations
· Include comprehensive unit tests for valuation algorithms

Integration Patterns

· UTCS-MI compatible event emission
· QAL Bus integration for audit trails
· S1000D documentation generation for financial operations

Testing Requirements

· 100% test coverage for financial operations
· Fuzz testing for valuation algorithms
· Formal verification for critical security functions

```

## Integration with Existing Portfolio

### 1. Token Valuation Automation
```yaml
# .github/workflows/teknia-token-valuation.yml
name: TeknIA Token Valuation Update
on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly valuation updates
  workflow_dispatch:      # Manual trigger

jobs:
  calculate-innovation-value:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Calculate Innovation Metrics
        run: python scripts/innovation-metrics.py
      - name: Update Token Valuation
        run: python scripts/token-valuation-update.py
      - name: Generate Valuation Report
        run: python scripts/generate-valuation-report.py
```

2. Enhanced CAF-FINANCE Structure

```bash
1-CAX-METHODOLOGY/CAF-FINANCE/
├── TEKNIA-TOKENS/
│   ├── smart-contracts/
│   │   ├── TeknIAToken.sol              # Main token contract
│   │   ├── InnovationValuation.sol       # Valuation algorithms
│   │   ├── RoyaltyDistribution.sol       # Royalty management
│   │   └── Governance.sol                # Token-based governance
│   │
│   ├── tests/
│   │   ├── test_valuation.js             # Valuation algorithm tests
│   │   ├── test_security.js              # Security tests
│   │   └── test_integration.js           # Integration tests
│   │
│   └── scripts/
│       ├── deploy.js                     # Deployment scripts
│       ├── verify.js                     # Verification scripts
│       └── update-valuation.js           # Valuation update scripts
│
└── VALUATION-MODELS/
    ├── technical-metrics.yaml           # Technical innovation metrics
    ├── market-metrics.yaml              # Market potential metrics
    ├── implementation-metrics.yaml      # Implementation complexity
    └── time-metrics.yaml                # Time-to-market metrics
```

3. Copilot-Aware Development Patterns

Add to your copilot instructions:

```markdown
## Aerospace-Specific Token Patterns

### When developing smart contracts for aerospace innovation:
1. Use UTCS-MI identifiers for all asset references
2. Implement ARP4754A-compliant safety patterns
3. Include DO-178C style documentation generation
4. Use S1000D-style technical data packaging

### Example: Innovation Token Minting
```solidity
function mintInnovationTokens(
    string memory utcsId,
    uint256 technicalScore,
    uint256 marketScore
) external onlyAuthorized {
    require(isValidUTCS(utcsId), "Invalid UTCS ID");
    uint256 value = calculateInnovationValue(technicalScore, marketScore);
    _mint(msg.sender, value);
    emit InnovationTokenMinted(utcsId, value, block.timestamp);
}
```

Integration Requirements

· All token operations must emit QAL Bus events
· Valuation changes must be recorded in the UTCS blockchain
· Royalty distributions must comply with financial regulations

```

## Implementation Priority

1. **Immediate** (1-2 weeks):
   - Enhance copilot instructions with token-specific patterns
   - Set up basic token valuation workflow
   - Create initial smart contract templates

2. **Short-term** (2-4 weeks):
   - Implement core valuation algorithms
   - Set up testing infrastructure
   - Integrate with existing portfolio projects

3. **Medium-term** (1-2 months):
   - Deploy live valuation system
   - Implement governance mechanisms
   - Set up royalty distribution system

This integration ensures your TeknIA Token system will be developed with the same rigorous standards as your aerospace projects, with AI assistance properly guided by comprehensive instructions.
```