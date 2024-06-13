from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.HistorialCrecimiento import HistorialCrecimiento, HistorialCrecimientoSchema
from aplicacion.modelo.Animal import Animal
from aplicacion.modelo.RacionFormulada import RacionFormulada
from marshmallow import ValidationError
from sqlalchemy import desc

# Servicios de Historial Crecimiento


#Servicio para listar todos los historialCrecimientos
@app.route('/historialCrecimiento/<animal_id>/all', methods=['GET'])
def historial_crecimiento_listar_todos(animal_id):
    if animal_id == '0':
        #Se crea la lista de todos los historialCrecimientos.
        historial_crecimientos = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).order_by(HistorialCrecimiento.id).all()
    else:
        #Se crea la lista de los historialCrecimientos de una granja.
        historial_crecimientos = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).filter(HistorialCrecimiento.animal_id == animal_id).order_by(desc(HistorialCrecimiento.semana_crecimiento)).all()
    if len(historial_crecimientos) > 0:  
        #Se serializa la información a retornar
        historial_crecimientos_schema = HistorialCrecimientoSchema(many=True)
        data = historial_crecimientos_schema.dump(historial_crecimientos)
    
        return {"Mensaje": "Lista de historial Crecimientos", "historialCrecimiento": data}
    else:
        return {"Mensaje": "No se encontró el historial crecimiento", "animal_id": animal_id}, 404

#Servicio para listar el último historialCrecimientos de la semana por animal Id
@app.route('/historialCrecimiento/<animal_id>', methods=['GET'])
def historial_crecimiento_listar_uno(animal_id):
    #Se busca el animal
    historial_crecimiento = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).filter(HistorialCrecimiento.animal_id == animal_id).order_by(desc(HistorialCrecimiento.semana_crecimiento)).first()

    #Se encontró el historialCrecimientos
    if historial_crecimiento is not None:

        # Se serializa la información a retornar
        historial_crecimiento_schema = HistorialCrecimientoSchema()
        data = historial_crecimiento_schema.dump(historial_crecimiento)
        return {"Mensaje": "Animal encontrada", "historialCrecimiento": data}

    # No se encontró el historialCrecimientos
    else:
        return {"Mensaje": "No se encontró el historial crecimiento", "id": id},404

#Servicio para crear un historial de desarrollo
@app.route('/historialCrecimiento', methods=['POST'])
def historial_crecimiento_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    historial_crecimiento_schema = HistorialCrecimientoSchema()
    
    try:
        data = historial_crecimiento_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    
    altura_promedio = data["altura_promedio"]
    peso_total = data["peso_total"]
    cantidad = data["cantidad"]
    semana_crecimiento = data["semana_crecimiento"]
    comentario = data["comentario"]
    animal_id = data["animal_id"]

    registro_inactivo_existe = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==False).filter(HistorialCrecimiento.semana_crecimiento == semana_crecimiento).filter(HistorialCrecimiento.animal_id == animal_id).one_or_none()

    if registro_inactivo_existe is not None:
        db.session.delete(registro_inactivo_existe)
        db.session.commit()
    
    animal_existe = Animal.query.filter(Animal.id == animal_id).one_or_none()

    if animal_existe is None:
        return {"Mensaje": "El id del animal no se encuentra registrado"}, 400


    registro_existe = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).filter(HistorialCrecimiento.semana_crecimiento == semana_crecimiento).filter(HistorialCrecimiento.animal_id == animal_id).one_or_none()

    if registro_existe is not None:
        return {"Mensaje": "Ya existe un registro con esa semana de crecimiento"}, 401

    usuario_actual=animal_existe.granja.usuario_id
    historial_crecimiento_menor = HistorialCrecimiento.query.filter(HistorialCrecimiento.semana_crecimiento < semana_crecimiento).filter(HistorialCrecimiento.animal_id == animal_id).order_by(desc(HistorialCrecimiento.semana_crecimiento)).first()

    if historial_crecimiento_menor is not None:
        raciones=RacionFormulada.query.filter(RacionFormulada.usuario_id == usuario_actual).filter(RacionFormulada.etapa_semana == historial_crecimiento_menor.semana_crecimiento).filter(RacionFormulada.aplicar == True).all()
        if len(raciones)>0:
            for item in raciones:
                item.aplicar=False
                db.session.merge(item)
                db.session.commit()

    historial_crecimiento_nuevo = HistorialCrecimiento(
        activo=True,
        altura_promedio=altura_promedio,
        peso_total=peso_total,
        cantidad=cantidad,
        semana_crecimiento=semana_crecimiento,
        comentario=comentario,
        animal_id=animal_id,
        fecha_creacion=dt.now(),
        fecha_modificacion=dt.now()
    )
    db.session.add(historial_crecimiento_nuevo)  # Añade un nuevo registro a la base de datos
    db.session.commit()  # Guarda todos los cambios

    ultimoHistorial = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).filter(HistorialCrecimiento.animal_id == animal_id).order_by(desc(HistorialCrecimiento.semana_crecimiento)).first()
    
    animal_existe.cantidad_actual=ultimoHistorial.cantidad
    animal_existe.peso_animal_actual=ultimoHistorial.peso_total
    animal_existe.precio_animal=round(ultimoHistorial.peso_total * animal_existe.precio_kg_animal,2)
    animal_existe.costo_kg_animal=round(animal_existe.costo_racion/ultimoHistorial.peso_total,2)
    animal_existe.etapa = 2
    db.session.add(animal_existe)  # Añade un nuevo registro a la base de datos
    db.session.commit()  # Guarda todos los cambios


    return {"Mensaje": "Se creo historial crecimiento"}

