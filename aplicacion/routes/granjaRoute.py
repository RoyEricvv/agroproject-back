from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Granja import Granja, GranjaSchema
from aplicacion.modelo.Usuario import Usuario
from aplicacion.modelo.Departamento import Departamento
from marshmallow import ValidationError

# Servicios de Granja

#Servicio para listar todos las granjas
@app.route('/granjas/<usuario_id>/all', methods=['GET'])
def granja_listar_todos(usuario_id):
    if usuario_id == '0':
        #Se crea la lista de granjas.
        granjas = Granja.query.filter(Granja.activo==True).order_by(Granja.id).all()
    else:
        granjas = Granja.query.filter(Granja.activo==True).filter(Granja.usuario_id == usuario_id).order_by(Granja.nombre).all()
    
    if len(granjas) > 0:
        #Se serializa la información a retornar
        granja_schema = GranjaSchema(many=True)
        data = granja_schema.dump(granjas)
    
        return {"Mensaje": "Se lista las granjas", "granjas": data}
    else:
        return {"Mensaje": "No se encontró las granjas", "usernameId": usuario_id}, 404

#Servicio para devolver una granja por usuario_id
'''
@app.route('/granjas/<granja_id>', methods=['GET'])
def granja_listar_uno(granja_id):
    #Se busca la granja
    granja = Granja.query.filter(Granja.id == granja_id).one_or_none()

    #Se encontró la granja
    if granja is not None:

        print(granja)
        # Se serializa la información a retornar
        granja_schema = GranjaSchema()
        data = granja_schema.dump(granja)
        return {"Mensaje": "Se encontró la granja", "granja": data}

    # No se encontró el usuario
    else:
        return {"Mensaje": "No se encontró la granja", "granjaid": granja_id},404
'''
#Servicio para crear una granja
@app.route('/granjas', methods=['POST'])
def granja_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    granja_schema = GranjaSchema()
    
    try:
        data = granja_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    nombre = data["nombre"]
    usuario_id = data["usuario_id"]
    departamento_id = data["departamento_id"]

    usuario_existe = Usuario.query.get(usuario_id)

    if usuario_existe is None:
        return {"Mensaje": "El id del usuario no se encuentra registrado"}, 400


    #Se busca granja repetida en base de datos
    granja_existente = (
        Granja.query.filter(Granja.nombre == nombre)
        .filter(Granja.usuario_id == usuario_id)
        .filter(Granja.departamento_id == departamento_id)
        .filter(Granja.activo==True)
        .one_or_none()
    )

    if granja_existente is None:

        if nombre and usuario_id :
            granja_nuevo = Granja(
                activo=True,
                nombre=nombre,
                usuario_id=usuario_id,
                departamento_id=departamento_id,
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            db.session.add(granja_nuevo)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

            return {"Mensaje": "Se creo granja"}
    # La granja ya existe
    else:
        return {"Mensaje": "El usuario ya cuenta con esa Granja", "nombre": nombre}, 401



#Servicio para actualizar una granja mediante ID
@app.route('/granjas/update', methods=['POST'])
def granja_actualizar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca granja en base de datos
    granja_actualizar = (
        Granja.query.filter(Granja.usuario_id == json_data["usuario_id"]).filter(Granja.departamento_id == json_data["departamento_id"]).filter(Granja.activo==True)
        .one_or_none()
    )

    if granja_actualizar is None:
        return {"Mensaje": "Granja no existe"}, 404


    granja_schema = GranjaSchema()
    try:
        data = granja_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    nombre = data["nombre"]
    usuario_id = data["usuario_id"]
    departamento_id = data["departamento_id"]

    usuario_existe = Usuario.query.get(usuario_id)

    if usuario_existe is None:
        return {"Mensaje": "El id del usuario no se encuentra registrado"}, 404

    #Se busca granja con parámetros iguales
    granja_repetido = (
        Granja.query.filter(Granja.nombre == nombre)
        .filter(Granja.usuario_id == usuario_id)
        .filter(Granja.departamento_id == departamento_id)
        .filter(Granja.activo==True)
        .one_or_none()
    )

    if granja_repetido is not None:
        return {"Mensaje": "Ya existe otra granja con el mismo nombre para el usuario"}, 404
    else:
        granja_actualizar.nombre = nombre
        granja_actualizar.usuario_id = usuario_id
        granja_actualizar.fecha_modificacion = dt.now()

        db.session.merge(granja_actualizar)
        db.session.commit()

        return {"Mensaje": "Se actualizó granja."}

#Servicio para eliminar una granja mediante ID
@app.route('/granjas/delete', methods=['POST'])
def granja_eliminar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca granja en base de datos
    granja_eliminar = (
        Granja.query.filter(Granja.usuario_id == json_data["usuario_id"]).filter(Granja.departamento_id == json_data["departamento_id"]).filter(Granja.activo==True)
        .one_or_none()
    )

    if granja_eliminar is None:
        return {"Mensaje": "Granja no existe"}, 404
    else:
        granja_eliminar.activo=False
        db.session.merge(granja_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó granja"}