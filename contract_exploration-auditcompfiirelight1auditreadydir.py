!ls -la /tmp/ | grep -i firelight && echo "---" && ls -la /tmp/

REPO = "/tmp/audit-comp-firelight-1_audit_ready"
!find {REPO}/contracts -name "*.sol" | sort

files = [
    f"{REPO}/contracts/core/CoverOrderAllocator.sol,
    f"{REPO}/contracts/core/IncidentManager.sol,
    f"{REPO}/contracts/core/CoverNFT.sol,
    f"{REPO}/contracts/core/VaultRewardDistributor.sol,
    f"{REPO}/contracts/core/FirelightVaultStorage.sol,
    f"{REPO}/contracts/core/lib/Checkpoints.sol,
    f"{REPO}/contracts/core/lib/PriceFeed.sol,
    f"{REPO}/contracts/core/lib/Decimals.sol,
]

for f in files:
    print(f"\n{'='*80}\n{f}\n{'='*80}")
    with open(f, 'r') as fh:
        print(fh.read()[:8000])
    print("\n[...truncated...]\n")