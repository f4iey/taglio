# taglio
As you noticed, `taglio` stands for *taglio is another great lightsaber interface option*!

It is yet, another program to write specific commands and sound files to [polaris-opencore](https://github.com/lamadiluce/polaris-opencore) props microcontrollers, written in Python.

The main goal is to simply make a portable program that runs on most popular architectures and operating systems.

## Prerequisites
To use this, you will of course need to have Python installed on your system with the following dependencies:
```sh
pip install pyserial dateutil
```

## Usage
All info available in the help section
```sh
Usage: taglio [-h -v -i -l --erase-all -p [PORT] -c [ASCII]] [PATH TO FILE]

Options:
  -h, --help            show this help message and exit
  -v, --verbose         verbose display for debugging
  -i, --info            read saber FW version and ser no.
  -l, --list            list all files in the saber
  --erase-all           erase the serial flash
  -p PORT, --port=PORT  set the serial port (e.g /dev/ttyUSB0 or COM3)
  -c COMMAND, --command=COMMAND
                        send raw serial command
```


