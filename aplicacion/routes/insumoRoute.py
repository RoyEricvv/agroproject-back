from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Insumo import Insumo, InsumoSchema
from aplicacion.modelo.Departamento import Departamento
from aplicacion.modelo.MateriaSeca import MateriaSeca
from marshmallow import ValidationError

# Servicios de Insumo


#Servicio para listar todos los insumos
@app.route('/insumos', methods=['GET'])
def insumo_listar_todos():
    #Se crea la lista de usuarios.
    insumos = Insumo.query.filter(Insumo.activo==True).order_by(Insumo.nombre).all()

    #Se serializa la información a retornar
    insumos_schema = InsumoSchema(many=True)
    data = insumos_schema.dump(insumos)
 
    return {"Mensaje": "Lista de insumos", "insumos": data}

#Servicio para listar todos los insumos no aditivos
@app.route('/insumos/NoAditivo', methods=['GET'])
def insumo_listar_todos_no_aditivos():
    #Se crea la lista de usuarios.
    insumos = Insumo.query.filter(Insumo.activo==True).filter(Insumo.es_aditivo == False).order_by(Insumo.id).all()

    #Se serializa la información a retornar
    insumos_schema = InsumoSchema(many=True)
    data = insumos_schema.dump(insumos)
 
    return {"Mensaje": "Lista de insumos", "insumos": data}

#Servicio para listar una insumos por id
@app.route('/insumos/<insumos_id>', methods=['GET'])
def insumo_listar_uno(insumos_id):
    #Se busca el usuario
    insumo = Insumo.query.filter(Insumo.activo==True).filter(Insumo.id == insumos_id).one_or_none()

    #Se encontró el insumos
    if insumo is not None:

        # Se serializa la información a retornar
        insumo_schema = InsumoSchema()
        data = insumo_schema.dump(insumo)
        return {"Mensaje": "Insumo encontrada", "insumo": data}

    # No se encontró el insumos
    else:
        return {"Mensaje": "No se encontró el insumo", "insumoId": insumos_id},404

#Servicio para crear un insumo
@app.route('/insumos', methods=['POST'])
def insumo_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400    

    nombre = json_data["nombre"]
    materia_seca = json_data["materia_seca"]
    es_aditivo = json_data["es_aditivo"]
    
    #Se busca usuario repetido en base de datos
    insumo_existente = (
        Insumo.query.filter(Insumo.nombre == nombre).filter(Insumo.activo==True)
        .one_or_none()
    )

    departamentos = Departamento.query.order_by(Departamento.id).all()

    if insumo_existente is None:

        if nombre:
            insumo_nuevo = Insumo(
                activo=True,
                nombre=nombre,
                es_aditivo=es_aditivo,
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            db.session.add(insumo_nuevo)  # Añade un nuevo registro a la base de datos
            db.session.flush()
            db.session.commit()  # Guarda todos los cambios


            if departamentos is not None and not es_aditivo:
                for dep in departamentos:
                    materia_nuevo = MateriaSeca(activo=True,porcentaje=materia_seca, insumo_id=insumo_nuevo.id, departamento_id=dep.id,fecha_creacion=dt.now(),fecha_modificacion=dt.now())
                    db.session.add(materia_nuevo)
                    db.session.commit()

            return {"Mensaje": "Se creo insumo", "insumoId":insumo_nuevo.id}
    # El usuario ya existe
    else:
        return {"Mensaje": "Insumo ya existe", "insumo": nombre}, 401

#Servicio para actualizar un insumo mediante ID
@app.route('/insumos/<insumos_id>', methods=['POST'])
def insumo_actualizar(insumos_id):

    #Se busca usuario en base de datos
    insumo_actualizar = (
        Insumo.query.filter(Insumo.id == insumos_id).filter(Insumo.activo==True)
        .one_or_none()
    )

    if insumo_actualizar is None:
        return {"Mensaje": "Insumo no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    insumo_schema = InsumoSchema()
    try:
        data = insumo_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    nombre = data["nombre"]

    #Se busca usuario con parámetros iguales
    insumo_repetido = (
        Insumo.query.filter(Insumo.nombre == nombre).filter(Insumo.activo==True)
        .one_or_none()
    )

    if(insumo_repetido is not None and insumo_repetido.id != insumos_id):
        return {"Mensaje": "Ya existe otro insumo con el mismo nombre"}, 404
    else:
        insumo_actualizar.nombre = nombre
        insumo_actualizar.fecha_modificacion = dt.now()

        db.session.merge(insumo_actualizar)
        db.session.commit()

        return {"Mensaje": "Se actualizó insumo"}

#Servicio para eliminar una insumo mediante ID
@app.route('/insumos/<insumos_id>/delete', methods=['GET'])
def insumo_eliminar(insumos_id):

    #Se busca usuario en base de datos
    insumo_eliminar = (
        Insumo.query.filter(Insumo.id == insumos_id).filter(Insumo.activo==True)
        .one_or_none()
    )

    if insumo_eliminar is None:
        return {"Mensaje": "Insumo no existe"}, 404
    else:
        insumo_eliminar.activo=False
        db.session.merge(insumo_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó insumo "}