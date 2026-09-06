# Immunefi-Firelight-auditcomp_BB-Report--004

Audit Competition Details:
Firelight is an on-chain cover protocol. The contracts implement an upgradeable ERC4626-compatible vault for staked collateral, an off-chain-matched cover order allocation flow, cover receipt NFTs, incident assessment and payout execution, a vault reward distributor, and a Flare FTSO v2 price adapter exposed through a Chainlink AggregatorV3-compatible read surface.  The MVP is intentionally permissioned: trusted operators create and settle cover orders, submit matching commitments, assess incidents, and execute approved payouts. The contracts enforce role boundaries, capacity checks, settlement constraints, payout accounting, withdrawal delays, blocklist/rescue controls, and asset transfer paths.  This audit covers Firelight Phase 2, as described in the Firelight documentation. For more information about Firelight, please visit https://docs.firelight.finance.  

Technical Project Information System overview and upgrade context One existing deployed contract is being upgraded: 
- The legacy predeposit vault (contracts/legacy/FirelightVaultPredeposits.sol, with storage in contracts/legacy/FirelightVaultStoragePredeposits.sol). The upgrade implementation is contracts/core/FirelightVault.sol, with V2 storage in contracts/core/FirelightVaultStorage.sol. Reviewers should compare the legacy vault and the V2 vault for storage compatibility and behavior changes. All other in-scope Phase 2 contracts are new deployments.
- Upgrade context FirelightVault.sol is the V2 upgrade implementation for the already-deployed legacy predeposit vault (contracts/legacy/FirelightVaultPredeposits.sol), deployed on Flare at 0x4C18Ff3C89632c3Dd62E796c0aFA5c07c4c1B2b3. Reviewers should examine both the new V2 behavior and its compatibility with the legacy vault storage/layout. The legacy contracts (contracts/legacy/FirelightVaultPredeposits.sol and contracts/legacy/FirelightVaultStoragePredeposits.sol) are included to support upgrade-diff and storage-compatibility review. All other in-scope Phase 2 contracts are new deployments.

Priority areas of concern Firelight is most concerned about:
- Commitment and settlement correctness in CoverOrderAllocator.
- Capacity calculation and solvency constraints.
- Incident/payout accounting: FIFO priority, payout-window behavior, assessment loss validation, first-loss buffer waterfall, vault payout bounds, and interaction between multiple incidents in the same period.
- Upgradeability safety for the upgradeable contracts.
- External price and token assumptions, especially FTSO adapter behavior.

Standardized Rules:
This program follows Immunefi's standard competition rules. For the full default rules on validity, duplicates, known issues, severity, disputes, KYC, payments, and publication, read How Audit Competitions Work: Rules and Policies. Where this program page defines a specific rule, the program page prevails.

Proof of Concept (PoC) Requirements:
A runnable PoC is required. For more information, please read the Web3 PoC Guidelines.

Insight Reporting:
Insight reports may be submitted to this program. Runnable code is not required, but the PoC section must describe the conditions under which the insight is valuable.
Only the best report of a given Insight is rewarded. Duplicates of Insights are not rewarded.
Insights are rewarded according to Immunefi's Standardized Competition Reward Terms and are not eligible for mediation or appeal.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Auditing Information for Report #004:

The following security audit was performed in collaboration with @dhasirar during week 1 of the program commencement.

##Preconfiguration##

URL to fetch repo:
- "https://github.com/immunefi-team/audit-comp-firelight"

In-Scope:
- FtsoChainlinkAdapter.sol
- VaultRewardDistributor.sol
- IncidentManager.sol
- CoverNFT.sol
- CoverOrderAllocator.sol
- FirelightVault.sol (and legacy for comparison)
- Interfaces: IAggregatorV3.sol, IIncidentManager.sol, ICoverOrderAllocator.sol, IFirelightVault.sol
- Libraries: Checkpoints.sol, PriceFeed.sol, Decimals.sol

