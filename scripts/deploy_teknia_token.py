#!/usr/bin/env python3
"""
Deploy TekniaToken using web3.py and the Hardhat artifact.
Requirements:
  pip install web3 eth-account python-dotenv
Workflow:
  1) npx hardhat compile
  2) export WEB3_PROVIDER_URI="http://127.0.0.1:8545" (or Infura/Alchemy RPC)
     export DEPLOYER_KEY="0x..." (private key)
  3) python scripts/deploy_teknia_token.py --artifact artifacts/contracts/TekniaToken.sol/TekniaToken.json --initial-supply 1000000000
"""
import json
import argparse
import os
from pathlib import Path
from web3 import Web3
from eth_account import Account
from dotenv import load_dotenv

load_dotenv()

DEFAULT_ARTIFACT = "artifacts/contracts/TekniaToken.sol/TekniaToken.json"
DEPLOYMENTS_DIR = Path("deployments")
DEPLOYMENTS_DIR.mkdir(exist_ok=True)

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--artifact", default=os.environ.get("TEK_ARTIFACT", DEFAULT_ARTIFACT),
                   help="Path to Hardhat artifact JSON (ABI + bytecode)")
    p.add_argument("--initial-supply", type=int, default=1_000_000_000,
                   help="Token supply in TEK units (will be multiplied by 10**decimals)")
    p.add_argument("--decimals", type=int, default=18, help="Token decimals")
    p.add_argument("--provider", default=os.environ.get("WEB3_PROVIDER_URI", "http://127.0.0.1:8545"),
                   help="RPC endpoint")
    p.add_argument("--key", default=os.environ.get("DEPLOYER_KEY"), help="Deployer private key (hex)")
    return p.parse_args()

def main():
    args = parse_args()
    artifact_path = Path(args.artifact)
    if not artifact_path.exists():
        raise SystemExit(f"Artifact not found. Run `npx hardhat compile` first. Missing: {artifact_path}")

    with artifact_path.open("r", encoding="utf-8") as fh:
        artifact = json.load(fh)

    abi = artifact.get("abi")
    bytecode = artifact.get("bytecode")
    if not abi or not bytecode:
        raise SystemExit("Artifact missing abi/bytecode")

    w3 = Web3(Web3.HTTPProvider(args.provider))
    if not w3.is_connected():
        raise SystemExit(f"Failed to connect to provider: {args.provider}")

    deployer_key = args.key
    if not deployer_key:
        raise SystemExit("Set DEPLOYER_KEY env var or pass --key")

    acct = Account.from_key(deployer_key)
    nonce = w3.eth.get_transaction_count(acct.address)
    chain_id = w3.eth.chain_id

    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    initial_supply_wei = args.initial_supply * (10 ** args.decimals)

    construct_txn = contract.constructor(initial_supply_wei).build_transaction({
        "from": acct.address,
        "nonce": nonce,
        "gas": 5_000_000,
        "gasPrice": w3.eth.gas_price,
        "chainId": chain_id
    })

    signed = acct.sign_transaction(construct_txn)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    print("Deploy tx sent:", tx_hash.hex())
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=600)
    print("Contract deployed at:", receipt.contractAddress)
    out = {
        "address": receipt.contractAddress,
        "txHash": tx_hash.hex(),
        "deployer": acct.address,
        "chainId": chain_id
    }
    fname = DEPLOYMENTS_DIR / f"teknia-{chain_id}.json"
    fname.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("Saved deployment info to", fname)

if __name__ == "__main__":
    main()
