from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from sqlalchemy.sql.expression import false
from aplicacion import db
from aplicacion.modelo.Inventario import Inventario, InventarioSchema
from aplicacion.modelo.Usuario import Usuario
from aplicacion.modelo.Insumo import Insumo
from aplicacion.modelo.RacionFormulada import RacionFormulada
from aplicacion.modelo.ContenidoRacion import ContenidoRacion
from aplicacion.modelo.Restriccion import Restriccion
from marshmallow import ValidationError

# Servicios de Inventario


#Servicio para listar todo el invertario por usuario
@app.route('/inventarios/<usuario_id>/all', methods=['GET'])
def inventario_listar_todos(usuario_id):
    if usuario_id == '0':
        #Se crea la lista de inventarios.
        inventarios = Inventario.query.filter(Inventario.activo==True).order_by(Inventario.insumo_id).all()
    else:
        inventarios = Inventario.query.join(Insumo).filter(Inventario.activo==True).filter(Inventario.usuario_id == usuario_id).order_by(Insumo.nombre).all()

    if len(inventarios) > 0:
        #Se serializa la información a retornar
        print(inventarios[0])
        inventario_schema = InventarioSchema(many=True)
        data = inventario_schema.dump(inventarios)
    
        return {"Mensaje": "Se lista las inventarios", "inventarios": data}
    else:
        return {"Mensaje": "No se encontró el inventario", "usuario_id": usuario_id}, 404

#Servicio para listar todo el invertario por usuario
@app.route('/inventarios/disponible/<usuario_id>/<especie_id>/<etapa_vida_id>', methods=['GET'])
def inventario_listar_por_etapas(usuario_id,especie_id, etapa_vida_id):
    if usuario_id == '0':
        #Se crea la lista de inventarios.
        inventarios = Inventario.query.filter(Inventario.activo==True).order_by(Inventario.insumo_id).all()
    else:
        restricciones = Restriccion.query.filter(Restriccion.activo==True).filter(Restriccion.etapa_vida_id == etapa_vida_id).filter(Restriccion.especie_id == especie_id).filter(Restriccion.porcentaje_permitido > 0 ).all()
        if len(restricciones) == 0:
            return {"Mensaje": "No se encontró insumo adecuado para la formulación de ración", "especie_id": especie_id}, 404
        
        insumos_id = []
        for r in restricciones:
            insumos_id.append(r.insumo_id)
        inventarios = Inventario.query.join(Insumo).filter(Inventario.activo==True).filter(Inventario.usuario_id == usuario_id).filter(Inventario.insumo_id.in_(insumos_id)).order_by(Insumo.nombre).all()

    if len(inventarios) > 0:
        #Se serializa la información a retornar
        print(inventarios[0])
        inventario_schema = InventarioSchema(many=True)
        data = inventario_schema.dump(inventarios)
    
        return {"Mensaje": "Se lista el inventarios", "inventarios": data}
    else:
        return {"Mensaje": "No se encontró el inventario", "usuario_id": usuario_id}, 404

#Servicio para listar todo el invertario que no es aditivo
@app.route('/inventarios/<usuario_id>/insumo', methods=['GET'])
def inventario_listar_todos_insumo(usuario_id):
    if usuario_id == '0':
        #Se crea la lista de inventarios.
        inventarios = Inventario.query.join(Insumo).filter(Insumo.activo==True).filter(Inventario.activo==True).filter(Insumo.es_aditivo == False).order_by(Inventario.insumo_id).all()
    else:
        inventarios = Inventario.query.join(Insumo).filter(Insumo.activo==True).filter(Inventario.activo==True).filter(Inventario.usuario_id == usuario_id).filter(Insumo.es_aditivo == False).order_by(Inventario.insumo_id).all()

    if len(inventarios) > 0:
        #Se serializa la información a retornar
        print(inventarios[0])
        inventario_schema = InventarioSchema(many=True)
        data = inventario_schema.dump(inventarios)
    
        return {"Mensaje": "Se lista las inventarios", "inventarios": data}
    else:
        return {"Mensaje": "No se encontró el inventario", "usuario_id": usuario_id}, 404