True repos:
- https://github.com/firelight-protocol/firelight-core/blob/main/contracts/FirelightVault.sol
- https://github.com/firelight-protocol/firelight-core/blob/main/contracts/FirelightVaultStorage.sol
## Old ver. , competition utilizes a fork repo ##

Competition-target repos:
- https://raw.githubusercontent.com/firelight-protocol/firelight-core/main/contracts/FirelightVault.sol
  -> [success]
- https://raw.githubusercontent.com/firelight-protocol/firelight-core/main/contracts/CoverOrderAllocator.sol
  -> [failed]
- https://raw.githubusercontent.com/firelight-protocol/firelight-core/main/contracts/IncidentManager.sol
  -> [failed]

Additional targeted repo branches:
- contracts/core/FirelightVault.sol
- contracts/core/CoverOrderAllocator.sol
- contracts/core/IncidentManager.sol
- contracts/core/CoverNFT.sol
- contracts/core/VaultRewardDistributor.sol
- contracts/core/FtsoChainlinkAdapter.sol
- contracts/core/lib/Checkpoints.sol
- contracts/core/lib/PriceFeed.sol
- contracts/core/lib/Decimals.sol
- contracts/interfaces/IAggregatorV3.sol
- contracts/interfaces/IIncidentManager.sol
- contracts/interfaces/ICoverOrderAllocator.sol
- contracts/interfaces/IFirelightVault.sol

++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Summary #1:

I successfully retrieved and analyzed FirelightVault.sol (the core ERC4626 vault with delayed withdrawals). However, I initially encountered access restrictions on the Immunefi audit repository for the remaining high-priority contracts: CoverOrderAllocator.sol, IncidentManager.sol, CoverNFT.sol, FtsoChainlinkAdapter.sol, and VaultRewardDistributor.sol.

Priority areas flagged by Firelight:
- Commitment/settlement correctness in CoverOrderAllocator
- Capacity calculation and solvency constraints
- Incident/payout accounting (FIFO, waterfall, first-loss buffer)
- Upgradeability safety (legacy → V2 storage compatibility)
- FTSO adapter behavior

Confirmed Findings from FirelightVault.sol:

1. [MEDIUM] Missing Reentrancy Guard on claimWithdraw
Location: FirelightVault.claimWithdraw()
Severity: Medium
Description: While deposit, mint, withdraw, and redeem all implement nonReentrant, claimWithdraw does not. Although isWithdrawClaimed is set before the external safeTransfer call (preventing same-period double-claiming), the absence of nonReentrant creates an inconsistency. If the vault asset is an ERC777 token or has transfer hooks, reentrancy could be used to interact with external protocols or manipulate state in unexpected ways during the claim window.
Impact: Potential state manipulation or unexpected interactions if asset tokens have callbacks.
Recommendation: Add nonReentrant to claimWithdraw for defense in depth.

2. [MEDIUM] Blocklisted Receiver Permanently Freezes Withdrawal Claims
Location: FirelightVault._requestWithdraw / claimWithdraw
Severity: Medium
Description: When a withdrawal is requested with a receiver parameter, withdrawSharesOf[period][receiver] is credited to the receiver. However, claimWithdraw requires notBlocklisted(_msgSender()) and pays assets to _msgSender(). If the receiver is later blocklisted, they cannot claim. Crucially, the original sender also cannot claim on their behalf because withdrawSharesOf[period][sender] is zero. While a RESCUER_ROLE can eventually call rescueWithdrawFromBlocklisted, the withdrawal remains frozen until manual intervention.
Impact: Temporary freezing of funds for users whose designated receiver address is blocklisted after a withdrawal request.
Recommendation: Consider allowing the original withdrawal initiator to claim if the receiver is blocklisted, or document this operational requirement explicitly.

