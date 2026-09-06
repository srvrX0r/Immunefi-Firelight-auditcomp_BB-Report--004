# Immunefi-Firelight-auditcomp_BB-Report--004
FireLight v2 on-chain cover protocol w contracts implementing upgradeable ERC4626-compatible vault for staked collateral+off-chain-matched cover order allocation flow+cover receipt NFTs+incident assessment &amp; payout execution+vault reward distributor+Flare FTSO v2 price adapter exposed through Chainlink AggregatorV3-compatible read surface


Firelight is an on-chain cover protocol. The contracts implement an upgradeable ERC4626-compatible vault for staked collateral, an off-chain-matched cover order allocation flow, cover receipt NFTs, incident assessment and payout execution, a vault reward distributor, and a Flare FTSO v2 price adapter exposed through a Chainlink AggregatorV3-compatible read surface.  The MVP is intentionally permissioned: trusted operators create and settle cover orders, submit matching commitments, assess incidents, and execute approved payouts. The contracts enforce role boundaries, capacity checks, settlement constraints, payout accounting, withdrawal delays, blocklist/rescue controls, and asset transfer paths.  This audit covers Firelight Phase 2, as described in the Firelight documentation. For more information about Firelight, please visit https://docs.firelight.finance.  Technical Project Information System overview and upgrade context One existing deployed contract is being upgraded: the legacy predeposit vault (contracts/legacy/FirelightVaultPredeposits.sol, with storage in contracts/legacy/FirelightVaultStoragePredeposits.sol). The upgrade implementation is contracts/core/FirelightVault.sol, with V2 storage in contracts/core/FirelightVaultStorage.sol. Reviewers should compare the legacy vault and the V2 vault for storage compatibility and behavior changes. All other in-scope Phase 2 contracts are new deployments.  Upgrade context FirelightVault.sol is the V2 upgrade implementation for the already-deployed legacy predeposit vault (contracts/legacy/FirelightVaultPredeposits.sol), deployed on Flare at 0x4C18Ff3C89632c3Dd62E796c0aFA5c07c4c1B2b3. Reviewers should examine both the new V2 behavior and its compatibility with the legacy vault storage/layout. The legacy contracts (contracts/legacy/FirelightVaultPredeposits.sol and contracts/legacy/FirelightVaultStoragePredeposits.sol) are included to support upgrade-diff and storage-compatibility review. All other in-scope Phase 2 contracts are new deployments.  Priority areas of concern Firelight is most concerned about:  Commitment and settlement correctness in CoverOrderAllocator. Capacity calculation and solvency constraints. Incident/payout accounting: FIFO priority, payout-window behavior, assessment loss validation, first-loss buffer waterfall, vault payout bounds, and interaction between multiple incidents in the same period. Upgradeability safety for the upgradeable contracts. External price and token assumptions, especially FTSO adapter behavior.

Priority areas of concern
Firelight is most concerned about:

Commitment and settlement correctness in CoverOrderAllocator.
Capacity calculation and solvency constraints.
Incident/payout accounting: FIFO priority, payout-window behavior, assessment loss validation, first-loss buffer waterfall, vault payout bounds, and interaction between multiple incidents in the same period.
Upgradeability safety for the upgradeable contracts.
External price and token assumptions, especially FTSO adapter behavior.
Standardized Rules
This program follows Immunefi's standard competition rules. For the full default rules on validity, duplicates, known issues, severity, disputes, KYC, payments, and publication, read How Audit Competitions Work: Rules and Policies. Where this program page defines a specific rule, the program page prevails.

Proof of Concept (PoC) Requirements
A runnable PoC is required. For more information, please read the Web3 PoC Guidelines.

Insight Reporting
Insight reports may be submitted to this program. Runnable code is not required, but the PoC section must describe the conditions under which the insight is valuable.
Only the best report of a given Insight is rewarded. Duplicates of Insights are not rewarded.
Insights are rewarded according to Immunefi's Standardized Competition Reward Terms and are not eligible for mediation or appeal.
