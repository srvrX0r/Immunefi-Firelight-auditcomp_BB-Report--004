import os

REPO = "/tmp/audit-comp-firelight-1_audit_ready"

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

# Read all core in-scope contracts
cover_order_allocator = read_file(f"{REPO}/contracts/core/CoverOrderAllocator.sol")
incident_manager = read_file(f"{REPO}/contracts/core/IncidentManager.sol")
cover_nft = read_file(f"{REPO}/contracts/core/CoverNFT.sol")
vault_reward_distributor = read_file(f"{REPO}/contracts/core/VaultRewardDistributor.sol")
ftso_adapter = read_file(f"{REPO}/contracts/oracle/FtsoChainlinkAdapter.sol")
firelight_vault_storage = read_file(f"{REPO}/contracts/core/FirelightVaultStorage.sol")
checkpoints_lib = read_file(f"{REPO}/contracts/core/lib/Checkpoints.sol")
price_feed_lib = read_file(f"{REPO}/contracts/core/lib/PriceFeed.sol")
decimals_lib = read_file(f"{REPO}/contracts/core/lib/Decimals.sol")
legacy_vault = read_file(f"{REPO}/contracts/legacy/FirelightVaultPredeposits.sol")
legacy_storage = read_file(f"{REPO}/contracts/legacy/FirelightVaultStoragePredeposits.sol")

# Interfaces
ifirelight_vault = read_file(f"{REPO}/contracts/core/interfaces/IFirelightVault.sol")
icover_order_allocator = read_file(f"{REPO}/contracts/core/interfaces/ICoverOrderAllocator.sol")
iincident_manager = read_file(f"{REPO}/contracts/core/interfaces/IIncidentManager.sol")
iaggregator_v3 = read_file(f"{REPO}/contracts/core/interfaces/IAggregatorV3.sol")

print("Files loaded successfully:")
for name, content in [
    ("CoverOrderAllocator", cover_order_allocator),
    ("IncidentManager", incident_manager),
    ("CoverNFT", cover_nft),
    ("VaultRewardDistributor", vault_reward_distributor),
    ("FtsoChainlinkAdapter", ftso_adapter),
    ("FirelightVaultStorage", firelight_vault_storage),
    ("Checkpoints", checkpoints_lib),
    ("PriceFeed", price_feed_lib),
    ("Decimals", decimals_lib),
    ("LegacyVault", legacy_vault),
    ("LegacyStorage", legacy_storage),
]:
    print(f"  {name}: {len(content)} chars, {content.count(chr(10))} lines")
