latest_round = extract_function_full(ftso, 'latestRoundData')
print("=== latestRoundData ===")
print(latest_round)
print("\n" + "="*80 + "\n")

ftso_view = extract_function_full(ftso, '_ftsoV2View')
print("=== _ftsoV2View ===")
print(ftso_view)