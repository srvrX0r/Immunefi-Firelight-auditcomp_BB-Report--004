approve = extract_function_full(incident_manager, 'approveCurrentAssessment')
print("=== approveCurrentAssessment ===")
print(approve)
print("\n" + "="*80 + "\n")


decimals_lib = read_file(f"{REPO}/contracts/core/lib/Decimals.sol")
print("=== Decimals.sol ===")
print(decimals_lib)