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

# Auditing Information for Report--004:

The following security audit was performed in collaboration with @dhasirar during week 1 of the program commencement.

##Pre-configuration##

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

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Analysis :

I successfully retrieved and analyzed FirelightVault.sol (the core ERC4626 vault with delayed withdrawals). I initially encountered access restrictions on the Immunefi audit repository for the remaining high-priority contracts until cloning the audit competition raw test fork through the repo: CoverOrderAllocator.sol, IncidentManager.sol, CoverNFT.sol, FtsoChainlinkAdapter.sol, VaultRewardDistributor.sol. Examinations of VaultRewardDistributor showed it calls _vault.checkpointTotalAssets() which requires CHECKPOINT_ROLE. This is good because it does update the checkpoint. Verifying whether the vault actually has this function.
Analyzing FtsoChainlinkAdapter showed that the latestRoundData function does not check freshness as it passes through updatedAt as the FTSO timestamp, but there's no check against block.timestamp or a max age. However, the consumer (CoverOrderAllocator and IncidentManager) do check maxPriceAge when calling getPrice(), which is handled at the consumer level. The audit revealed interesting artifacts when analyzing the legacy vault code due to the import path existing in both OZ v4 and v5 while the V2 Phase uses _decimalsOffset() which is v5-specific. And Time.timestamp() from @openzeppelin/contracts/utils/types/Time.sol which is v5-specific:

```solidity
import {ERC4626Upgradeable} from "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC4626Upgradeable.sol";
```

In OZ v5, upgradeable contracts were rewritten to use ERC-7201 namespaced storage. This means:

```
OZ v4: ERC20Upgradeable stores _name, _symbol, _balances, _allowances, _totalSupply at slots 0-4 (linear)
OZ v5: ERC20Upgradeable stores these in a namespaced struct at a deterministic slot (ERC-7201)
```

If the legacy vault was compiled with OZ v4, its proxy has OZ v4 state at slots 0-4. If V2 is compiled with OZ v5, the V2 implementation would look for OZ v5 state at the namespaced slot, but the proxy still has OZ v4 state at slots 0-4. The repo has a single package.json with OZ v5 while the legacy contracts are in the same repo. If the entire repo uses OZ v5, then the legacy was probably re-compiled with v5 for testing purposes, but the MAINNET deployment was done earlier with v4. The final discovery during the audit was during the FirelightVault revision for the checkpointTotalAssets function that VaultRewardDistributor calls. The payout function in FirelightVault has a potential issue with how it handles withdrawAssets and withdrawShares:

```solidity
function payout(...) {
    // ...
    uint256 capturePeriodWithdrawals = withdrawAssets[capturePeriod + 1];
    uint256 nextPeriodWithdrawals;
    if (_currentPeriod == capturePeriod + 1) {
        nextPeriodWithdrawals = withdrawAssets[capturePeriod + 2];
    }
    
    uint256 activePayableAmount = currentActiveAssets + capturePeriodWithdrawals + nextPeriodWithdrawals;
    paidAmount = Math.min(amount, Math.min(assetsAtCapturePeriod, activePayableAmount));
    
    if (paidAmount > 0) {
        // ... computes paidFromActive, paidFromCaptureWithdrawals, paidFromNextWithdrawals
        
        withdrawAssets[capturePeriod + 1] = capturePeriodWithdrawals - paidFromCaptureWithdrawals;
        if (paidFromNextWithdrawals > 0) {
            withdrawAssets[capturePeriod + 2] = nextPeriodWithdrawals - paidFromNextWithdrawals;
        }
        
        pendingWithdrawAssets -= paidFromCaptureWithdrawals + paidFromNextWithdrawals;
        
        IERC20(asset()).safeTransfer(to, paidAmount);
    }
}

// withdrawShares is NEVER modified in payout. But claimWithdraw computes assets using:
assets = _convertToAssetsTotals(
    withdrawSharesOf[period][sender],
    withdrawShares[period],
    withdrawAssets[period],
    Math.Rounding.Floor
);
```

