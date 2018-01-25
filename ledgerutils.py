#!/usr/bin/env python

import sys
import os
import configparser
import argparse
import dateutil.parser

from modules import Alelo
from modules import Itau
from modules import Nubank
from modules import QIF

from ledger import load_list_csv

parser = argparse.ArgumentParser(
        description="Import files into ledger format.")
parser.add_argument("-d", type=str, metavar="DATE", dest="date",
        help="Start parsing from this date")
parser.add_argument("-i", type=argparse.FileType("r"), default=None,
        dest="input_file", metavar="INPUT",
        help="Input file used by the parser")
parser.add_argument("-o", type=argparse.FileType("r"), default=None,
        dest="output_file", metavar="OUTPUT",
        help="Output file to write new entries")
parser.add_argument("command",
        help="Command. Currently supports: 'import', and 'online'")
parser.add_argument("account",
        help="Format name. Currently supports: 'alelo', 'itau', 'nubank', and 'qif'")
args = parser.parse_args()

CONFIG = configparser.ConfigParser()
conf = None
from_date = None
input_file = None
output_file = None
account_type = args.account

load_list_csv()

if args.date:
    from_date = dateutil.parser.parse(args.date).timetuple()

if os.path.isfile('ledgerutils.conf'):
    CONFIG.read('ledgerutils.conf')

if args.account in CONFIG.sections():
    conf = CONFIG[args.account]

if conf and "account_type" in conf:
    account_type = conf["account_type"]

# Command line has priority over config file
if args.input_file:
    input_file = args.input_file
elif 'input_file' in conf:
    input_file = open(conf['input_file'], "r")
if args.output_file:
    output_file = args.output_file
elif 'output_file' in conf:
    output_file = open(conf['output_file'], "r")

LIST_BANKS = {
    'alelo': Alelo.Alelo(conf, output_file=output_file, from_date=from_date),
    'itau': Itau.Itau(conf, output_file=output_file, from_date=from_date),
    'nubank': Nubank.Nubank(conf, output_file=output_file, from_date=from_date),
    'qif': QIF.QIF(conf, output_file=output_file, from_date=from_date)
}

if input_file:
    BANK = LIST_BANKS[account_type]
    if args.command == "import":
        BANK.read_file(input_file)
        BANK.write_entry()
    elif args.command == "online":
        BANK.online()