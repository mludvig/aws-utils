#!/usr/bin/env python3

# vpc-config.py - Calculate vpc-config.yml addresses based on the given CIDR
#
# By Michael Ludvig <mludvig@logix.net.nz>
# See https://aws.nz/aws-utils/vpc-config

import sys
import re
import struct
import socket
import argparse

def fatal(message):
    print("ERROR: %s" % message, file=sys.stderr)
    sys.exit(1)

def ip2int(addr):
    return struct.unpack("!I", socket.inet_aton(addr))[0]

def int2ip(addr):
    return socket.inet_ntoa(struct.pack("!I", addr))

def arg_ipaddr(arg):
    try:
        ip_num = ip2int(arg.split("/")[0])
        return int2ip(ip_num)
    except Exception as e:
        msg = "Invalid CIDR: %s" % (arg)
        raise argparse.ArgumentTypeError(msg)

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)
parser.description="""\
Parse a vpc-config.yml template and calculate the CIDRs.
"""
parser.add_argument('--template', type=argparse.FileType('r'), required=True, help='Path to vpc-config.yml.template')
parser.add_argument('--cidr', metavar="CIDR", type=arg_ipaddr, required=True, help='Address range of the VPC. The netmask (e.g. /19) is optional and ignored.')
parser.epilog = """
Template Syntax

    The template may contain the following tokens:

    %cidr%    Will be replated with CIDR (--cidr)

    %cidr+<OFFSET>%
              The value of OFFSET will be added to CIDR.
              E.g. with CIDR=10.0.32.0/19 and
                   template token %cidr+0.0.16.128%/26
                   the output will be: 10.0.48.128/26

    By Michael Ludvig - Check out http://aws.nz/ for more.
    """

args, extra = parser.parse_known_args()

cidr_base = ip2int(args.cidr)

lineno = 0
while True:
    lineno += 1
    line = args.template.readline()
    if not line:
        break
    line = line.rstrip()
    tokens = re.findall("%cidr.*?%", line)
    if not tokens:
        print(line)
        continue
    for token in tokens:
        if token == "%cidr%":
            line = line.replace(token, args.cidr)
            continue
        m = re.match("%cidr *\+ *(\d+\.\d+\.\d+\.\d+)%", token)
        if m:
            try:
                offset = ip2int(m.group(1))
            except:
                fatal("Invalid offset in token on line %d: %s" % (lineno, token))
            ip = int2ip(cidr_base + offset)
            line = line.replace(token, ip)
            continue
        fatal("Invalid token on line %d: %s" % (lineno, token))
    print(line)
