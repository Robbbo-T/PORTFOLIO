require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.19",
    settings: {
      optimizer: { enabled: true, runs: 200 }
    }
  },
  networks: {
    hardhat: {},
    localhost: { url: "http://127.0.0.1:8545" },
    // Example testnet (set env vars to use)
    // WARNING: Storing private keys in environment variables (DEPLOYER_KEY) can expose them to risk.
    // Consider using a secure key management system (such as HashiCorp Vault, AWS Secrets Manager, etc.)
    // or ensure environment variables are handled securely and never committed to source control.
    // See Hardhat documentation for best practices: https://hardhat.org/hardhat-runner/docs/guides/deploying#using-private-keys
    sepolia: {
      url: process.env.SEPOLIA_RPC || "",
      accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : []
    }
  },
  paths: {
    sources: "contracts",
    tests: "test",
    cache: "cache",
    artifacts: "artifacts"
  }
};
