import subprocess
import logging

args = ['bash','entrypoint.sh']
logging.info('Starting app with entrypoint.sh')
out = subprocess.Popen(args, stdout=subprocess.PIPE)
# Run the command
output = out.communicate()[0]
logging.info('entrypoint start: %s'%(output))