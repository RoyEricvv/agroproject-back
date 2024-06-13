from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Especie import Especie, EspecieSchema
from marshmallow import ValidationError

# Servicios de Especie


#Servicio para listar todos las especies
@app.route('/especies', methods=['GET'])
def especie_listar_todos():
    #Se crea la lista de especies.
    especies = Especie.query.filter(Especie.activo==True).order_by(Especie.nombre).all()

    #Se serializa la información a retornar
    especies_schema = EspecieSchema(many=True)
    data = especies_schema.dump(especies)
 
    return {"Mensaje": "Lista de especies", "especies": data}

#Servicio para listar una especie por id
@app.route('/especies/<especies_id>', methods=['GET'])
def especie_listar_uno(especies_id):
    #Se busca el usuario
    especie = Especie.query.filter(Especie.activo==True).filter(Especie.id == especies_id).one_or_none()

    #Se encontró la especie
    if especie is not None:

        # Se serializa la información a retornar
        especie_schema = EspecieSchema()
        data = especie_schema.dump(especie)
        return {"Mensaje": "Especie encontrada", "especie": data}

    # No se encontró el usuario
    else:
        return {"Mensaje": "No se encontró la especie", "especieId": especies_id},404

#Servicio para crear una especie
@app.route('/especies', methods=['POST'])
def especie_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    especie_schema = EspecieSchema()
    
    try:
        data = especie_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    nombre = data["nombre"]

    #Se busca especie repetido en base de datos
    especie_existente = (
        Especie.query.filter(Especie.nombre == nombre).filter(Especie.activo==True)
        .one_or_none()
    )

    if especie_existente is None:

        if nombre:
            especie_nuevo = Especie(
                activo=True,
                nombre=nombre,
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            db.session.add(especie_nuevo)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

            return {"Mensaje": "Se creo especie"}
    # La especie ya existe
    else:
        return {"Mensaje": "Especie ya existe", "especie": nombre}, 401

#Servicio para actualizar una especie mediante ID
@app.route('/especies/<especies_id>', methods=['POST'])
def especie_actualizar(especies_id):

    #Se busca especie en base de datos
    especie_actualizar = (
        Especie.query.filter(Especie.id == especies_id).filter(Especie.activo==True)
        .one_or_none()
    )

    if especie_actualizar is None:
        return {"Mensaje": "Usuario no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    especie_schema = EspecieSchema()
    try:
        data = especie_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    nombre = data["nombre"]

    #Se busca especie con parámetros iguales
    especie_repetido = (
        Especie.query.filter(Especie.nombre == nombre).filter(Especie.activo==True)
        .one_or_none()
    )

    if(especie_repetido is not None and especie_repetido.id != especies_id):
        return {"Mensaje": "Ya existe otra especie con el mismo nombre"}, 404
    else:
        especie_actualizar.nombre = nombre
        especie_actualizar.fecha_modificacion = dt.now()

        db.session.merge(especie_actualizar)
        db.session.commit()

        return {"Mensaje": "Se actualizó especie"}

#Servicio para eliminar una especie mediante ID
@app.route('/especies/<especies_id>/delete', methods=['GET'])
def especie_eliminar(especies_id):

    #Se busca especie en base de datos
    especie_eliminar = (
        Especie.query.filter(Especie.id == especies_id).filter(Especie.activo==True)
        .one_or_none()
    )

    if especie_eliminar is None:
        return {"Mensaje": "Especie no existe"}, 404
    else:
        especie_eliminar.activo=False
        db.session.merge(especie_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó especie "}