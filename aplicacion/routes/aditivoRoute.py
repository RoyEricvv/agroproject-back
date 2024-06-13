from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Aditivo import Aditivo, AditivoSchema
from aplicacion.modelo.Departamento import Departamento
from aplicacion.modelo.MateriaSeca import MateriaSeca
from marshmallow import ValidationError

# Servicios de Aditivo


#Servicio para listar todos los aditivos
@app.route('/aditivos/<aditivos_id>', methods=['GET'])
def aditivo_listar_por_Aditivo(aditivos_id):
    #Se crea la lista de usuarios.
    aditivos = Aditivo.query.filter(Aditivo.aditivo_id == aditivos_id).filter(Aditivo.activo == True).order_by(Aditivo.insumo_id).all()

    #Se serializa la información a retornar
    aditivos_schema = AditivoSchema(many=True)
    data = aditivos_schema.dump(aditivos)
 
    return {"Mensaje": "Lista de aditivos", "aditivos": data}

#Servicio para crear un aditivo
@app.route('/aditivos', methods=['POST'])
def aditivo_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400    

    relacion = json_data["relacion"]
    aditivo_id = json_data["aditivo_id"]
    insumo_id = json_data["insumo_id"]

    #Se busca usuario repetido en base de datos
    aditivo_existente = (
        Aditivo.query.filter(Aditivo.aditivo_id == aditivo_id).filter(Aditivo.insumo_id == insumo_id).filter(Aditivo.activo == True)
        .one_or_none()
    )
    if aditivo_existente is None:

        aditivo_nuevo = Aditivo(
            activo=True,
            relacion=relacion,
            aditivo_id=aditivo_id,
            insumo_id=insumo_id,
            fecha_creacion=dt.now(),
            fecha_modificacion=dt.now()
        )
        db.session.add(aditivo_nuevo)  # Añade un nuevo registro a la base de datos
        db.session.commit()  # Guarda todos los cambios

        return {"Mensaje": "Se creo aditivo"}
    # El usuario ya existe
    else:
        return {"Mensaje": "Aditivo ya existe"}, 401

#Servicio para actualizar un aditivo mediante ID
@app.route('/aditivos/<aditivos_id>/<insumo_id>/update', methods=['POST'])
def aditivo_actualizar(aditivos_id,insumo_id):

    #Se busca usuario en base de datos
    aditivo_actualizar = (
        Aditivo.query.filter(Aditivo.aditivo_id == aditivos_id).filter(Aditivo.insumo_id == insumo_id).filter(Aditivo.activo == True)
        .one_or_none()
    )

    if aditivo_actualizar is None:
        return {"Mensaje": "Aditivo no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    aditivo_schema = AditivoSchema()
    try:
        data = aditivo_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    relacion = data["relacion"]

    aditivo_actualizar.relacion = relacion
    aditivo_actualizar.fecha_modificacion = dt.now()

    db.session.merge(aditivo_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó aditivo"}

#Servicio para eliminar una aditivo mediante ID
@app.route('/aditivos/<aditivos_id>/<insumo_id>/delete', methods=['GET'])
def aditivo_eliminar(aditivos_id, insumo_id):

    #Se busca usuario en base de datos
    aditivo_eliminar = (
        Aditivo.query.filter(Aditivo.aditivo_id == aditivos_id).filter(Aditivo.insumo_id == insumo_id).filter(Aditivo.activo == True)
        .one_or_none()
    )

    if aditivo_eliminar is None:
        return {"Mensaje": "Aditivo no existe"}, 404
    else:
        aditivo_eliminar.activo = False
        db.session.merge(aditivo_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó aditivo "}