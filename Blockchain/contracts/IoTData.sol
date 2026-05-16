// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title IoTData
 * @dev Smart contract to store and manage IoT sensor data on the blockchain.
 * Acts as the immutable, tamper-proof ledger for cross-verification.
 */
contract IoTData {

    // Struct to represent a single verified sensor reading
    struct SensorData {
        string deviceId;
        string timestamp;
        int temperature;
        string dataHash;
        string zkProof;
    }

    SensorData[] public dataRecords;

    event DataStored(
        string deviceId,
        string timestamp,
        int temperature,
        string dataHash,
        string zkProof
    );

    /**
     * @dev Stores a new verified sensor reading on the blockchain.
     * Only called AFTER the ZKP proof has been verified.
     * @param _deviceId The unique ID of the IoT sensor
     * @param _timestamp The time the reading was taken
     * @param _temperature The recorded temperature
     * @param _dataHash The SHA-256 hash of the original data payload
     * @param _zkProof The JSON string representation of the Zero-Knowledge Proof
     */
    function storeData(
        string memory _deviceId,
        string memory _timestamp,
        int _temperature,
        string memory _dataHash,
        string memory _zkProof
    ) public {

        dataRecords.push(SensorData({
            deviceId: _deviceId,
            timestamp: _timestamp,
            temperature: _temperature,
            dataHash: _dataHash,
            zkProof: _zkProof
        }));

        emit DataStored(_deviceId, _timestamp, _temperature, _dataHash, _zkProof);
    }

    /**
     * @dev Gets the total number of records stored.
     * @return The length of the dataRecords array
     */
    function getDataCount() public view returns (uint) {
        return dataRecords.length;
    }

    /**
     * @dev Retrieves a specific sensor reading by index.
     * Used by the server for cross-verifying database records against the blockchain.
     * @param index The array index of the record
     * @return deviceId, timestamp, temperature, dataHash, zkProof
     */
    function getData(uint index) public view returns (
        string memory,
        string memory,
        int,
        string memory,
        string memory
    ) {
        SensorData memory d = dataRecords[index];
        return (d.deviceId, d.timestamp, d.temperature, d.dataHash, d.zkProof);
    }
}