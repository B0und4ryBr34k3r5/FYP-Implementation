const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {

    const Verifier = await hre.ethers.getContractFactory(
        "Groth16Verifier"
    );

    const verifier = await Verifier.deploy();

    await verifier.waitForDeployment();

    const verifierAddress = await verifier.getAddress();

    console.log(
        "Verifier deployed to:",
        verifierAddress
    );

    // =========================
    // SAVE ADDRESS
    // =========================

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

    addresses.verifier = verifierAddress;

    fs.writeFileSync(
        addressPath,
        JSON.stringify(addresses, null, 4)
    );

    console.log("Verifier address saved.");
}

main().catch((error) => {

    console.error(error);
    process.exitCode = 1;
});