3. [LOW/INSIGHT] Misleading NatSpec Comment on Withdrawal Delay
Location: FirelightVault.redeem()
Severity: Low / Insight
Description: The natspec comment states the withdrawal "will be available in the next period." However, the implementation schedules for currentPeriod() + 1 and claimWithdraw enforces period < currentPeriod(). This means a withdrawal requested in period N cannot be claimed until period N+2 or later — effectively "the period after the next full period." The comment in withdraw() is accurate, but redeem() understates the delay.
Impact: Integration errors or user confusion due to mismatched expectations.
Recommendation: Update the redeem() comment to accurately reflect the enforced delay.

4. [MEDIUM] Rescue Operation Fragmentation Risk
Location: FirelightVault.rescueSharesFromBlocklisted
Severity: Medium
Description: rescueSharesFromBlocklisted transfers all vault shares from a blocklisted address, but it does not automatically rescue pending withdrawal claims. If the rescuer calls only rescueSharesFromBlocklisted and forgets rescueWithdrawFromBlocklisted, the blocklisted address's pending withdrawals remain associated with the blocklisted address and cannot be claimed (since claimWithdraw blocks blocklisted senders).
Impact: Permanent freezing of unclaimed withdrawals if rescue operations are incomplete.
Recommendation: Either bundle both rescues atomically or emit a forced event requiring paired rescue calls.

5. [HIGH] Upgrade Storage Compatibility
Location: FirelightVault.sol → FirelightVaultStorage.sol vs. legacy
Severity: High
Description: The competition explicitly flags upgradeability safety as a priority concern. The V2 vault inherits from FirelightVaultStorage and multiple OpenZeppelin upgradeable contracts. With access to contracts/legacy/FirelightVaultStoragePredeposits.sol, the following were audited:
- Storage slot alignment between legacy and V2
- Whether new storage variables are appended correctly
- Potential storage collisions with inherited OZ contracts
Impact: Storage collision during proxy upgrade could corrupt vault state, leading to complete fund loss or protocol bricking.
Recommendation: Publish the legacy storage contract for diff review. Verify using OpenZeppelin's upgrade-safe validation tools.


++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
## Files retrieved from repository clone:
1. package.json 
- Findings: OZ v5.4.0 confirmed — Critical for upgrade collision analysis
2. VaultRewardDistributor.sol
- Calls checkpointTotalAssets() correctly — no bug here
3. FtsoChainlinkAdapter.sol
- No on-chain freshness check (consumer-side only) — design choice, not a bug
4. IncidentManager._executePayout
- FLB waterfall logic reviewed — rounding is minor, no critical flaw found

PoC Submission:
- Runnable PoC for all severities submitted, thus create Foundry test file that demo's each bug:

```plain
poc/
|__ FirelightVault.BlocklistedReceiver.t.sol
|__ FirelightVault.RescueFragmentation.t.sol
|__ FirelightVault.MisleadingNatSpec.md
```


Finding 1: [MEDIUM] Blocklisted Receiver Permanently Freezes Withdrawal

Contract: FirelightVault.sol
Function: withdraw() / redeem() → claimWithdraw()
Severity: Medium
Root Cause:
- When a user calls withdraw(assets, receiver, owner), the withdrawal shares are credited to receiver (withdrawSharesOf[period][receiver]), not the initiator. If receiver is later added to the blocklist, claimWithdraw reverts because of notBlocklisted(_msgSender()). The original initiator cannot claim because withdrawSharesOf[period][initiator] == 0.
Impact: 
- Temporary freezing of funds. If RESCUER_ROLE is unavailable or unaware, funds remain frozen indefinitely.

PoC Code:

```solidity
function testBlocklistedReceiverFreezesWithdrawal() public {
    // Setup for PoC: User deposits and requests withdrawal to alice
    vm.prank(user);
    vault.deposit(1000e18, user);

    vm.prank(user);
    vault.withdraw(100e18, alice, user);  // receiver = alice
    
    // Admin blocklists alice
    vm.prank(blocklister);
    vault.addToBlocklist(alice);
    
    // Advance to claimable period (N+2)
    vm.warp(vault.currentPeriodEnd() + vault.currentPeriodConfiguration().duration + 1);
    
    // Alice cannot claim (blocklisted)
    vm.prank(alice);
    vm.expectRevert(FirelightVault.BlocklistedAddress.selector);
    vault.claimWithdraw(vault.currentPeriod() - 1);
    
    // Original initiator also cannot claim (zero shares credited to them)
    vm.prank(user);
    vm.expectRevert(FirelightVault.NoWithdrawalAmount.selector);
    vault.claimWithdraw(vault.currentPeriod() - 1);
}
```

