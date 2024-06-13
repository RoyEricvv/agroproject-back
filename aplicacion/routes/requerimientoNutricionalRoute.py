from typing import Awaitable
from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from sqlalchemy.sql.expression import true
from aplicacion import db
from aplicacion.modelo.RequerimientoNutricional import RequerimientoNutricional, RequerimientoNutricionalSchema
from aplicacion.modelo.Nutriente import Nutriente
from aplicacion.modelo.EtapaVida import EtapaVida
from aplicacion.modelo.Departamento import Departamento
from aplicacion.modelo.Fuente import Fuente
from marshmallow import ValidationError

# Servicios de requerimiento nutricional


#Servicio para listar todos las contenido Nutricionales
@app.route('/requerimientoNutricionales/all', methods=['POST'])
def requerimiento_nutricional_listar_todos():
    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    #Se crea la lista de requerimientoNutricionales.
    requerimiento_nutricionales = (
        RequerimientoNutricional.query.join(Nutriente).filter(RequerimientoNutricional.etapa_vida_id == json_data["etapa_vida_id"])
        .filter(RequerimientoNutricional.activo==True)
        .filter(RequerimientoNutricional.departamento_id == json_data["departamento_id"])
        .filter(RequerimientoNutricional.fuente_id == json_data["fuente_id"])
        .order_by(Nutriente.nombre).all()
        )

    #Se serializa la información a retornar
    requerimiento_nutricional_schema = RequerimientoNutricionalSchema(many=True)
    data = requerimiento_nutricional_schema.dump(requerimiento_nutricionales)
 
    return {"Mensaje": "Se lista las requerimiento Nutricionales", "requerimientoNutricionales": data}

#Servicio para devolver una requerimiento nutricional por usuario_id
'''
@app.route('/requerimientoNutricionales/<caracteristica_especie_id>', methods=['GET'])
def requerimiento_nutricional_listar_uno(caracteristica_especie_id):
    #Se busca la requerimiento nutricional
    requerimiento_nutricional = RequerimientoNutricional.query.filter(RequerimientoNutricional.id == caracteristica_especie_id).one_or_none()

    #Se encontró la requerimiento nutricional
    if requerimiento_nutricional is not None:
        print(requerimiento_nutricional)
        # Se serializa la información a retornar
        requerimiento_nutricional_schema = RequerimientoNutricionalSchema()
        data = requerimiento_nutricional_schema.dump(requerimiento_nutricional)
        return {"Mensaje": "Se encontró el requerimiento nutricional", "contenidoNutricional": data}

    # No se encontró el usuario
    else:
        return {"Mensaje": "No se encontró el requerimiento nutricional", "caracteristica_especie_id": caracteristica_especie_id},404
'''

