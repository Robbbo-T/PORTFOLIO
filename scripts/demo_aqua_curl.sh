#!/bin/bash
# Demo script showing AQUA API integration via curl

echo "🌊 AQUA API Integration Demo"
echo "=============================="

echo "📤 Sample curl request to validate FE manifest:"
echo ""

# Show the curl command that would be used
cat << 'EOF'
curl -X POST "https://aqua.example.com/api/v1/manifests/validate" \
  -H "Content-Type: application/json" \
  -d '{
        "manifest": {
          "type": "FE",
          "name": "Cross-Domain Federation",
          "version": "1.0.0",
          "members": [
            {"domain": "AAA", "role": "coordinator"},
            {"domain": "CQH", "role": "participant"}
          ],
          "orchestration_rules": {
            "consensus_protocol": "proof-of-authority",
            "quorum_threshold": 0.67,
            "timeout_seconds": 300
          }
        },
        "domain": "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
        "llc_path": "TFA/ELEMENTS/FE"
      }'
EOF

echo ""
echo "📥 Expected JSON Response:"
echo ""

cat << 'EOF'
{
  "valid": true,
  "canonical_hash": "0x1234567890abcdef...",
  "errors": [],
  "metadata": {
    "domain": "AAA-AERODYNAMICS-AND-AIRFRAMES-ARCHITECTURES",
    "llc_path": "TFA/ELEMENTS/FE",
    "manifest_type": "FE",
    "validation_timestamp": "2025-09-20T05:17:43Z"
  }
}
EOF

echo ""
echo "ℹ️ Note: This demo shows the expected API format."
echo "   For actual validation, use: python3 scripts/test_aqua_validation.py"