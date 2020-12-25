import subprocess
import logging

args = ['bash','entrypoint.sh']
out = subprocess.Popen(args, stdout=subprocess.PIPE)
# Run the command
output = out.communicate()[0]