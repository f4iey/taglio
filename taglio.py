import serial
import os
from optparse import OptionParser

# functions
def send(cmd):
    ser.write((cmd + "\n").encode('ascii', 'ignore'))
def read():
    out = ser.readline().decode()
    if not out:
        print("Read timeout\n")
        return
    return out
def print_ack(cmd):
    send(cmd)
    print(read())

parser = OptionParser(usage='taglio [-h -v -i -l --erase-all -p [PORT] -c [ASCII]] [PATH TO FILE]')
parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
                  help="verbose display for debugging")
parser.add_option("-i", "--info",
                  action="store_true", dest="info", default=False, help="read saber FW version and ser no.")
parser.add_option("-l", "--list",
                  action="store_true", dest="list", default=False, help="list all files in the saber")
parser.add_option("--erase-all",
                  action="store_true", dest="erase", default=False, help="erase the serial flash")
parser.add_option("-p", "--port", action="store", dest="port", type="string",
                  help="set the serial port (e.g /dev/ttyUSB0 or COM3)")
parser.add_option("-c", "--command", action="store", dest="command", default=False, type="string",
                  help="send raw serial command")
parser.set_defaults(port='/dev/ttyACM0')

(options, args) = parser.parse_args()


# Check if the help option was specified
if len(args) == 0 and not options.__dict__:
    parser.print_help()

# first, try to open the serial port
print("Trying port ", options.port, "...\n")
try:
    ser = serial.Serial(options.port, baudrate=9600)
except serial.serialutil.SerialException as e:
    print("\033[31mError: ", e, "\033[0m")


if options.info:
    print_ack("V?")
    print_ack("S?")
if options.list:
    print_ack("LIST?")
if options.erase:
    send("WR?")
    if read() == 'OK, Write Ready':
        print_ack("ERASE=ALL")
        inByte = ser.read(timeout=5)
        while inByte != 10 or inByte < 65:
            print(chr(inByte), end='')
            inByte = ser.read(timeout=5)
            if not inByte:
                print("Error: communication timed out...")
                exit(1)
        print('')
        print(read())
        print(read())
    else:
        print("Error: Saber not ready to Write file, aborting...")
        exit(1)
if options.command:
    print(options.command)
    print_ack(options.command)

# All options passed, we can send file if th file path has been specified
if len(args) > 0:
    # Check is saber is wriyable
    send("WR?")
    if read() == 'OK, Write Ready':
        print("Saber ready to write to serial flash")
        # Check if enough space is available
        with open(args[0], 'rb') as f:
            fsize = os.path.getsize(args[0])
            send("FREE?")
            response = read()
            if response.startswith("FREE="):
                freespace = int(response[5:])
                if freespace < fsize:
                    print("Error: Not enough space left on device")
                    exit(1)
            else:
                print("Protocol error")
                exit(1)
            print("Writing: ", os.path.basename(args[0]), "to ", options.port)
            print("Space left on saber: ", freespace)
            print("File size: ", fsize)
            send("WR=" + os.path.basename(args[0]) + ',' + str(fsize))
            if read().startswith('OK, Write'):
                byte = f.read(1)
                while byte != b'':
                    # send the file byte per byte to serial
                    ser.write(byte)
                    byte = f.read(1)
                    # future add rmaining bytes time with dateutil
                print("File ", os.path.basename(args[0]), " written to saber")
            else:
                print("Protocol error")
    else:
        print("Error: Saber not ready for writing!")
