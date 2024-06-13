from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Usuario import Usuario, UsuarioSchema
from aplicacion.modelo.Perfil import Perfil
from marshmallow import ValidationError
# Servicios de Usuario


#Servicio para listar todos los usuarios
@app.route('/usuarios', methods=['GET'])
def usuario_listar_todos():
    #Se crea la lista de usuarios.
    usuarios = Usuario.query.order_by(Usuario.id).all()

    #Se serializa la información a retornar
    usuario_schema = UsuarioSchema(many=True)
    data = usuario_schema.dump(usuarios)
 
    return {"Mensaje": "Lista de usuarios", "usuarios": data}

#Servicio para listar un usario por USERNAME
@app.route('/usuarios/<username>', methods=['GET'])
def usuario_listar_uno(username):
    #Se busca el usuario
    usuario = Usuario.query.filter(Usuario.activo==True).filter(Usuario.username == username).one_or_none()

    #Se encontró el usuario
    if usuario is not None:

        print(usuario)
        # Se serializa la información a retornar
        usuario_schema = UsuarioSchema()
        data = usuario_schema.dump(usuario)
        return {"Mensaje": "Usuario encontrado", "usuario": data}

    # No se encontró el usuario
    else:
        return {"Mensaje": "No se encontró el usuario", "username": username},404

#Servicio para crear un usuario
@app.route('/usuarios', methods=['POST'])
def usuario_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    usuario_schema = UsuarioSchema()
    
    try:
        data = usuario_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    username = data["username"]
    correo = ""
    password = data["password"]
    nombres = data["nombres"]
    apellidos = data["apellidos"]
    perfil_id = data["perfil_id"]

    perfil_existe = Perfil.query.filter(Perfil.id == perfil_id).one_or_none()
    if perfil_existe is None:
        return {"Mensaje": "El id del perfil no existe"}, 400

    #Se busca usuario repetido en base de datos
    usuario_existente = (
        Usuario.query.filter(Usuario.username == username).filter(Usuario.activo==True)
        #.filter(Usuario.correo == correo)
        .one_or_none()
    )

    if usuario_existente is None:

        if username and password:
            usuario_nuevo = Usuario(
                activo=True,
                username=username,
                nombres=nombres,
                apellidos=apellidos,
                password=password,
                perfil_id=perfil_id,
                correo=correo,
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            db.session.add(usuario_nuevo)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

            return {"Mensaje": "Se creo usuario"}
    # El usuario ya existe
    else:
        return {"Mensaje": "Usuario ya existe", "username": username}, 401

#Servicio para actualizar un usuario mediante ID
@app.route('/usuarios/<username_id>', methods=['POST'])
def usuario_actualizar(username_id):

    #Se busca usuario en base de datos
    usuario_actualizar = (
        Usuario.query.filter(Usuario.id == username_id)
        .one_or_none()
    )

    if usuario_actualizar is None:
        return {"Mensaje": "Usuario no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    usuario_schema = UsuarioSchema()
    try:
        data = usuario_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    username = data["username"]
    correo = ""
    nombres = data["nombres"]
    apellidos = data["apellidos"]
    perfil_id = data["perfil_id"]

    #Se busca usuario con parámetros iguales
    usuario_repetido = (
        Usuario.query.filter(Usuario.username == username)
        #.filter(Usuario.correo == correo)
        .one_or_none()
    )

    if(usuario_repetido is not None and usuario_repetido.id != username_id):
        return {"Mensaje": "Ya existe otro usuario con el mismo username e email"}, 404
    else:
        usuario_actualizar.username = username
        usuario_actualizar.correo = correo
        usuario_actualizar.nombres = nombres
        usuario_actualizar.apellidos = apellidos
        usuario_actualizar.perfil_id = perfil_id
        usuario_actualizar.fecha_modificacion = dt.now()

        db.session.merge(usuario_actualizar)
        db.session.commit()

        return {"Mensaje": "Se actualizó usuario "}

#Servicio para eliminar un usuario mediante ID
@app.route('/usuarios/<username_id>/delete', methods=['GET'])
def usuario_eliminar(username_id):

    #Se busca usuario en base de datos
    usuario_eliminar = (
        Usuario.query.filter(Usuario.id == username_id)
        .one_or_none()
    )

    if usuario_actualizar is None:
        return {"Mensaje": "Usuario no existe"}, 404
    else:
        usuario_eliminar.activo=not usuario_eliminar.activo
        db.session.merge(usuario_eliminar)
        db.session.commit()

        return {"Mensaje": "Se actualizó usuario "}

#Servicios de Logeo

#Servicio para verificar usuario
@app.route('/login', methods=['post'])
def login():

    json_data = request.get_json()
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400
    
    username = json_data["username"]
    password = json_data["password"]
    #Se busca el usuario
    autenticar = Usuario.query.filter(Usuario.activo==True).filter(Usuario.username == username, Usuario.password == password).one_or_none()
    if autenticar is None:
        return {"Mensaje": "Usuario no existe"}, 404
    else:
        usuario_schema = UsuarioSchema(exclude=['password'])
        data = usuario_schema.dump(autenticar)
        return {"Mensaje": "Se encontró el usuario", "usuario": data}