#Servicio para crear una requerimiento nutricional
@app.route('/requerimientoNutricionales', methods=['POST'])
def requerimiento_nutricional_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400   

    cantidad = json_data["cantidad"]
    tipo_requerimiento = json_data ["tipo_requerimiento"]
    nutriente_id = json_data["nutriente_id"]
    etapa_vida_id = json_data["etapa_vida_id"]
    departamento_id = json_data["departamento_id"]
    fuente_id = json_data["fuente_id"]
    esencial = json_data["esencial"]
    se_repite = json_data["se_repite"]

    fuente_existe = Fuente.query.get(fuente_id)

    if fuente_existe is None:
        return {"Mensaje": "El id de la fuente no se encuentra registrado"}, 400

    nutriente_existe = Nutriente.query.get(nutriente_id)

    if nutriente_existe is None:
        return {"Mensaje": "El id del nutriente no se encuentra registrado"}, 400

    etapa_vida_existe = EtapaVida.query.get(etapa_vida_id)

    if etapa_vida_existe is None:
        return {"Mensaje": "El id de la caracteristica especie no se encuentra registrada"}, 400

    departamento_existe = Departamento.query.filter(Departamento.id == departamento_id).one_or_none()

    if departamento_existe is None:
        return {"Mensaje": "El id del departamento no se encuentra registrada"}, 400

    if se_repite:
        lista_dep = Departamento.query.filter(Departamento.activo==True).order_by(Departamento.id).all()
        for dep in lista_dep:
            registro_inactivo_existe = (
                RequerimientoNutricional.query.filter(RequerimientoNutricional.etapa_vida_id == etapa_vida_id)
                .filter(RequerimientoNutricional.activo==False)
                .filter(RequerimientoNutricional.nutriente_id == nutriente_id)
                .filter(RequerimientoNutricional.fuente_id == fuente_id)
                .filter(RequerimientoNutricional.departamento_id == dep.id)
                .one_or_none()
            )

            if registro_inactivo_existe is not None:
                db.session.delete(registro_inactivo_existe)
                db.session.commit()

            registro_existe = (
                RequerimientoNutricional.query.filter(RequerimientoNutricional.etapa_vida_id == etapa_vida_id)
                .filter(RequerimientoNutricional.activo==True)
                .filter(RequerimientoNutricional.nutriente_id == nutriente_id)
                .filter(RequerimientoNutricional.fuente_id == fuente_id)
                .filter(RequerimientoNutricional.departamento_id == dep.id)
                .one_or_none()
            )

            if registro_existe is not None:
                continue
            
            requerimiento_nutricional_nuevo = RequerimientoNutricional(
                esencial=esencial,
                activo=True,
                cantidad=cantidad,
                tipo_requerimiento=tipo_requerimiento,
                nutriente_id=nutriente_id,
                etapa_vida_id=etapa_vida_id,
                departamento_id=dep.id,
                fuente_id=fuente_id,
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            db.session.add(requerimiento_nutricional_nuevo)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

        return {"Mensaje": "Se creo requerimiento nutricional"}

    else:
        registro_inactivo_existe = (
            RequerimientoNutricional.query.filter(RequerimientoNutricional.etapa_vida_id == etapa_vida_id)
            .filter(RequerimientoNutricional.activo==False)
            .filter(RequerimientoNutricional.nutriente_id == nutriente_id)
            .filter(RequerimientoNutricional.fuente_id == fuente_id)
            .filter(RequerimientoNutricional.departamento_id == departamento_id)
            .one_or_none()
        )

        if registro_inactivo_existe is not None:
            db.session.delete(registro_inactivo_existe)
            db.session.commit()
    
        registro_existe = (
            RequerimientoNutricional.query.filter(RequerimientoNutricional.etapa_vida_id == etapa_vida_id)
            .filter(RequerimientoNutricional.activo==True)
            .filter(RequerimientoNutricional.nutriente_id == nutriente_id)
            .filter(RequerimientoNutricional.fuente_id == fuente_id)
            .filter(RequerimientoNutricional.departamento_id == departamento_id)
            .one_or_none()
        )

        if registro_existe is not None:
            return {"Mensaje": "Ya existe un registro con la misma información"}, 401

        requerimiento_nutricional_nuevo = RequerimientoNutricional(
            esencial=esencial,
            activo=True,
            cantidad=cantidad,
            tipo_requerimiento=tipo_requerimiento,
            nutriente_id=nutriente_id,
            etapa_vida_id=etapa_vida_id,
            departamento_id=departamento_id,
            fuente_id=fuente_id,
            fecha_creacion=dt.now(),
            fecha_modificacion=dt.now()
        )
        db.session.add(requerimiento_nutricional_nuevo)  # Añade un nuevo registro a la base de datos
        db.session.commit()  # Guarda todos los cambios

        return {"Mensaje": "Se creo requerimiento nutricional"}


#Servicio para actualizar una requerimiento nutricional mediante ID
@app.route('/requerimientoNutricionales/update', methods=['POST'])
def requerimiento_nutricional_actualizar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca requerimiento nutricional en base de datos
    requerimiento_nutricional_actualizar = (
        RequerimientoNutricional.query.filter(RequerimientoNutricional.etapa_vida_id == json_data["etapa_vida_id"])
        .filter(RequerimientoNutricional.activo==True)
        .filter(RequerimientoNutricional.nutriente_id == json_data["nutriente_id"])
        .filter(RequerimientoNutricional.fuente_id == json_data["fuente_id"])
        .filter(RequerimientoNutricional.departamento_id == json_data["departamento_id"])
        .one_or_none()
    )

    if requerimiento_nutricional_actualizar is None:
        return {"Mensaje": "RequerimientoNutricional no existe"}, 404

    requerimiento_nutricional_schema = RequerimientoNutricionalSchema()
    try:
        data = requerimiento_nutricional_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    cantidad = data["cantidad"]
    tipo_requerimiento = data ["tipo_requerimiento"]
    nutriente_id = data["nutriente_id"]
    etapa_vida_id = data["etapa_vida_id"]
    esencial = json_data["esencial"]
    departamento_id = data["departamento_id"]
    fuente_id = data["fuente_id"]

    nutriente_existe = Nutriente.query.get(nutriente_id)

    if nutriente_existe is None:
        return {"Mensaje": "El id del nutriente no se encuentra registrado"}, 400

    etapa_vida_existe = EtapaVida.query.get(etapa_vida_id)

    if etapa_vida_existe is None:
        return {"Mensaje": "El id de la caracteristica especie no se encuentra registrada"}, 400


    requerimiento_nutricional_actualizar.cantidad = cantidad
    requerimiento_nutricional_actualizar.esencial = esencial
    requerimiento_nutricional_actualizar.tipo_requerimiento = tipo_requerimiento
    requerimiento_nutricional_actualizar.fecha_modificacion = dt.now()
    
    db.session.merge(requerimiento_nutricional_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó requerimiento nutricional."}

#Servicio para eliminar una requerimiento nutricional mediante ID
@app.route('/requerimientoNutricionales/delete', methods=['POST'])
def requerimiento_nutricional_eliminar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca requerimiento nutricional en base de datos
    requerimiento_nutricional_eliminar = (
        RequerimientoNutricional.query.filter(RequerimientoNutricional.etapa_vida_id == json_data["etapa_vida_id"])
        .filter(RequerimientoNutricional.activo==True)
        .filter(RequerimientoNutricional.nutriente_id == json_data["nutriente_id"])
        .filter(RequerimientoNutricional.fuente_id == json_data["fuente_id"])
        .filter(RequerimientoNutricional.departamento_id == json_data["departamento_id"])
        .one_or_none()
    )

    if requerimiento_nutricional_eliminar is None:
        return {"Mensaje": "requerimiento nutricional no existe"}, 404
    else:
        requerimiento_nutricional_eliminar.activo=False
        db.session.merge(requerimiento_nutricional_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó requerimiento nutricional"}