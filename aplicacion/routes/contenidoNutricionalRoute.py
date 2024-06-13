from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.ContenidoNutricional import ContenidoNutricional, ContenidoNutricionalSchema
from aplicacion.modelo.Nutriente import Nutriente
from aplicacion.modelo.Insumo import Insumo
from marshmallow import ValidationError

# Servicios de Contenido Nutricional


#Servicio para listar todos las contenido Nutricionales
@app.route('/contenidoNutricionales/<insumo_id>/all', methods=['GET'])
def contenido_nutricional_listar_todos(insumo_id):
    if insumo_id == '0':
        #Se crea la lista de contenidoNutricionales.
        contenido_nutricionales = ContenidoNutricional.query.filter(ContenidoNutricional.activo==True).order_by(ContenidoNutricional.id).all()
    else:
        contenido_nutricionales = ContenidoNutricional.query.join(Nutriente).filter(ContenidoNutricional.insumo_id == insumo_id).filter(ContenidoNutricional.activo==True).order_by(Nutriente.nombre).all()
    
    if len(contenido_nutricionales) > 0:
        #Se serializa la información a retornar
        contenido_nutricional_schema = ContenidoNutricionalSchema(many=True)
        data = contenido_nutricional_schema.dump(contenido_nutricionales)
    
        return {"Mensaje": "Se lista las contenidoNutricionales", "contenidoNutricionales": data}
    else:
        return {"Mensaje": "No se encontró el inventario", "insumoId": insumo_id}, 404

#Servicio para devolver un contenido nutricional 
'''
@app.route('/contenidoNutricionales/<contenidoNutricional_id>', methods=['GET'])
def contenido_nutricional_listar_uno(contenidoNutricional_id):
    #Se busca la contenido nutricional
    contenido_nutricional = ContenidoNutricional.query.filter(ContenidoNutricional.id == contenidoNutricional_id).one_or_none()

    #Se encontró la contenido nutricional
    if contenido_nutricional is not None:

        print(contenido_nutricional)
        # Se serializa la información a retornar
        contenido_nutricional_schema = ContenidoNutricionalSchema()
        data = contenido_nutricional_schema.dump(contenido_nutricional)
        return {"Mensaje": "Se encontró el contenido nutricional", "contenidoNutricional": data}

    # No se encontró el usuario
    else:
        return {"Mensaje": "No se encontró el contenido nutricional", "Id": contenidoNutricional_id},404
'''
#Servicio para crear una contenido nutricional
@app.route('/contenidoNutricionales', methods=['POST'])
def contenido_nutricional_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    contenido_nutricional_schema = ContenidoNutricionalSchema()
    
    try:
        data = contenido_nutricional_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    cantidad = data["cantidad"]
    nutriente_id = data["nutriente_id"]
    insumo_id = data["insumo_id"]

    nutriente_existe = Nutriente.query.get(nutriente_id)

    if nutriente_existe is None:
        return {"Mensaje": "El id del nutriente no se encuentra registrado"}, 400

    insumo_existe = Insumo.query.get(insumo_id)

    if insumo_existe is None:
        return {"Mensaje": "El id del insumo no se encuentra registrado"}, 400

    registro_existe = ContenidoNutricional.query.filter(ContenidoNutricional.nutriente_id == nutriente_id).filter(ContenidoNutricional.insumo_id == insumo_id).filter(ContenidoNutricional.activo==True).one_or_none()

    if registro_existe is not None:
        return {"Mensaje": "Ya existe un registro con la misma información"}, 401

    contenido_nutricional_nuevo = ContenidoNutricional(
        activo=True,
        cantidad=cantidad,
        nutriente_id=nutriente_id,
        insumo_id=insumo_id,
        fecha_creacion=dt.now(),
        fecha_modificacion=dt.now()
    )
    db.session.add(contenido_nutricional_nuevo)  # Añade un nuevo registro a la base de datos
    db.session.commit()  # Guarda todos los cambios

    return {"Mensaje": "Se creo contenido nutricional"}




#Servicio para actualizar una contenido nutricional mediante ID
@app.route('/contenidoNutricionales/update', methods=['POST'])
def contenido_nutricional_actualizar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca contenido nutricional en base de datos
    contenido_nutricional_actualizar = (
        ContenidoNutricional.query.filter(ContenidoNutricional.nutriente_id == json_data["nutriente_id"]).filter(ContenidoNutricional.insumo_id == json_data["insumo_id"]).filter(ContenidoNutricional.activo==True)
        .one_or_none()
    )

    if contenido_nutricional_actualizar is None:
        return {"Mensaje": "ContenidoNutricional no existe"}, 404
    contenido_nutricional_schema = ContenidoNutricionalSchema()
    try:
        data = contenido_nutricional_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    cantidad = data["cantidad"]
    nutriente_id = data["nutriente_id"]
    insumo_id = data["insumo_id"]

    nutriente_existe = Nutriente.query.get(nutriente_id)

    if nutriente_existe is None:
        return {"Mensaje": "El id del nutriente no se encuentra registrado"}, 400

    insumo_existe = Insumo.query.get(insumo_id)

    if insumo_existe is None:
        return {"Mensaje": "El id del insumo no se encuentra registrado"}, 400


    contenido_nutricional_actualizar.cantidad = cantidad
    contenido_nutricional_actualizar.fecha_modificacion = dt.now()


    db.session.merge(contenido_nutricional_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó contenido nutricional."}

#Servicio para eliminar una contenido nutricional mediante ID
@app.route('/contenidoNutricionales/delete', methods=['POST'])
def contenido_nutricional_eliminar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    
    #Se busca contenido nutricional en base de datos
    contenido_nutricional_eliminar = (
        ContenidoNutricional.query.filter(ContenidoNutricional.nutriente_id == json_data["nutriente_id"]).filter(ContenidoNutricional.insumo_id == json_data["insumo_id"]).filter(ContenidoNutricional.activo==True)
        .one_or_none()
    )

    if contenido_nutricional_eliminar is None:
        return {"Mensaje": "Contenido Nutricional no existe"}, 404
    else:
        contenido_nutricional_eliminar.activo=False
        db.session.merge(contenido_nutricional_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó contenido nutricional"}