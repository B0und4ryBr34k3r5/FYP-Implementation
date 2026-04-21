const { ethers } = require("hardhat");

async function main() {
  const IoTData = await ethers.getContractFactory("IoTData");
  const contract = await IoTData.deploy();

  await contract.waitForDeployment();

  console.log("Contract deployed to:", contract.target);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});