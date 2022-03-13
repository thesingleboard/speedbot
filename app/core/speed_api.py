import settings
import logging
from prom_lib import prometheus

#API stuff
from flask import Flask, abort, jsonify, request

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from prometheus_client import make_wsgi_app

#Set flask to output "pretty print"
application = Flask(__name__)

# Add prometheus wsgi middleware to route /metrics requests
application.wsgi_app = DispatcherMiddleware(application.wsgi_app, { '/metrics': make_wsgi_app()})

application.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

api = settings.API
pt = pitemp()

@application.route('/api/'+api+'/alive',methods=['POST'])
def get_alive():

    api_status = 'up'
    device_id = pt.get_cpu_id()
    if(device_id == '0000000000000000'):
        api_status = 'down'

    return jsonify({'DEVICEID': device_id,'STATUS':api_status})

@application.route('/api/'+api+'/status',methods=['GET'])
def get_status():

    #try:
    system_status = pt.get_system_status()
    #except Exception as e:
     #   logging.error("Sytem status: %s"%e)
      #  system_status = 'error'
    
    return jsonify({'status':system_status})
    
if __name__ == '__main__':
    application.run(host='0.0.0.0',port=, debug=True,ssl_context='adhoc')