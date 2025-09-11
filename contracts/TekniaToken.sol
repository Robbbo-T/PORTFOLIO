// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Snapshot.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/draft-ERC20Permit.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

/// @title TekniaToken (TEK) - ERC20 with snapshot & permit
/// @notice Minimal but useful scaffold for Teknia token development & governance
contract TekniaToken is ERC20, ERC20Snapshot, ERC20Permit, Ownable {
    constructor(uint256 initialSupply) ERC20("Teknia", "TEK") ERC20Permit("Teknia") {
        require(initialSupply > 0, "initialSupply>0");
        _mint(msg.sender, initialSupply);
    }

    /// @notice Take a snapshot (owner only). Snapshot id returned.
    function snapshot() external onlyOwner returns (uint256) {
        return _snapshot();
    }

    // required override for multiple inheritance
    function _beforeTokenTransfer(address from, address to, uint256 amount)
        internal
        override(ERC20, ERC20Snapshot)
    {
        super._beforeTokenTransfer(from, to, amount);
    }
}
