from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.ConsumoSanitario import ConsumoSanitario
from aplicacion.modelo.Granja import Granja
from aplicacion.modelo.Animal import Animal
from marshmallow import ValidationError