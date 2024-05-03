const { ethers, upgrades } = require("hardhat");

async function main() {
    const EAAC = await ethers.getContractFactory("EAAC");
    console.log("Deploying EAAC...");
    const eaac = await upgrades.deployProxy(EAAC, [], {initializer: 'initialize'});
    await eaac.waitForDeployment();
    console.log("EAAC deployed to:", await eaac.getAddress());
}

main().catch((error) => {
    console.error(error);
    process.exit(1);
});
