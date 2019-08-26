import grpc
from concurrent import futures
import logging
import time
import argparse

import serial_pb2 as Serial
import serial_pb2_grpc as rpc

from IntellivueProtocol.RS232 import RS232 as SerialDevice

address = 'localhost'
port = 50051
serial_port = ''


class SerialServer(rpc.SerialServerServicer):

    def __init__(self):
        self.serialDevice = None

    def SerialOpen(self, request, context):
        serial_port = request.data
        try:
            self.serialDevice = SerialDevice(serial_port)
        except IOError as e:
            return Serial.PortResponse(data='IOError')

        return Serial.PortResponse(data='Connected')

    def SerialSend(self, request, context):
        message = request.data
        # output serial message to device
        self.serialDevice.write(message)
        return Serial.Empty()

    def SerialReceive(self, request, context):
        message = ''
        message = self.serialDevice.read()
        return Serial.SerialMessage(data=message)

    def SerialClose(self, request, context):
        self.serialDevice.close()
        return Serial.Empty()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    rpc.add_SerialServerServicer_to_server(SerialServer(), server)
    print('Starting server. Listening...')
    server.add_insecure_port('{}:{}'.format(address, port))
    server.start()
    try:
        while True:
            time.sleep(60 * 60 * 240)
    except KeyboardInterrupt:
        server.stop(0)


def parse_args():
    # Creates an options array from the command-line arguments

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--port', help="Device port (or 'sample')", default="/dev/ttyUSB0")
    _opts = parser.parse_args()
    return _opts


if __name__ == '__main__':
    logging.basicConfig()
    opts = parse_args()
    serial_port = opts.port
    serve()
