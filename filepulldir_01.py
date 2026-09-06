import os

REPO = "/tmp/audit-comp-firelight-1_audit_ready"

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

# 1. package.json
pkg = read_file(f"{REPO}/package.json")
print("=== package.json ===")
print(pkg)
print("\n" + "="*80 + "\n")

# 2. VaultRewardDistributor full code
vrd = read_file(f"{REPO}/contracts/core/VaultRewardDistributor.sol")
print("=== VaultRewardDistributor.sol ===")
print(vrd)
print("\n" + "="*80 + "\n")

# 3. FtsoChainlinkAdapter full code
ftso = read_file(f"{REPO}/contracts/oracle/FtsoChainlinkAdapter.sol")
print("=== FtsoChainlinkAdapter.sol ===")
print(ftso)
