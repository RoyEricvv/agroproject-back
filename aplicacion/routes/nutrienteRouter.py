from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Nutriente import Nutriente, NutrienteSchema
from marshmallow import ValidationError

# Servicios de Nutriente


#Servicio para listar todos los nutrientes
@app.route('/nutrientes', methods=['GET'])
def nutriente_listar_todos():
    #Se crea la lista de usuarios.
    nutrientes = Nutriente.query.filter(Nutriente.activo==True).order_by(Nutriente.nombre).all()

    #Se serializa la información a retornar
    nutrientes_schema = NutrienteSchema(many=True)
    data = nutrientes_schema.dump(nutrientes)
 
    return {"Mensaje": "Lista de nutrientes", "nutrientes": data}

#Servicio para listar una nutrientes por id
@app.route('/nutrientes/<nutrientes_id>', methods=['GET'])
def nutriente_listar_uno(nutrientes_id):
    #Se busca el nutriente
    nutriente = Nutriente.query.filter(Nutriente.activo==True).filter(Nutriente.id == nutrientes_id).one_or_none()

    #Se encontró el nutrientes
    if nutriente is not None:

        # Se serializa la información a retornar
        nutriente_schema = NutrienteSchema()
        data = nutriente_schema.dump(nutriente)
        return {"Mensaje": "Nutriente encontrada", "nutriente": data}

    # No se encontró el nutrientes
    else:
        return {"Mensaje": "No se encontró el nutriente", "nutrienteId": nutrientes_id},404

#Servicio para crear una nutriente
@app.route('/nutrientes', methods=['POST'])
def nutriente_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    nutriente_schema = NutrienteSchema()
    
    try:
        data = nutriente_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    nombre = data["nombre"]

    #Se busca nutriente repetido en base de datos
    nutriente_existente = (
        Nutriente.query.filter(Nutriente.nombre == nombre).filter(Nutriente.activo==True)
        .one_or_none()
    )

    if nutriente_existente is None:

        if nombre:
            nutriente_nuevo = Nutriente(
                activo=True,
                nombre=nombre,
                abreviatura=data["abreviatura"],
                unidad=data["unidad"],
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            db.session.add(nutriente_nuevo)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

            return {"Mensaje": "Se creo nutriente"}
    # El nutriente ya existe
    else:
        return {"Mensaje": "Nutriente ya existe", "nutriente": nombre}, 401

#Servicio para actualizar un nutriente mediante ID
@app.route('/nutrientes/<nutrientes_id>', methods=['POST'])
def nutriente_actualizar(nutrientes_id):

    #Se busca nutriente en base de datos
    nutriente_actualizar = (
        Nutriente.query.filter(Nutriente.id == nutrientes_id).filter(Nutriente.activo==True)
        .one_or_none()
    )

    if nutriente_actualizar is None:
        return {"Mensaje": "Nutriente no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    nutriente_schema = NutrienteSchema()
    try:
        data = nutriente_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    nombre = data["nombre"]

    #Se busca nutriente con parámetros iguales
    nutriente_repetido = (
        Nutriente.query.filter(Nutriente.nombre == nombre).filter(Nutriente.id != nutrientes_id).filter(Nutriente.activo==True)
        .one_or_none()
    )

    if(nutriente_repetido is not None and nutriente_repetido.id != nutrientes_id):
        return {"Mensaje": "Ya existe otro nutriente con el mismo nombre"}, 404
    else:
        nutriente_actualizar.nombre = nombre
        nutriente_actualizar.abreviatura = data["abreviatura"]
        nutriente_actualizar.fecha_modificacion=dt.now()

        db.session.merge(nutriente_actualizar)
        db.session.commit()

        return {"Mensaje": "Se actualizó nutriente"}

#Servicio para eliminar un nutriente mediante ID
@app.route('/nutrientes/<nutrientes_id>/delete', methods=['GET'])
def nutriente_eliminar(nutrientes_id):

    #Se busca usuario en base de datos
    nutriente_eliminar = (
        Nutriente.query.filter(Nutriente.id == nutrientes_id).filter(Nutriente.activo==True)
        .one_or_none()
    )

    if nutriente_eliminar is None:
        return {"Mensaje": "Nutriente no existe"}, 404
    else:
        nutriente_eliminar.activo=False
        db.session.merge(nutriente_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó nutriente "}