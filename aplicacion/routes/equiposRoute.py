from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Equipo import Equipo, Granja, EquipoSchema
from marshmallow import ValidationError


# Servicio para listar todos los equipos de una granja
@app.route('/equipos/<granja_id>/allGranja', methods=['GET'])
def equipo_listar_todos_granja(granja_id):
    if granja_id == '0':
        equipos = Equipo.query.filter(Equipo.estado_equipo == True).order_by(Equipo.nombre).all()
    else:
        equipos = Equipo.query.filter_by(granja_id=granja_id, estado_equipo=True).order_by(Equipo.id).all()
    
    if equipos:
        equipos_schema = EquipoSchema(many=True)
        data = equipos_schema.dump(equipos)
        return {"Mensaje": "Lista de equipos", "equipos": data}
    else:
        return {"Mensaje": "No se encontraron equipos para la granja especificada", "granjaId": granja_id}, 404

#Listar todos los equipos de un usuario
@app.route('/equipos/<usuario_id>/<tipo>/all', methods=['GET'])
def equipo_listar_todos_usuario(usuario_id, tipo):
    if usuario_id == '0':
        equipos = Equipo.query.filter(Equipo.estado_equipo == True).order_by(Equipo.id).all()
    else:
        print("vuamos")
        if tipo == '1':  # Listar equipos no contabilizados
            equipos = Equipo.query.join(Granja).filter(Granja.usuario_id == usuario_id, Equipo.estado_equipo == True, Equipo.estado_equipo != 3).order_by(Equipo.id).all()
        else:
            equipos = Equipo.query.join(Granja).filter(Granja.usuario_id == usuario_id, Equipo.estado_equipo == True).order_by(Equipo.id).all()
    
    if equipos:
        equipos_schema = EquipoSchema(many=True)
        data = equipos_schema.dump(equipos)
        return {"Mensaje": "Lista de equipos", "equipos": data}
    else:
        return {"Mensaje": "No se encontraron equipos para el usuario especificado", "usuarioId": usuario_id}, 404

    

# #Servicio para listar todos los animales de un usuario
# @app.route('/animales/<usuario_id>/<tipo>/allAnimales', methods=['GET'])
# def animal_listar_todos_usuario(usuario_id,tipo):
#     if usuario_id == '0':
#         #Se crea la lista de todos los animales.
#         animales = Animal.query.filter(Animal.activo==True).order_by(Animal.id).all()
#     else:
#         #Se crea la lista de los animales de una granja.
#         if tipo == 1: #Listar animales no contabilizados
#             animales = Animal.query.join(Granja).filter(Granja.usuario_id == usuario_id).filter(Animal.activo==True).filter(Animal.estado_animal!=3).order_by(Animal.id).all()
#         else:
#             animales = Animal.query.join(Granja).filter(Granja.usuario_id == usuario_id).filter(Animal.activo==True).order_by(Animal.id).all()
#         print(animales)
#     if len(animales) > 0:
#         #Se serializa la información a retornar
#         animales_schema = AnimalSchema(many=True)
#         data = animales_schema.dump(animales)
    
#         return {"Mensaje": "Lista de animales", "animales": data}
#     else:
#         return {"Mensaje": "No se encontró animales", "usuarioId": usuario_id},404
    
#Obtener un equipo por su ID
@app.route('/equipos/<equipo_id>', methods=['GET'])
def equipo_obtener_por_id(equipo_id):
    equipo = Equipo.query.filter_by(id=equipo_id, estado_equipo=True).one_or_none()

    if equipo:
        equipo_schema = EquipoSchema()
        data = equipo_schema.dump(equipo)
        return {"Mensaje": "Equipo encontrado", "equipo": data}
    else:
        return {"Mensaje": "No se encontró el equipo", "equipoId": equipo_id}, 404

# Crear un nuevo equipo
@app.route('/equipos', methods=['POST'])
def equipo_crear():
    json_data = request.get_json()
    
    if not json_data:
        return {"Mensaje": "No se envió información"}, 400
    
    equipo_schema = EquipoSchema()
    
    try:
        data = equipo_schema.load(json_data)
    except ValidationError as err:
        return err.messages, 422
    
    nuevo_equipo = Equipo(
        granja_id=data['granja_id'],
        estado_equipo=data.get('estado_equipo', 1),  # Asignar un valor predeterminado si no se proporciona
        nombre=data['nombre'],
        numero_serie=data['numero_serie'],
        precio=data['precio'],
        moneda=data['moneda'],
        comentario=data.get('comentario'),
        documento=data.get('documento'),
        fecha_compra=data.get('fecha_compra'),
        estado=data.get('estado'),
        proveedor=data.get('proveedor'),
        vida_estimada=data.get('vida_estimada'),
        tipo_depreciacion=data.get('tipo_depreciacion'),
        fecha_limite_garantia=data.get('fecha_limite_garantia')
    )
    
    db.session.add(nuevo_equipo)
    db.session.commit()
    
    return {"Mensaje": "Equipo creado exitosamente"}

# Actualizar un equipo por su ID
@app.route('/equipos/<equipo_id>', methods=['PUT'])
def equipo_actualizar(equipo_id):
    equipo = Equipo.query.filter_by(id=equipo_id, estado_equipo=True).one_or_none()

    if not equipo:
        return {"Mensaje": "Equipo no encontrado"}, 404
    
    json_data = request.get_json()
    if not json_data:
        return {"Mensaje": "No se envió información"}, 400
    
    equipo_schema = EquipoSchema()
    try:
        data = equipo_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    
    equipo.nombre = data.get('nombre', equipo.nombre)
    equipo.numero_serie = data.get('numero_serie', equipo.numero_serie)
    equipo.precio = data.get('precio', equipo.precio)
    equipo.moneda = data.get('moneda', equipo.moneda)
    equipo.comentario = data.get('comentario', equipo.comentario)
    equipo.documento = data.get('documento', equipo.documento)
    equipo.fecha_compra = data.get('fecha_compra', equipo.fecha_compra)
    equipo.estado = data.get('estado', equipo.estado)
    equipo.proveedor = data.get('proveedor', equipo.proveedor)
    equipo.vida_estimada = data.get('vida_estimada', equipo.vida_estimada)
    equipo.tipo_depreciacion = data.get('tipo_depreciacion', equipo.tipo_depreciacion)
    equipo.fecha_limite_garantia = data.get('fecha_limite_garantia', equipo.fecha_limite_garantia)
    
    db.session.merge(equipo)
    db.session.commit()
    
    return {"Mensaje": "Equipo actualizado exitosamente"}

# Eliminar un equipo por su ID
@app.route('/equipos/<equipo_id>', methods=['DELETE'])
def equipo_eliminar(equipo_id):
    equipo = Equipo.query.filter_by(id=equipo_id, estado_equipo=True).one_or_none()

    if not equipo:
        return {"Mensaje": "Equipo no encontrado"}, 404
    
    equipo.estado_equipo = False
    db.session.merge(equipo)
    db.session.commit()
    
    return {"Mensaje": "Equipo eliminado exitosamente"}
