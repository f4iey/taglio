import serial
import os
import time
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
    t.set_output_format(file_type='raw', bits=16, channels=1, rate=44100)
    # loop over the input files and apply the transformation
    for input_file in glob.glob(input_pattern):
        output_file = output_pattern.format(os.path.splitext(input_file)[0])
        print(input_file, " -> ", output_file)
        t.build(input_file, output_file)
def flash_fw(hexfile):
    if os.system("tycmd --version") == 0:
        os.system("tycmd list")
        if input("Confirm firmware flash on device [y/N]?") == 'y':
            print("Flashing firmware...")
            os.system("tycmd upload " + hexfile)
            print("Flash complete!")
        else:
            print("Operation aborted, exiting...")
    else:
        print("Error: tytools is not installed! Aborting...")
    exit()

def set_color(action, bank, rgbw):
    # Sets the action color (main/flash/swing) to the specified bank (0 to 7)
    prefix = action_format(action).upper()
    out = prefix + bank
    for i in rgbw.split(',')
        out += hex(i)[2:]
    print_ack(out)
    
def get_color(action, bank):
    # Getts the action color (main/flash/swing) from the specified bank (0 to 7)
    prefix = action_format(action)
    print_ack(prefix + bank + '?')

def action_format(action):
    prefix = ''
    match action:
        case 'main':
            prefix = 'c'
        case 'flash':
            prefix = 'f'
        case 'swing':
            prefix = 'w'
        case _:
            print("ERROR: Action not known, aborting...")
            exit(1)
    return prefix

parser = OptionParser(usage='taglio [OPTION] [PATHS TO FILES]')
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
parser.add_option("--flash-hex", action="store", dest="hexfile", default=False, type="string", help="flash the target firmware")
parser.add_option("--set-color", action="store", dest="color", default = False, type="string", help="sets a new color to target bank with decimal RGBW format (e.g --set-color 255,127,0,15)")
parser.add_option("--color-bank", action="store", dest="bank", default='0', type="string", help="selects the target color bank (default 0)")
parser.add_option("--color-action", action="store", dest="colorAction", default='main', type="string", help="selects the target color action (defaults to main)")
parser.add_option("--color-fetch", action="store_true", dest="colorFetch", default=False, help="reads all the colors from the chosen action and bank")


parser.set_defaults(port='/dev/ttyACM0')

(options, args) = parser.parse_args()

# Check if the help option was specified
if len(args) == 0 and not (options.info or options.list or options.erase or options.command or options.wavpath or options.hexfile or options.verbose or options.slist or options.save or options.reset or options.color or options.bank or options.colorAction or options.colorFetch):
    parser.print_help()
    exit()

# Other options not requiring saber connection
if options.wavpath:
    convert_all(options.wavpath)
    print("All wav files have been converted to RAW")
    if len(args) == 0:
        exit()
if options.hexfile:
    flash_fw(options.hexfile)

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
if options.color:
    set_color(options.colorAction, options.bank, options.color)
if options.colorFetch:
    print_multi(action_format(options.colorAction) + '?')

# All options passed, we can send file if th file path has been specified
if len(args) > 0:
    for i in args:
        for audiofile in glob.glob(i):
            # Open the serial port
            if not ser.is_open:
                ser.open()
            # Check if saber is writable
            send("WR?")
            if read().startswith("OK, Write Ready"):
                print("Saber ready to write to serial flash")
                # Check if enough space is available
                with open(audiofile, 'rb') as f:
                    fsize = os.path.getsize(audiofile)
                    send("FREE?")
                    response = read()
                    if response.startswith("FREE="):
                        freespace = int(response[5:])
                        if freespace < fsize:
                            print("Error: Not enough space left on device")
                            exit(1)
                    else:
                        print("Free space query failed")
                        exit(1)
                    print("Writing: ", os.path.basename(audiofile), "to ", options.port)
                    print("Space left on saber: ", freespace)
                    print("File size: ", fsize)
                    send("WR=" + os.path.basename(audiofile) + ',' + str(fsize))
                    if read().startswith('OK, Write'):
                        byte = f.read(1)
                        with tqdm(total=fsize) as pbar:
                            while byte != b'':
                                # send the file byte per byte to serial
                                ser.write(byte)
                                byte = f.read(1)
                                pbar.update(1)
                        print("File ", os.path.basename(audiofile), " written to saber")
                        ser.close()
                        time.sleep(1)
                    else:
                        print("Protocol error")
            else:
                print("Error: Saber not ready for writing!")
