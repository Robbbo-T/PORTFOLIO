#!/bin/bash
# ASI-T Genesis Docker QS/UTCS Label Helper
# 
# This script adds required QS/UTCS provenance labels to Docker images
# during build time to ensure traceability and evidence anchoring.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVIDENCE_DIR="${SCRIPT_DIR}/../EVIDENCE"

# Default values
POLICY_HASH="${POLICY_HASH:-sha256:c3ab8ff13720e8ad9047dd39466b3c8974e592c2fa383d4a3960714caef0c4f2}"
MODEL_SHA="${MODEL_SHA:-sha256:5d41402abc4b2a76b9719d911017c592ac36e8e3f1a978e9e8ac3b5b8e6c7f23}"
DATA_MANIFEST_HASH="${DATA_MANIFEST_HASH:-sha256:8e6b8b9f0e7f4c5d3b2a1c0e9f8e7d6c5b4a3c2d1e0f9e8d7c6b5a4c3d2e1f00}"
CANONICAL_HASH="${CANONICAL_HASH:-sha256:1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b}"
OPERATOR_ID="${OPERATOR_ID:-UTCS:OP:robbo-t}"

usage() {
    cat << EOF
Usage: $0 [OPTIONS] DOCKER_BUILD_ARGS...

Add Genesis QS/UTCS labels to Docker build commands.

OPTIONS:
    --policy-hash HASH      Policy hash (default: from env or sample)
    --model-sha HASH        Model SHA hash (default: from env or sample)  
    --data-manifest HASH    Data manifest hash (default: from env or sample)
    --canonical-hash HASH   Canonical hash (default: from env or sample)
    --operator-id ID        Operator ID (default: from env or sample)
    --evidence-file FILE    Load hashes from evidence JSON file
    --help                  Show this help

EXAMPLES:
    # Add labels to docker build
    $0 docker build -t myapp:latest .

    # Use specific evidence file
    $0 --evidence-file evidence.json docker build -t myapp:latest .
    
    # Override specific hashes
    $0 --policy-hash sha256:abc123... docker build -t myapp:latest .

EOF
}

load_evidence_file() {
    local evidence_file="$1"
    
    if [[ ! -f "$evidence_file" ]]; then
        echo "❌ Evidence file not found: $evidence_file" >&2
        exit 1
    fi
    
    # Extract hashes from evidence JSON
    POLICY_HASH=$(python3 -c "
import json, sys
with open('$evidence_file') as f:
    data = json.load(f)
    print(data.get('provenance', {}).get('policy_hash', '$POLICY_HASH'))
" 2>/dev/null || echo "$POLICY_HASH")

    MODEL_SHA=$(python3 -c "
import json, sys
with open('$evidence_file') as f:
    data = json.load(f)
    print(data.get('provenance', {}).get('model_sha', '$MODEL_SHA'))
" 2>/dev/null || echo "$MODEL_SHA")

    DATA_MANIFEST_HASH=$(python3 -c "
import json, sys
with open('$evidence_file') as f:
    data = json.load(f)
    print(data.get('provenance', {}).get('data_manifest_hash', '$DATA_MANIFEST_HASH'))
" 2>/dev/null || echo "$DATA_MANIFEST_HASH")

    CANONICAL_HASH=$(python3 -c "
import json, sys
with open('$evidence_file') as f:
    data = json.load(f)
    print(data.get('provenance', {}).get('canonical_hash', '$CANONICAL_HASH'))
" 2>/dev/null || echo "$CANONICAL_HASH")

    OPERATOR_ID=$(python3 -c "
import json, sys
with open('$evidence_file') as f:
    data = json.load(f)
    print(data.get('provenance', {}).get('operator_id', '$OPERATOR_ID'))
" 2>/dev/null || echo "$OPERATOR_ID")

    echo "📋 Loaded evidence from: $evidence_file"
}

generate_labels() {
    local timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    
    cat << EOF
--label asit.qs.policy_hash="${POLICY_HASH}" \\
--label asit.qs.model_sha="${MODEL_SHA}" \\
--label asit.qs.data_manifest_hash="${DATA_MANIFEST_HASH}" \\
--label asit.qs.canonical_hash="${CANONICAL_HASH}" \\
--label asit.utcs.operator_id="${OPERATOR_ID}" \\
--label asit.utcs.build_timestamp="${timestamp}" \\
--label asit.genesis.version="1.0.0"
EOF
}

main() {
    local docker_args=()
    
    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --policy-hash)
                POLICY_HASH="$2"
                shift 2
                ;;
            --model-sha)
                MODEL_SHA="$2"
                shift 2
                ;;
            --data-manifest)
                DATA_MANIFEST_HASH="$2"
                shift 2
                ;;
            --canonical-hash)
                CANONICAL_HASH="$2"
                shift 2
                ;;
            --operator-id)
                OPERATOR_ID="$2"
                shift 2
                ;;
            --evidence-file)
                load_evidence_file "$2"
                shift 2
                ;;
            --help)
                usage
                exit 0
                ;;
            docker)
                docker_args=("$@")
                break
                ;;
            *)
                echo "❌ Unknown option: $1" >&2
                usage >&2
                exit 1
                ;;
        esac
    done
    
    if [[ ${#docker_args[@]} -eq 0 ]]; then
        echo "❌ No docker command provided" >&2
        usage >&2
        exit 1
    fi
    
    # Check if first arg is docker build
    if [[ "${docker_args[1]:-}" == "build" ]]; then
        echo "🏷️  Adding Genesis QS/UTCS labels to Docker build..."
        
        # Insert labels after 'docker build'
        local enhanced_cmd=(
            "${docker_args[0]}"  # docker
            "${docker_args[1]}"  # build
        )
        
        # Add our labels
        while IFS= read -r label; do
            [[ -n "$label" ]] && enhanced_cmd+=("$label")
        done < <(generate_labels)
        
        # Add remaining arguments
        enhanced_cmd+=("${docker_args[@]:2}")
        
        echo "🚀 Executing: ${enhanced_cmd[*]}"
        exec "${enhanced_cmd[@]}"
    else
        echo "ℹ️  Not a docker build command, passing through..."
        exec "${docker_args[@]}"
    fi
}

# Auto-detect evidence file if available
if [[ -f "$EVIDENCE_DIR/sample.qs.json" ]] && [[ "${1:-}" != "--evidence-file" ]]; then
    load_evidence_file "$EVIDENCE_DIR/sample.qs.json"
fi

main "$@"