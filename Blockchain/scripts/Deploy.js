const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {

    const IoTData = await hre.ethers.getContractFactory(
        "IoTData"
    );

    const contract = await IoTData.deploy();

    await contract.waitForDeployment();

    const contractAddress = await contract.getAddress();

    console.log(
        "IoTData deployed to:",
        contractAddress
    );

    // SAVE ADDRESS
    const addressPath = path.join(
        __dirname,
        "..",
        "addresses.json"
    );

    let addresses = {
        verifier: "",
        iotdata: ""
    };

    if (fs.existsSync(addressPath)) {

        addresses = JSON.parse(
            fs.readFileSync(addressPath)
        );
    }

    addresses.iotdata = contractAddress;

    fs.writeFileSync(
        addressPath,
        JSON.stringify(addresses, null, 4)
    );

    console.log("IoTData address saved.");
}

main().catch((error) => {

    console.error(error);
    process.exitCode = 1;
});