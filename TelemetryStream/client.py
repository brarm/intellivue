import time
import logging

import grpc
import threading

import serial_pb2 as Serial
import serial_pb2_grpc as rpc

address = 'infiniwell037'
port = 50051


class Client:
    def __init__(self):
        channel = grpc.insecure_channel('{}:{}'.format(address, str(port)))
        self.conn = rpc.SerialServerStub(channel)
        print('Client connected to server at {}:{}'.format(address, port))

    def open_serial(self, port):
        serial_port = Serial.SerialPort(data=port)
        port_response = self.conn.SerialOpen(serial_port)
        return port_response

    def send_serial(self, message):
        serial_message = Serial.SerialMessage(data=message)
        self.conn.SerialSend(serial_message)

    def receive_serial(self):
        data = self.conn.SerialReceive(Serial.Empty()).data
        return data

    def close_serial(self):
        self.conn.SerialClose(Serial.Empty())


if __name__ == '__main__':
    c = Client()
    logging.basicConfig()
    while 1:
        time.sleep(60 * 60 * 240)