#Servicio para actualizar un crecimiento mediante ID
@app.route('/historialCrecimiento/<historial_crecimiento_id>', methods=['POST'])
def historial_crecimiento_actualizar(historial_crecimiento_id):

    #Se busca crecimiento en base de datos
    historial_crecimiento_actualizar = (
        HistorialCrecimiento.query.filter(HistorialCrecimiento.id == historial_crecimiento_id).filter(HistorialCrecimiento.activo==True)
        .one_or_none()
    )

    if historial_crecimiento_actualizar is None:
        return {"Mensaje": "Historial crecimiento no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    historial_crecimiento_schema = HistorialCrecimientoSchema()
    try:
        data = historial_crecimiento_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    comentario = data["comentario"]
    peso_total = data["peso_total"]
    cantidad = data["cantidad"]
    animal_id = data["animal_id"]
    altura_promedio = data["altura_promedio"]

    historial_crecimiento_actualizar.comentario = comentario
    historial_crecimiento_actualizar.altura_promedio = altura_promedio
    historial_crecimiento_actualizar.peso_total = peso_total
    historial_crecimiento_actualizar.cantidad = cantidad
    historial_crecimiento_actualizar.fecha_modificacion = dt.now()

    db.session.merge(historial_crecimiento_actualizar)
    db.session.commit()

    animal_existe = Animal.query.filter(Animal.id == animal_id).one_or_none()
    ultimoHistorial = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).filter(HistorialCrecimiento.animal_id == animal_id).order_by(desc(HistorialCrecimiento.semana_crecimiento)).first()
    
    animal_existe.cantidad_actual=ultimoHistorial.cantidad
    animal_existe.peso_animal_actual=ultimoHistorial.peso_total
    animal_existe.precio_animal=round(ultimoHistorial.peso_total * animal_existe.precio_kg_animal,2)
    animal_existe.costo_kg_animal=round(animal_existe.costo_racion/ultimoHistorial.peso_total,2)
    animal_existe.etapa = 2
    db.session.add(animal_existe)  # Añade un nuevo registro a la base de datos
    db.session.commit()  # Guarda todos los cambios

    return {"Mensaje": "Se actualizó historial crecimiento"}

#Servicio para eliminar un crecimiento mediante ID
@app.route('/historialCrecimiento/<historial_crecimiento_id>/delete', methods=['GET'])
def historial_crecimiento_eliminar(historial_crecimiento_id):

    #Se busca crecimiento en base de datos
    historial_crecimiento_eliminar = (
        HistorialCrecimiento.query.filter(HistorialCrecimiento.id == historial_crecimiento_id).filter(HistorialCrecimiento.activo==True)
        .one_or_none()
    )

    if historial_crecimiento_eliminar is None:
        return {"Mensaje": "Historial crecimiento no existe"}, 404
    else:
        animal_existe = Animal.query.filter(Animal.id == historial_crecimiento_eliminar.animal_id).one_or_none()
        historial_crecimiento_eliminar.activo=False
        db.session.merge(historial_crecimiento_eliminar)
        db.session.commit()

        ultimoHistorial = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).filter(HistorialCrecimiento.animal_id == animal_existe.id).order_by(desc(HistorialCrecimiento.semana_crecimiento)).first()
        if ultimoHistorial is not None:
            animal_existe.cantidad_actual=ultimoHistorial.cantidad
            animal_existe.peso_animal_actual=ultimoHistorial.peso_total
            animal_existe.precio_animal=round(ultimoHistorial.peso_total * animal_existe.precio_kg_animal,2)
            animal_existe.costo_kg_animal=round(animal_existe.costo_racion/ultimoHistorial.peso_total,2)
            animal_existe.etapa = 2
            db.session.add(animal_existe)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios
        else:
            animal_existe.cantidad_actual=0
            animal_existe.peso_animal_actual=0
            animal_existe.precio_animal=0
            animal_existe.costo_kg_animal=0
            animal_existe.etapa = 2
            db.session.add(animal_existe)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

        return {"Mensaje": "Se eliminó historial crecimiento "}