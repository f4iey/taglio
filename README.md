# taglio
As you noticed, `taglio` stands for *taglio is another great lightsaber interface option*!

It is yet, another program to write specific commands and sound files to [polaris-opencore](https://github.com/lamadiluce/polaris-opencore) props microcontrollers, written in Python.

The main goal is to simply make a portable program that runs on most popular architectures and operating systems.

## Download
Clone the repository
__Using Git:__
```sh
git clone https://github.com/f4iey/taglio.git
cd taglio
```
__By downloading the source code as an archive:__
```sh
curl -fLO https://github.com/f4iey/taglio/archive/refs/heads/main.zip
unzip main.zip
cd taglio-main
```
If you are not familiar with one of these below, just click the *Download ZIP* button under the `Code` dropdown button.

## Before running
To use this, you will of course need to have `Python` installed on your system with the following dependencies:
__Using pip:__
```sh
pip install -r requirements.txt
```
*If your python libraries are already coped with your package manager, it is recommended to install these two libs using it.*
For the program itself, all info are available in the help section by running `taglio` or `python taglio.py`

In addition, it is possible to *flash the firmware* by *installing* an optional dependency: [tytools](https://github.com/Koromix/tytools/releases)

### Usage and options
```sh
Usage: taglio [OPTION] [PATHS TO FILES]

Options:
  -h, --help            show this help message and exit
  -v, --verbose         verbose display for debugging
  -i, --info            read saber FW version and ser no.
  -l, --list            list all files in the saber
  --erase-all           erase the serial flash
  -p PORT, --port=PORT  set the serial port (e.g /dev/ttyUSB0 or COM3)
  -c COMMAND, --command=COMMAND
                        send raw serial command
  -s, --sounds          list config sound filenames
  -S, --save            save config in non-volatile memory
  -R, --reset           reset back to default FW config
  -C WAVPATH, --convert=WAVPATH
                        convert all wav files to raw
  --flash-hex=HEXFILE   flash the target firmware

```

Wildcards and multiple entries are supported
```sh
taglio path/to/files/*.RAW
taglio path/to/file1.RAW
taglio path/to.file2.RAW
```
