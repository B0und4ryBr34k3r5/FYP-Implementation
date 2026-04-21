// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IoTData {

    struct SensorData {
        string deviceId;
        string timestamp;
        int temperature;
    }

    SensorData[] public dataRecords;

    event DataStored(
        string deviceId,
        string timestamp,
        int temperature
    );

    function storeData(
        string memory _deviceId,
        string memory _timestamp,
        int _temperature
    ) public {

        dataRecords.push(SensorData({
            deviceId: _deviceId,
            timestamp: _timestamp,
            temperature: _temperature
        }));

        emit DataStored(_deviceId, _timestamp, _temperature);
    }

    function getDataCount() public view returns (uint) {
        return dataRecords.length;
    }

    function getData(uint index) public view returns (
        string memory,
        string memory,
        int
    ) {
        SensorData memory d = dataRecords[index];
        return (d.deviceId, d.timestamp, d.temperature);
    }
}