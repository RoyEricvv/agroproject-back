from aplicacion.modelo.Nutriente import Nutriente
from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.ContenidoRacion import ContenidoRacion, ContenidoRacionSchema
from aplicacion.modelo.RacionFormulada import RacionFormulada
from aplicacion.modelo.Insumo import Insumo
from marshmallow import ValidationError

# Servicios de contenido Ración


#Servicio para listar todos las contenido Nutricionales
@app.route('/contenidoRaciones/<racion_formulada_id>/all', methods=['GET'])
def contenido_racion_listar_todos(racion_formulada_id):
    if racion_formulada_id == '0':
        #Se crea la lista de contenidoRaciones.
        contenido_raciones = ContenidoRacion.query.filter(ContenidoRacion.activo==True).order_by(ContenidoRacion.insumo_id).all()
    else:
        #Se crea la lista de contenidoRaciones.
        contenido_raciones = ContenidoRacion.query.join(Insumo).filter(ContenidoRacion.activo==True).filter(ContenidoRacion.racion_formulada_id == racion_formulada_id).order_by(Insumo.nombre).all()

    if len(contenido_raciones)>0:
        #Se serializa la información a retornar
        contenido_raciones_schema = ContenidoRacionSchema(many=True)
        data = contenido_raciones_schema.dump(contenido_raciones)
    
        return {"Mensaje": "Se lista las contenidoRaciones", "contenidoRaciones": data}
    else:
        return {"Mensaje": "No se encontró el contenido", "racionformuladaID": racion_formulada_id}, 404

#Servicio para devolver una contenido Ración por usuario_id
'''
@app.route('/contenidoRaciones/<contenidoRacion_id>', methods=['GET'])
def contenido_racion_listar_uno(contenidoRacion_id):
    #Se busca la contenido Ración
    contenido_racion = ContenidoRacion.query.filter(ContenidoRacion.id == contenidoRacion_id).one_or_none()

    #Se encontró la contenido Ración
    if contenido_racion is not None:

        print(contenido_racion)
        # Se serializa la información a retornar
        contenido_racion_schema = ContenidoRacionSchema()
        data = contenido_racion_schema.dump(contenido_racion)
        return {"Mensaje": "Se encontró el contenido Ración", "ContenidoRacion": data}

    # No se encontró el usuario
    else:
        return {"Mensaje": "No se encontró el contenido Ración", "racionFormuladaId": contenidoRacion_id},404
'''
#Servicio para crear una contenido Ración
@app.route('/contenidoRaciones', methods=['POST'])
def contenido_racion_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    contenido_racion_schema = ContenidoRacionSchema()
    
    try:
        data = contenido_racion_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    cantidad_total = data["cantidad_total"]
    costo_total = data["costo_total"]
    insumo_id = data["insumo_id"]
    racion_formulada_id = data["racion_formulada_id"]
    

    racion_formulada_existe = RacionFormulada.query.get(racion_formulada_id)

    if racion_formulada_existe is None:
        return {"Mensaje": "El id de la racion formulada no se encuentra registrado"}, 400

    insumo_existe = Insumo.query.get(insumo_id)

    if insumo_existe is None:
        return {"Mensaje": "El id del insumo no se encuentra registrado"}, 400

    registro_existe = ContenidoRacion.query.filter(ContenidoRacion.activo==True).filter(ContenidoRacion.insumo_id == insumo_id).filter(ContenidoRacion.racion_formulada_id == racion_formulada_id).one_or_none()

    if registro_existe is not None:
        return {"Mensaje": "Ya existe un registro con la misma información"}, 401
    
    contenido_racion_nuevo = ContenidoRacion(
        activo=True,
        cantidad_total=cantidad_total,
        costo_total=costo_total,
        insumo_id=insumo_id,
        racion_formulada_id=racion_formulada_id,
        fecha_creacion=dt.now(),
        fecha_modificacion=dt.now()
    )
    db.session.add(contenido_racion_nuevo)  # Añade un nuevo registro a la base de datos
    db.session.commit()  # Guarda todos los cambios

    return {"Mensaje": "Se creo contenido Ración"}




#Servicio para actualizar una contenido Ración mediante ID
@app.route('/contenidoRaciones/update', methods=['POST'])
def contenido_racion_actualizar():
    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca contenido Ración en base de datos
    contenido_racion_actualizar = (
        ContenidoRacion.query.filter(ContenidoRacion.activo==True).filter(ContenidoRacion.insumo_id == json_data["insumo_id"]).filter(ContenidoRacion.racion_formulada_id == json_data["racion_formulada_id"])
        .one_or_none()
    )

    if contenido_racion_actualizar is None:
        return {"Mensaje": "ContenidoRacion no existe"}, 404

    contenido_racion_schema = ContenidoRacionSchema()
    try:
        data = contenido_racion_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    cantidad_total = data["cantidad_total"]
    costo_total = data["costo_total"]
    insumo_id = data["insumo_id"]
    racion_formulada_id = data["racion_formulada_id"]

    racion_formulada_existe = RacionFormulada.query.get(racion_formulada_id)

    if racion_formulada_existe is None:
        return {"Mensaje": "El id de la racion formulada no se encuentra registrado"}, 400

    insumo_existe = Insumo.query.get(insumo_id)

    if insumo_existe is None:
        return {"Mensaje": "El id del insumo no se encuentra registrado"}, 400


    contenido_racion_actualizar.cantidad_total = cantidad_total
    contenido_racion_actualizar.costo_total = costo_total
    contenido_racion_actualizar.fecha_modificacion = dt.now()

    db.session.merge(contenido_racion_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó contenido Ración."}

#Servicio para eliminar una contenido Ración mediante ID
@app.route('/contenidoRaciones/delete', methods=['POST'])
def contenido_racion_eliminar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca contenido Ración en base de datos
    contenido_racion_eliminar = (
        ContenidoRacion.query.filter(ContenidoRacion.activo==True).filter(ContenidoRacion.insumo_id == json_data["insumo_id"]).filter(ContenidoRacion.racion_formulada_id == json_data["racion_formulada_id"])
        .one_or_none()
    )

    if contenido_racion_eliminar is None:
        return {"Mensaje": "contenido Ración no existe"}, 404
    else:
        contenido_racion_eliminar.activo=False
        db.session.merge(contenido_racion_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó contenido Ración"}