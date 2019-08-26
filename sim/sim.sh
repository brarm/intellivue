#!/bin/bash
trap "kill 0" EXIT

source ~/envs/intellivue/bin/activate
sleep 5
python ../TelemetryStream/PhilipsTelemetryStream.py --values Pleth 128 ECG 256 --port /dev/ttyUSB0&
sleep 10
java -jar $1&

sleep 240
