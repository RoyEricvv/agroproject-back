from flask import request
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.RacionFormulada import RacionFormulada, RacionFormuladaSchema
from aplicacion.modelo.Animal import Animal
from aplicacion.modelo.Usuario import Usuario
from marshmallow import ValidationError

# Servicios de RacionFormulada


#Servicio para listar todos los racionFormuladas
@app.route('/racionFormuladas/<usuario_id>/all', methods=['GET'])
def racion_formulada_listar_todos(usuario_id):
    if usuario_id == '0':
        #Se crea la lista de usuarios.
        raciones_formuladas = RacionFormulada.query.filter(RacionFormulada.activo==True).order_by(RacionFormulada.id).all()
    else: 
        raciones_formuladas = RacionFormulada.query.filter(RacionFormulada.activo==True).filter(RacionFormulada.usuario_id == usuario_id).order_by(RacionFormulada.id).all()
    if len(raciones_formuladas) > 0:
        #Se serializa la información a retornar
        raciones_formuladas_schema = RacionFormuladaSchema(many=True)
        data = raciones_formuladas_schema.dump(raciones_formuladas)
 
        return {"Mensaje": "Lista de racion Formuladas", "racionFormuladas": data}
    else:
        return {"Mensaje": "No se encontró las raciones formuladas", "usuario_id": usuario_id}, 404

#Servicio para listar todos los racionFormuladas
@app.route('/racionFormuladas/<usuario_id>/<especie_id>/favoritos', methods=['GET'])
def racion_formulada_listar_favoritos(usuario_id, especie_id):
    if usuario_id == '0':
        #Se crea la lista de usuarios.
        raciones_formuladas = RacionFormulada.query.filter(RacionFormulada.activo==True).order_by(RacionFormulada.id).all()
    else: 
        raciones_formuladas = RacionFormulada.query.join(Animal).filter(Animal.activo==True).filter(RacionFormulada.activo==True).filter(Animal.especie_id == especie_id).filter(RacionFormulada.favorito == True).filter(RacionFormulada.usuario_id == usuario_id).order_by(RacionFormulada.etapa_semana).all()
    if len(raciones_formuladas) > 0:
        #Se serializa la información a retornar
        raciones_formuladas_schema = RacionFormuladaSchema(many=True)
        data = raciones_formuladas_schema.dump(raciones_formuladas)
 
        return {"Mensaje": "Lista de racion Formuladas", "racionFormuladas": data}
    else:
        return {"Mensaje": "No se encontró las raciones formuladas", "usuario_id": usuario_id}, 404

#Servicio para listar una racionFormuladas por id

@app.route('/racionFormuladas/<racionFormuladas_id>', methods=['GET'])
def racion_formulada_listar_uno(racionFormuladas_id):
    #Se busca el racionFormulada
    racion_formulada = RacionFormulada.query.filter(RacionFormulada.activo==True).filter(RacionFormulada.id == racionFormuladas_id).one_or_none()

    #Se encontró el racionFormuladas
    if racion_formulada is not None:

        # Se serializa la información a retornar
        racion_formulada_schema = RacionFormuladaSchema()
        data = racion_formulada_schema.dump(racion_formulada)
        return {"Mensaje": "Racion formulada encontrada", "racionFormulada": data}

    # No se encontró el racionFormuladas
    else:
        return {"Mensaje": "No se encontró el racion formulada", "racionFormuladaId": racionFormuladas_id},404

#Servicio para crear una racionFormulada
@app.route('/racionFormuladas', methods=['POST'])
def racion_formulada_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    racion_formulada_schema = RacionFormuladaSchema()
    
    try:
        data = racion_formulada_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    costo_total = data["costo_total"]
    cantidad_total = data["cantidad_total"]
    aplicar = data["aplicar"]
    usuario_id = data["usuario_id"]
    estado_racion = data ["estado_racion"]

    usuario_existe = Usuario.query.get(usuario_id)

    if usuario_existe is None:
        return {"Mensaje": "El id del usuario no se encuentra registrado"}, 400

    if costo_total and usuario_id:
        racion_formulada_nuevo = RacionFormulada(
            activo=True,
            costo_total=costo_total,
            cantidad_total=cantidad_total,
            aplicar=aplicar,
            usuario_id=usuario_id,
            favorito=False,
            estado_racion=estado_racion,
            fecha_creacion=dt.now(),
            fecha_modificacion=dt.now()
        )
        db.session.add(racion_formulada_nuevo)  # Añade un nuevo registro a la base de datos
        db.session.commit()  # Guarda todos los cambios

        return {"Mensaje": "Se creo racion formulada"}

#Servicio para actualizar un racionFormulada mediante ID
@app.route('/racionFormuladas/<racionFormuladas_id>', methods=['POST'])
def racion_formulada_actualizar(racionFormuladas_id):

    #Se busca racion Formulada en base de datos
    racion_formulada_actualizar = (
        RacionFormulada.query.filter(RacionFormulada.id == racionFormuladas_id).filter(RacionFormulada.activo==True)
        .one_or_none()
    )

    if racion_formulada_actualizar is None:
        return {"Mensaje": "Racion formulada no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    racion_formulada_schema = RacionFormuladaSchema()
    try:
        data = racion_formulada_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    costo_total = data["costo_total"]
    cantidad_total = data["cantidad_total"]
    aplicar = data["aplicar"]
    usuario_id = data["usuario_id"]
    estado_racion = data["estado_racion"]
    favorito = data["favorito"]

    usuario_existe = Usuario.query.get(usuario_id)

    if usuario_existe is None:
        return {"Mensaje": "El id del usuario no se encuentra registrado"}, 400

    racion_formulada_actualizar.costo_total = costo_total
    racion_formulada_actualizar.cantidad_total = cantidad_total
    racion_formulada_actualizar.aplicar = aplicar
    racion_formulada_actualizar.usuario_id = usuario_id
    racion_formulada_actualizar.estado_racion = estado_racion
    racion_formulada_actualizar.favorito = favorito
    racion_formulada_actualizar.fecha_modificacion = dt.now()

    db.session.merge(racion_formulada_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó racion formulada"}

#Servicio para eliminar un racionFormulada mediante ID
@app.route('/racionFormuladas/<racionFormuladas_id>/delete', methods=['GET'])
def racionFormulada_eliminar(racionFormuladas_id):

    #Se busca usuario en base de datos
    racion_formulada_eliminar = (
        RacionFormulada.query.filter(RacionFormulada.id == racionFormuladas_id).filter(RacionFormulada.activo==True)
        .one_or_none()
    )

    if racion_formulada_eliminar is None:
        return {"Mensaje": "Racion formulada no existe"}, 404
    else:
        racion_formulada_eliminar.activo=False
        db.session.merge(racion_formulada_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó racion formulada "}