After payout reduces withdrawAssets[period] but NOT withdrawShares[period], the ratio changes. Later claimers get fewer assets per share.
When a user requests withdrawal, they burn shares and withdrawAssets[period] and withdrawShares[period] are both incremented. The ratio at that moment is fixed.
After payout reduces withdrawAssets[period] but not withdrawShares[period], the ratio withdrawAssets / withdrawShares decreases. So when a user claims, they get fewer assets than they originally requested.
However, the payout also reduces pendingWithdrawAssets by the same amount and _convertToAssetsTotals uses the current withdrawAssets[period] and withdrawShares[period] values.

This is a bug when considering the following:
- Period 1: Alice requests withdrawal of 100 assets â†’ withdrawAssets[2] = 100, withdrawShares[2] = 100
- Period 1: Bob requests withdrawal of 100 assets â†’ withdrawAssets[2] = 200, withdrawShares[2] = 200
- Payout happens in period 1 (capturePeriod = 1), taking 50 from withdrawAssets[2]
- Now withdrawAssets[2] = 150, withdrawShares[2] = 200
- When Alice claims in period 3: assets = 100 * 150 / 200 = 75 assets (not 100)
- When Bob claims in period 3: assets = 100 * 150 / 200 = 75 assets (not 100)

This means payout slashes withdrawal amounts! The users who haven't claimed yet bear the loss.
The docs say "payout can execute during the incident period or the following period" and "withdrawals requested during the capture period are assigned to capturePeriod + 1 and remain payable while payout is allowed."
The code seems to intentionally allow payout to take from pending withdrawals. But the fact that withdrawShares is not reduced means the share-to-asset ratio becomes distorted.
When looking more carefully at the payout function:

```solidity
if (_currentPeriod == capturePeriod) {
    uint256 payableAmount = currentActiveAssets + capturePeriodWithdrawals;
    paidFromActive = paidAmount.mulDiv(currentActiveAssets, payableAmount);
    paidFromCaptureWithdrawals = paidAmount - paidFromActive;
}
```

In the capture period, payout takes from both active assets and capture period withdrawals. The paidFromCaptureWithdrawals is subtracted from withdrawAssets[capturePeriod + 1].
But withdrawShares[capturePeriod + 1] is not reduced. This means the remaining withdrawals are under-collateralized.
The docs say: "If the underlying staked asset decreases in USD value, available capital and the Capital Adequacy Ratio decrease. Severe collateral drawdowns can reduce coverage capacity and may cause shortfalls or undercollateralization relative to outstanding cover obligations."
This suggests undercollateralization is a known risk. But the specific mechanism of slashing unclaimed withdrawals without adjusting shares seems like it could cause accounting issues. When paidFromCaptureWithdrawals > 0 and withdrawShares is not updated in claimWithdraw:

```solidity
assets = _convertToAssetsTotals(
    withdrawSharesOf[period][sender],
    withdrawShares[period],
    withdrawAssets[period],
    Math.Rounding.Floor
);
```
If withdrawAssets[period] was reduced by payout but withdrawShares[period] wasn't, then all claimers for that period get less than they expected. This is effectively a pro-rata haircut on unclaimed withdrawals.
This could be argued as "intentional" since the protocol needs to pay out claims. But it should probably be documented more clearly.
When checking if there's a way to exploit the payout function to pay out more than assetsAtCapturePeriod:

```solidity
uint256 assetsAtCapturePeriod = totalAssetsAt(capturePeriodStart);
uint256 currentActiveAssets = totalAssets();

uint256 capturePeriodWithdrawals = withdrawAssets[capturePeriod + 1];
uint256 nextPeriodWithdrawals;
if (_currentPeriod == capturePeriod + 1) {
    nextPeriodWithdrawals = withdrawAssets[capturePeriod + 2];
}

uint256 activePayableAmount = currentActiveAssets + capturePeriodWithdrawals + nextPeriodWithdrawals;
paidAmount = Math.min(amount, Math.min(assetsAtCapturePeriod, activePayableAmount));
```

