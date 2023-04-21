import serial
import os
from optparse import OptionParser
from tqdm import tqdm
import sox
import glob

# functions
def send(cmd):
    ser.write((cmd + "\n").encode('ascii', 'ignore'))
def read():
    out = ser.readline().decode()
    if not out:
        print("Nothing more to read.")
        return
    return out
def print_ack(cmd):
    send(cmd)
    print(read())
def print_multi(cmd):
    send(cmd)
    buffer = read()
    while buffer:
        print(buffer, end='')
        buffer = read()
def convert_all(input_path):
    # Converts all WAV files into RAW in the specified directory
    # set the input and output file patterns
    if not input_path.endswith('/'):
        input_path += '/'
    input_pattern = input_path + '*.wav'
    output_pattern = '{}.RAW'
    t = sox.Transformer()
    t.set_output_format(file_type='raw')
    t.convert(samplerate=44100)
    # loop over the input files and apply the transformation
    for input_file in glob.glob(input_pattern):
        output_file = output_pattern.format(os.path.splitext(input_file)[0])
        print(input_file, " -> ", output_file)
        t.build(input_file, output_file)


parser = OptionParser(usage='taglio [OPTION] [PATH TO FILE]')
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
parser.add_option("-s", "--sounds", action="store_true", dest="slist", default=False, help="list config sound filenames")
parser.add_option("-S", "--save", action="store_true", dest="save", default=False, help="save config in non-volatile memory")
parser.add_option("-R", "--reset", action="store_true", dest="reset", default=False, help="reset back to default FW config")
parser.add_option("-C", "--convert", action="store", dest="wavpath", default=False, type="string", help="convert all wav files to raw")
parser.set_defaults(port='/dev/ttyACM0')

(options, args) = parser.parse_args()

# Check if the help option was specified
if len(args) == 0 and not (options.info or options.list or options.erase or options.command or options.wavpath or options.verbose or options.slist or options.save or options.reset):
    parser.print_help()
    exit()

# Other options not requiring saber connection
if options.wavpath:
    convert_all(options.wavpath)
    print("All wav files have been converted to RAW")
    exit()

# Options requiring saber connection
# first, try to open the serial port
print("Trying port ", options.port, "...\n")
try:
    ser = serial.Serial(options.port, baudrate=9600, timeout=0.5)
except serial.serialutil.SerialException as e:
    print("\033[31mError: ", e, "\033[0m")
    exit()


if options.info:
    print_ack("V?")
    print_ack("S?")
if options.list:
    print_multi("LIST?")
if options.slist:
    print_ack("sON?")
    print_ack("sOFF?")
    print_ack("sCL?")
    print_ack("sSW?")
    print_ack("sSMA?")
    print_ack("sSMB?")
if options.save:
    print_ack("SAVE")
if options.reset:
    print_ack("RESET")
if options.erase:
    send("WR?")
    if read().startswith("OK, Write Ready"):
        print_ack("ERASE=ALL")
        ser.timeout = 5
        inByte = ser.read().decode()
        while inByte != 10 or inByte < 65:
            print(inByte, end='')
            inByte = ser.read().decode()
            if not inByte:
                print("Exiting...")
                exit(0)
        ser.timeout = 0.5
        print('')
        print(read())
        print(read())
    else:
        print("Error: Saber not ready to write file, aborting...")
        exit(1)
if options.command:
    print_multi(options.command)

# All options passed, we can send file if th file path has been specified
if len(args) > 0:
    # Check is saber is writable
    send("WR?")
    if read().startswith("OK, Write Ready"):
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
                with tqdm(total=fsize) as pbar:
                    while byte != b'':
                        # send the file byte per byte to serial
                        ser.write(byte)
                        byte = f.read(1)
                        pbar.update(1)
                print("File ", os.path.basename(args[0]), " written to saber")
            else:
                print("Protocol error")
    else:
        print("Error: Saber not ready for writing!")
