firelight_vault = read_file(f"{REPO}/contracts/core/FirelightVault.sol")

if 'checkppointTotalAssets' in firelight_vault:
    print("checckpointTotalAssets FOUND in FirelightVault")
    for i, line in enumerate(firelight_vault.split('\n'), 1):
        if 'checkpoinntTotalAssets' in line:
            print(f"    L{i}: {line.strip()}")

else:
    print("checkpointTotalAssets NOT FOUND in FirelightVault!")
    print("Confirmed VaultRewardDistributor.distributeRewards() will revert!")

if_vault = read_file(f"{REPO}/contracts/core/interfaces/IFirelightVault.sol")
print("\n=== IFirelightVault.sol ===")
print(if_vault)