paidAmount is capped by both assetsAtCapturePeriod and activePayableAmount, which seems safe but totalAssets() returns super.totalAssets() - pendingWithdrawAssets. And pendingWithdrawAssets includes ALL pending withdrawals across all periods, but activePayableAmount only includes withdrawals for capturePeriod + 1 and capturePeriod + 2.
So currentActiveAssets = totalVaultAssets - pendingWithdrawAssets(all periods) and activePayableAmount = currentActiveAssets + withdrawAssets[capturePeriod + 1] + withdrawAssets[capturePeriod + 2].
This means activePayableAmount = totalVaultAssets - pendingWithdrawAssets(all other periods).
So if there are pending withdrawals for period N+3, N+4, etc., they are excluded from activePayableAmount. This means activePayableAmount could be HIGHER than totalAssets() alone would suggest.
However, paidAmount is also capped by assetsAtCapturePeriod, which is a historical snapshot. So the total payout is still bounded and thus verifies that Payout logic is actually quite carefully designed. When checking the CoverOrderAllocator for the Merkle leaf encoding issue in _settleCoverOrder:

```solidity
bytes32 leaf = keccak256(bytes.concat(keccak256(abi.encode(orderId, marketCoverAllocations))));
```

This uses abi.encode(orderId, marketCoverAllocations) where marketCoverAllocations is a dynamic array of structs. In Solidity, abi.encode of a dynamic array includes the array length and each element. So the encoding is:
- orderId (uint256)
- offset to array (uint256)
- array length (uint256)
- each element

This is properly structured because the double-hash (hash the encoding, then hash with length prefix) matches OpenZeppelin's standard. However, marketCoverAllocations is a calldata array. abi.encode of a calldata array includes the length and keccak256(bytes.concat(keccak256(...))) is the OZ v5 standard Merkle leaf format.
When checking if there's an issue with commitAllocation and recommitAllocation in commitAllocation:

```solidity
uint48 graceExpiresAt = uint48(block.timestamp) + $.settlementGracePeriod;
if (graceExpiresAt >= $.vault.currentPeriodEnd()) revert CommitTooCloseToPeriodEnd();
```

And in recommitAllocation:

```solidity
uint48 graceExpiresAt = uint48(block.timestamp) + $.settlementGracePeriod;
if (graceExpiresAt >= $.vault.currentPeriodEnd()) revert CommitTooCloseToPeriodEnd();
```
recommitAllocation uses $.vault.currentPeriodEnd() which is the CURRENT period's end, but recommitAllocation is for a specific period parameter. If period is not the current period, this check is wrong. When looking at _replaceableCommitment:

```solidity
function _replaceableCommitment(CoverOrderAllocatorStorage storage $, uint256 period) private view returns (AllocationCommitment storage commit) {
    commit = $.allocationCommitments[period];
    if (commit.root == bytes32(0)) revert NoCommitForPeriod();
    uint256 currentPeriod = _currentPeriod();
    if (period != currentPeriod) revert InvalidCommitmentPeriod(period, currentPeriod);
    if (commit.totalSettledCover > 0 || commit.totalSettledPremium > 0) revert CommitmentAlreadySettled();
}
```
So recommitAllocation can only be called for the current period. The check period != currentPeriod enforces this. So the currentPeriodEnd() check is correct.

Last check: the VaultRewardDistributor calling checkpointTotalAssets(). Upon verifying whether the vault has this function and it's properly restricted by looking at the Vault reward distributor code:

```solidity
_vault.checkpointTotalAssets();
```

In the FirelightVault, checkpointTotalAssets is missing in the FirelightVault code previously analyzed. When checking if it exists in the FirelightVault code, I see functions such as:
- totalAssets()
- totalAssetsAt()
- balanceOfAt()
- totalSupplyAt()

