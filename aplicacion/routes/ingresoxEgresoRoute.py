from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.IngresoxEgreso import IngresoxEgreso, Animal, Equipo, Sanitario, Granja
from marshmallow import ValidationError