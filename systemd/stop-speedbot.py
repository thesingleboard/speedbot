#!/usr/bin/python

import settings
import subprocess

args = ['sudo','docker','stop']

try:
    out = subprocess.Popen(args, stdout=subprocess.PIPE)
    # Run the command
    output = out.communicate()[0]
except Exception as e:
    print(output)