If checkpointTotalAssets doesn't exist in FirelightVault, then VaultRewardDistributor.distributeRewards() would revert when calling it. The vault might inherit it from somewhere, or it might be in the interface. The IFirelightVault interface would tells me this is a bug because if VaultRewardDistributor calls a function that doesn't exist on the vault, all reward distributions would revert.

- checkpointTotalAssets might be an external function that pushes the current totalAssets to the checkpoint trace.

Looking at the vault code, I see _traceTotalAssets.push(ts, _totalAssets) is called in _logTrace. But there's no public checkpointTotalAssets function visible.
The VaultRewardDistributor has onlyRole(DISTRIBUTOR_ROLE) on distributeRewards, and it calls _vault.checkpointTotalAssets(). If this function doesn't exist or isn't accessible, the distributor is broken. The distributor is a new deployment for Phase 2. It might be designed to work with the V2 vault which has this function. When revising the FirelightVault code more carefully, I see totalAssetsAt(uint48 timestamp) which does _traceTotalAssets.upperLookupRecent(timestamp). The _traceTotalAssets is updated in _logTrace which is called during deposits, withdrawals, and payouts. However, there's no explicit checkpointTotalAssets function. This means when VaultRewardDistributor transfers assets to the vault, the vault's _traceTotalAssets is NOT updated. So totalAssetsAt() would return stale values until the next deposit/withdrawal/payout triggers _logTrace.

## Confirmed bug:  Historical queries for total assets would be incorrect after reward distribution until the next state-changing operation.
- The distributor calls _vault.checkpointTotalAssets(). If this function exists, it would update the checkpoint. If it doesn't exist, the call reverts.

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Summary of audit findings:

1. package.json - Confirms OZ v5.4.0 is used. This is CRITICAL for the upgradeability finding.
2. VaultRewardDistributor - It does call checkpointTotalAssets() which exists in the vault with CHECKPOINT_ROLE. The distributor itself doesn't have reentrancy protection but it only does safeTransferFrom and then calls the vault checkpoint. This seems okay.
3. FtsoChainlinkAdapter - latestRoundData does NOT check freshness itself, but consumers check maxPriceAge. The adapter passes through updatedAt as the FTSO timestamp. No stale price check in the adapter itself.
4. IncidentManager _executePayout - The waterfall takes FLB first, then vault. It has rounding issues but they're minor. The main issue is that safeTransferForm from FLB reverts if allowance is insufficient, althought documented as intentional.
5. FirelightVault - checkpointTotalAssets exists at L523 with onlyRole(CHECKPOINT_ROLE)

Confirmed findings:

1. Blocklist Receiver Freeze Withdrawal (Medium) -- Confirmed
2. Rescure Operation Fragmentation (Medium) -- Confirmed
3. Misleading NatSpec on redeem() (Low/Insight) -- Confirmed
4. OZ v4-v5 Storage Collision on Upgrade (Critical lead) -- Very Strong////

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


-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Files retrieved from repository clone:

1. package.json 
- Findings: OZ v5.4.0 confirmed — Critical for upgrade collision analysis
2. VaultRewardDistributor.sol
- Calls checkpointTotalAssets() correctly — no bug here
3. FtsoChainlinkAdapter.sol
- No on-chain freshness check (consumer-side only) — design choice, not a bug
4. IncidentManager._executePayout
- FLB waterfall logic reviewed — rounding is minor, no critical flaw found


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

Severity: Critical
Root Cause: 
- The legacy vault was Phase 1, deployed before Phase 2, but compiled together.
Impact:
- If Phase 1 was compiled with OZ v4, then upgrading to V2 (compiled with OZ v5) would cause storage collision.

Fix: Update version numbers in package.json and within documentation specifying OZ v4 -> v5 Phase 1 (V1) as well as OZ v4 -> v5 Phase 2 (V2).

Evidence from package.json:

```JSON
"@openzeppelin/contracts-upgradeable": "~5.4.0"
"@openzeppelin/contracts": "5.2.0"
```
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



-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
