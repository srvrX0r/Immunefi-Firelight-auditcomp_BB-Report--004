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