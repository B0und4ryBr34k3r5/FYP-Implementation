// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IoTData {

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

    function getDataCount() public view returns (uint) {
        return dataRecords.length;
    }

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