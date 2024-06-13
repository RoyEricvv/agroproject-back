from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.NutrienteRacion import NutrienteRacion, NutrienteRacionSchema
from aplicacion.modelo.RacionFormulada import RacionFormulada
from marshmallow import ValidationError

# Servicios de contenido Ración


#Servicio para listar todos los Nutrientes de la racion
@app.route('/nutrienteRacion/<racion_formulada_id>/all', methods=['GET'])
def nutriente_racion_listar_todos(racion_formulada_id):
    if racion_formulada_id == '0':
        #Se crea la lista de contenidoRaciones.
        nutriente_raciones = NutrienteRacion.query.filter(NutrienteRacion.activo==True).order_by(NutrienteRacion.nutriente_id).all()
    else:
        #Se crea la lista de contenidoRaciones.
        nutriente_raciones = NutrienteRacion.query.filter(NutrienteRacion.activo==True).filter(NutrienteRacion.racion_id == racion_formulada_id).order_by(NutrienteRacion.nutriente_id).all()

    if len(nutriente_raciones)>0:
        #Se serializa la información a retornar
        nutriente_raciones_schema = NutrienteRacionSchema(many=True)
        data = nutriente_raciones_schema.dump(nutriente_raciones)
    
        return {"Mensaje": "Se lista los nutrientes de la ración", "nutrienteRacion": data}
    else:
        return {"Mensaje": "No se encontró nutriente", "racionformuladaID": racion_formulada_id}, 404