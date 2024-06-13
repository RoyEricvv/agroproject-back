from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Restriccion import Restriccion, RestriccionSchema
from marshmallow import ValidationError


#Servicio para listar todas las restricciones
@app.route('/restriccion/<insumo_id>/all', methods=['GET'])
def restriccion_todos(insumo_id):
    if insumo_id == '0':
        #Se crea la lista de toda la restriccion.
        restriccions = Restriccion.query.filter(Restriccion.activo==True).order_by(Restriccion.id).all()
    else:
        #Se crea la lista de toda la restriccion.
        restriccions = Restriccion.query.filter(Restriccion.activo==True).filter(Restriccion.insumo_id == insumo_id).order_by(Restriccion.especie_id).order_by(Restriccion.etapa_vida_id).all()

    if len(restriccions) > 0:
        #Se serializa la información a retornar
        restriccions_schema = RestriccionSchema(many=True)
        data = restriccions_schema.dump(restriccions)
    
        return {"Mensaje": "Lista de Restriccions", "restricciones": data}
    else:
        return {"Mensaje": "No se encontró las restricciones", "insumo_id": insumo_id}, 404

#Servicio para crear una restriccion
@app.route('/restriccion', methods=['POST'])
def restriccion_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    restriccion_schema = RestriccionSchema()
    
    try:
        data = restriccion_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    
    #Se busca restriccion repetido en base de datos
    restriccion_existente = (
        Restriccion.query.filter(Restriccion.activo==True).filter(Restriccion.insumo_id == data["insumo_id"]).filter(Restriccion.especie_id == data["especie_id"]).filter(Restriccion.etapa_vida_id == data["etapa_vida_id"])
        .one_or_none()
    )

    if restriccion_existente is None:

        restriccion_nuevo = Restriccion(
            activo=True,
            porcentaje_permitido=data["porcentaje_permitido"],
            insumo_id=data["insumo_id"],
            especie_id=data["especie_id"],
            etapa_vida_id=data["etapa_vida_id"],
            fecha_creacion=dt.now(),
            fecha_modificacion=dt.now()
        )
        db.session.add(restriccion_nuevo)  # Añade un nuevo registro a la base de datos
        db.session.commit()  # Guarda todos los cambios

        return {"Mensaje": "Se creo restriccion"}
    # La restriccion ya existe
    else:
        return {"Mensaje": "Restriccion ya existe"}, 401

#Servicio para actualizar una restriccion mediante ID
@app.route('/restriccion/update', methods=['POST'])
def restriccion_actualizar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca restriccion en base de datos
    restriccion_actualizar = (
        Restriccion.query.filter(Restriccion.activo==True).filter(Restriccion.insumo_id == json_data["insumo_id"]).filter(Restriccion.especie_id == json_data["especie_id"]).filter(Restriccion.etapa_vida_id == json_data["etapa_vida_id"])
        .one_or_none()
    )

    if restriccion_actualizar is None:
        return {"Mensaje": "Restriccion no existe"}, 404

    restriccion_actualizar.porcentaje_permitido = json_data["porcentaje_permitido"]
    restriccion_actualizar.fecha_modificacion = dt.now()

    db.session.merge(restriccion_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó restriccion."}

#Servicio para eliminar una restriccion de insumo mediante ID
@app.route('/restriccion/delete', methods=['POST'])
def restriccion_eliminar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca contenido Ración en base de datos
    restriccion_eliminar = (
        Restriccion.query.filter(Restriccion.insumo_id == json_data["insumo_id"]).filter(Restriccion.especie_id == json_data["especie_id"]).filter(Restriccion.activo==True)
        .one_or_none()
    )

    if restriccion_eliminar is None:
        return {"Mensaje": "restricción no existe"}, 404
    else:
        restriccion_eliminar.activo=False
        db.session.merge(restriccion_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó restricción"}