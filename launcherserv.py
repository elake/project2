import sys
import serial
import argparse
import time
import stormLauncher

global debug
debug = False

def main():
    args = parse_args()
    launcher = stormLauncher.launchControl()
    sent = 0
    # Initialize some stuff...
    if args.serialport:
        print("Opening serial port: %s" % args.serialport)
        serial_out = serial_in =  serial.Serial(args.serialport, 9600)
    else:
        print("No serial port.  Supply one with the -s port option")
        sys.exit()

    if args.verbose:
        debug = True
    else:
        debug = False

    idx = 0
    time.sleep(5.0)
    while True:
        msg = receive(serial_in) # get the message coming in on the serial port
        print(msg)
        msg = msg.split(" ")
        if len(msg) == 5: # Receiving num_lasers
            laser_array = lasersystem.LaserSystem(msg[4])
        elif (len(msg) == 3):
            if (0 <= int(msg[2]) <= 14 and not sent):
                    shoot_angle = laser_array.get_angle(msg[2])
                    launcher.face_angle(shoot_angle)
                    sent = 1
                    launcher.turretFire()

def send(serial_port, message):
    """
    Sends a message back to the client device.
    """
    full_message = ''.join((message, "\n"))

    (debug and
        print("server:" + full_message + ":") )

    reencoded = bytes(full_message, encoding='ascii')
    serial_port.write(reencoded)


def receive(serial_port, timeout=None):
    """
    Listen for a message. Attempt to timeout after a certain number of
    milliseconds.
    """
    raw_message = serial_port.readline()

    debug and print("client:", raw_message, ":")

    message = raw_message.decode('ascii')

    return message.rstrip("\n\r")

def parse_args():
    """
    Parses arguments for this program.
    Returns an object with the following members:
        args.
             serialport -- str
             verbose    -- bool
             graphname  -- str
    """

    parser = argparse.ArgumentParser(
        description='Firing instructions',
        epilog = 'If SERIALPORT is not specified, stdin/stdout are used.')
    parser.add_argument('-s', '--serial',
                        help='path to serial port',
                        dest='serialport',
                        default='/dev/ttyACM0')
    parser.add_argument('-v', dest='verbose',
                        help='verbose',
                        action='store_true')
    return parser.parse_args()

if __name__ == '__main__':
    main()