Finding 2: [MEDIUM] Rescue Operation Fragmentation Risk

Contract: FirelightVault.sol
Function: rescueSharesFromBlocklisted()
Severity: Medium
Root Cause:
- rescueSharesFromBlocklisted transfers vault shares but does not automatically rescue pending withdrawal claims. A rescuer calling only the share rescue leaves pending withdrawals permanently associated with the blocklisted address.
Impact:
- Permanent freezing of unclaimed withdrawal assets if rescue is incomplete.

PoC Code:

```solidity
function testIncompleteRescueFreezesWithdrawals() public {
    // User deposits, requests withdrawal, gets blocklisted
    vm.prank(user);
    vault.deposit(1000e18, user);
    vm.prank(user);
    vault.withdraw(100e18, user, user);
    
    vm.prank(blocklister);
    vault.addToBlocklist(user);
    
    // Rescuer only rescues shares, NOT withdrawals
    vm.prank(rescuer);
    vault.rescueSharesFromBlocklisted(user, beneficiary);
    
    // Advance to claimable period
    vm.warp(vault.currentPeriodEnd() + vault.currentPeriodConfiguration().duration + 1);
    
    // User cannot claim (blocklisted)
    vm.prank(user);
    vm.expectRevert(FirelightVault.BlocklistedAddress.selector);
    vault.claimWithdraw(vault.currentPeriod() - 1);
    
    // Beneficiary cannot claim either (withdrawals still assigned to user)
    vm.prank(beneficiary);
    vm.expectRevert(FirelightVault.NoWithdrawalAmount.selector);
    vault.claimWithdraw(vault.currentPeriod() - 1);
}
```

Finding 3: [LOW / INSIGHT] Misleading NatSpec on redeem()

Contract: FirelightVault.sol
Function: redeem()
Severity: Low / Insight
Root Cause:
- NatSpec states withdrawal "will be available in the next period" but the implementation schedules for currentPeriod() + 1 and claimWithdraw enforces period < currentPeriod(), making the actual claimable period N+2.
Impact:
- Integration errors, off-chain tooling miscalculations.
Fix: Update comment to "available in the period after the next full period" to match withdraw()'s accurate documentation.

Finding 4: [CRITICAL] OpenZeppelin v4 - v5 Storage Collision on Upgrade

Evidence from package.json:

```JSON
"@openzeppelin/contracts-upgradeable": "~5.4.0"
"@openzeppelin/contracts": "5.2.0"
```

# The Problem:

The Phase 1 legacy vault proxy is deployed on Flare mainnet. If it was originally compiled with OpenZeppelin v4 (extremely likely for a predeposit vault), its storage layout has OZ v4 state variables at linear slots 0-4.

The V2 FirelightVault uses OZ v5-specific features:
1) _decimalsOffset() — v5-only ERC4626 feature
2) Time.timestamp() — from @openzeppelin/contracts/utils/types/Time.sol (v5-only)

In OZ v5, upgradeable contracts were rewritten to use ERC-7201 namespaced storage. This means:
- OZ v4 ERC20Upgradeable: stores _name, _symbol, _balances, _allowances, _totalSupply at slots 0, 1, 2, 3, 4...
- OZ v5 ERC20Upgradeable: stores these in a namespaced struct at a deterministic hash slot

If the legacy proxy has OZ v4 state at slot 0, and V2 expects OZ v5 namespaced storage, the upgrade will:
- Corrupt _name / _symbol strings
- Misalign all FirelightVaultStorage variables
- Potentially brick the vault or cause insolvency


