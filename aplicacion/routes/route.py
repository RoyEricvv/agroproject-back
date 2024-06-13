from flask import request, make_response
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db

#Prueba de Servidor Corriendo
@app.route('/ping', methods=['GET'])
def ping():
    return 'Hello, World!' 
