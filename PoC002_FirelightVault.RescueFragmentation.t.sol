function testIncompleteRescueFreezesWithdrawals() public {
    //user deposits, requests withdrawal, gets blocklisted
    vm.prank(user);
    vault.deposit(1000e18, user);
    vm.prank(user);
    vault.withdraw(100e18, user, user);

    vm.prank(blocklister);
    vault.addToBlocklist(user);

    //Rescuer only rescues shares but doesnt withdrawal
    vm.prank(rescuer);
    vault.rescueSharesFromBlocklisted(user, beneficiary);

    //Advance to claimable period
    vm.warp(vault.currentPeriodEnd() + vault.currentPeriodConfiguration().duration + 1);

    //User cannot claim (blocklisted)
    vm.prank(user);
    vm.expectRevert(FirelightVault.BlocklistedAddrtess.selector);
    vault.claimWithdraw(vault.currentPeriod() - 1);

    //Beneficiary cannot claim either (withdrawals still assigned to user)
    vm.prank(beneficiary);
    vm.expectRevert(FirelightVault.NoWithdrawalAmount.selector);
    vault.claimWithdraw(vault.currentPeriod() - 1);
}