#Servicio para devolver una inventario por usuario_id
'''
@app.route('/inventarios/<inventario_id>', methods=['GET'])
def inventario_listar_uno(inventario_id):
    #Se busca la inventario
    inventario = Inventario.query.filter(Inventario.id == inventario_id).one_or_none()

    #Se encontró la inventario
    if inventario is not None:

        print(inventario)
        # Se serializa la información a retornar
        inventario_schema = InventarioSchema()
        data = inventario_schema.dump(inventario)
        return {"Mensaje": "Se encontró el inventario", "inventario": data}

    # No se encontró el usuario
    else:
        return {"Mensaje": "No se encontró el inventario", "usernameId": inventario_id},404
'''
#Servicio para crear una inventario
@app.route('/inventarios', methods=['POST'])
def inventario_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    inventario_schema = InventarioSchema()
    
    try:
        data = inventario_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    
    usuario_id = data["usuario_id"]
    insumo_id = data["insumo_id"]
    peso_total = data["peso_total"]
    costo_total = data["costo_total"]
    costo_unitario = data["costo_unitario"]

    registro_inactivo_existe = Inventario.query.filter(Inventario.activo==False).filter(Inventario.usuario_id == usuario_id).filter(Inventario.insumo_id == insumo_id).one_or_none()
    if registro_inactivo_existe is not None:
        db.session.delete(registro_inactivo_existe)
        db.session.commit()
    
    usuario_existe = Usuario.query.get(usuario_id)

    if usuario_existe is None:
        return {"Mensaje": "El id del usuario no se encuentra registrado"}, 400

    insumo_existe = Insumo.query.get(insumo_id)

    if insumo_existe is None:
        return {"Mensaje": "El id del insumo no se encuentra registrado"}, 400

    registro_existe = Inventario.query.filter(Inventario.activo==True).filter(Inventario.usuario_id == usuario_id).filter(Inventario.insumo_id == insumo_id).one_or_none()
    if registro_existe is not None:
        return {"Mensaje": "Ya existe un registro con la misma información"}, 401

    inventario_nuevo = Inventario(
        activo=True,
        peso_total=peso_total,
        costo_total=costo_total,
        costo_unitario=costo_unitario,
        usuario_id=usuario_id,
        insumo_id=insumo_id,
        fecha_creacion=dt.now(),
        fecha_modificacion=dt.now()
    )
    db.session.add(inventario_nuevo)  # Añade un nuevo registro a la base de datos
    db.session.commit()  # Guarda todos los cambios

    return {"Mensaje": "Se creo inventario"}




#Servicio para actualizar una inventario mediante ID
@app.route('/inventarios/update', methods=['POST'])
def inventario_actualizar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca inventario en base de datos
    inventario_actualizar = (
        Inventario.query.filter(Inventario.usuario_id == json_data["usuario_id"]).filter(Inventario.insumo_id == json_data["insumo_id"]).filter(Inventario.activo==True)
        .one_or_none()
    )

    if inventario_actualizar is None:
        return {"Mensaje": "Inventario no existe"}, 404
    

    inventario_schema = InventarioSchema()
    try:
        data = inventario_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    usuario_id = data["usuario_id"]
    insumo_id = data["insumo_id"]
    peso_total = data["peso_total"]
    costo_total = data["costo_total"]
    costo_unitario = data["costo_unitario"]

    usuario_existe = Usuario.query.get(usuario_id)

    if usuario_existe is None:
        return {"Mensaje": "El id del usuario no se encuentra registrado"}, 400

    insumo_existe = Insumo.query.get(insumo_id)

    if insumo_existe is None:
        return {"Mensaje": "El id del insumo no se encuentra registrado"}, 400

    inventario_actualizar.peso_total = peso_total
    inventario_actualizar.costo_total = round(peso_total * costo_unitario,2)
    inventario_actualizar.costo_unitario = costo_unitario
    inventario_actualizar.fecha_modificacion = dt.now()

    db.session.commit()

    costo_previo=int(inventario_actualizar.costo_unitario * 100)
    costo_actual=int(data["costo_unitario"]*100)

    if costo_previo!=costo_actual:
        raciones=RacionFormulada.query.join(ContenidoRacion).filter(ContenidoRacion.activo==True).filter(RacionFormulada.activo==True).filter(ContenidoRacion.insumo_id == insumo_id).filter(RacionFormulada.usuario_id == usuario_id).filter(RacionFormulada.aplicar == True).all()
        if len(raciones)>0:
            for item in raciones:
                item.aplicar=False
                db.session.merge(item)
                db.session.commit()

    return {"Mensaje": "Se actualizó inventario."}

#Servicio para eliminar una inventario mediante ID
@app.route('/inventarios/delete', methods=['POST'])
def inventario_eliminar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca inventario en base de datos
    inventario_eliminar = (
        Inventario.query.filter(Inventario.usuario_id == json_data["usuario_id"]).filter(Inventario.insumo_id == json_data["insumo_id"]).filter(Inventario.activo==True)
        .one_or_none()
    )

    if inventario_eliminar is None:
        return {"Mensaje": "Inventario no existe"}, 404
    else:
        inventario_eliminar.activo=False
        db.session.merge(inventario_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó inventario"}