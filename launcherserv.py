import sys
import serial
import argparse
import time
import launcher
import lasersystem
global debug
debug = False

def main():
    args = parse_args()
    turret = launcher.Turret()
    laser_array = None

    # Initialize the serial port
    if args.serialport:
        print("Opening serial port: %s" % args.serialport)
        serial_out = serial_in = serial.Serial(args.serialport, 9600)
        serial_in.flushInput()
    else:
        print("No serial port.  Supply one with the -s port option")
        sys.exit()

    if args.verbose:
        debug = True
    else:
        debug = False

    prev_laser = None
    prev_time = 0

    time.sleep(1.0)
    while True:
        msg = receive(serial_in) # get the message coming in on the serial port
        print(msg)
        msg = msg.split(" ")
        if len(msg) == 5 and msg[0] == "Number": # Receiving num_lasers
            try: int(msg[4]) 
            except ValueError: continue
            laser_array = lasersystem.LaserSystem(int(msg[4]))
        elif (len(msg) == 3 and msg[0] == "Laser" and laser_array):
            # receiving laser interrupt; double check that this is not a faulty
            # serial port message:
            try: int(msg[2])
            except ValueError: continue
            cur_laser = int(msg[2])
            cur_time = time.time()
            if prev_laser is None: # two lasers have been interrupted
                prev_laser = cur_laser
                prev_time = time.time()
                continue

            if prev_laser != cur_laser: # then the target is moving
                a1 = laser_array.get_angle(prev_laser) # get angles of lasers
                a2 = laser_array.get_angle(cur_laser)
                # determine velocity of the target
                velocity = target_velocity(a1, a2, prev_time, cur_time)
                # ask the turret to turn to catch up to the target and return
                # the amount of time it needs to wait for the target to come
                # back around
                wait_time = turret.lead_target(a2, velocity)
                print(wait_time)
                # wait the indicated amount of time, then fire on the target
                time.sleep(wait_time)
                turret.fire()
            else: # the target is stationary
                angle = laser_array.get_angle(cur_laser) # get angle of laser
                # ask the turret: turn to face the angle and fire on the target
                turret.face_angle(angle)
                turret.fire()
            serial_in.flushInput()
            prev_laser = None

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

def target_velocity(prev_angle, cur_angle, prev_time, cur_time):
    '''
    determine the radial velocity of the target given its current angle relative
    to its previous angle at the given times
    '''
    return (cur_angle - prev_angle) / (cur_time - prev_time)

if __name__ == '__main__':
    main()

