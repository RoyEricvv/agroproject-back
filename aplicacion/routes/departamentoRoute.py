from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Departamento import Departamento, DepartamentoSchema
from marshmallow import ValidationError

# Servicios de Departamento

#Servicio para listar todos los animales
@app.route('/departamento', methods=['GET'])
def departamento_todos():
    #Se crea la lista de todos los departamentos.
    departamentos = Departamento.query.filter(Departamento.activo==True).order_by(Departamento.id).all()
    #Se serializa la información a retornar
    departamentos_schema = DepartamentoSchema(many=True)
    data = departamentos_schema.dump(departamentos)

    return {"Mensaje": "Lista de Departamentos", "departamentos": data}
