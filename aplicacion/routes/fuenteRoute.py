from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Fuente import Fuente, FuenteSchema
from marshmallow import ValidationError


#Servicio para listar todas las materias secas
@app.route('/fuente/all', methods=['GET'])
def fuente_todos():
    #Se crea la lista de toda la materia seca.
    fuentes = Fuente.query.filter(Fuente.activo==True).order_by(Fuente.id).all()
    #Se serializa la información a retornar
    fuentes_schema = FuenteSchema(many=True)
    data = fuentes_schema.dump(fuentes)
    
    return {"Mensaje": "Lista de Fuentes", "fuentes": data}

#Servicio para crear una fuente
@app.route('/fuente', methods=['POST'])
def fuente_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    fuente_schema = FuenteSchema()
    
    try:
        data = fuente_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    nombre = data["nombre"]

    #Se busca fuente repetido en base de datos
    fuente_existente = (
        Fuente.query.filter(Fuente.nombre == nombre).filter(Fuente.activo==True)
        .one_or_none()
    )

    if fuente_existente is None:

        if nombre:
            fuente_nuevo = Fuente(
                activo=True,
                nombre=nombre,
            )
            db.session.add(fuente_nuevo)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

            return {"Mensaje": "Se creo fuente"}
    # La fuente ya existe
    else:
        return {"Mensaje": "Fuente ya existe", "fuente": nombre}, 401

#Servicio para actualizar una materia seca mediante ID
@app.route('/fuente/update', methods=['POST'])
def fuente_actualizar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca fuente en base de datos
    fuente_actualizar = (
        Fuente.query.filter(Fuente.id == json_data["id"]).filter(Fuente.activo==True)
        .one_or_none()
    )

    if fuente_actualizar is None:
        return {"Mensaje": "Fuente no existe"}, 404

    nombre = "%{}%".format(json_data["id"])

    fuente_duplicado = (
        Fuente.query.filter(Fuente.nombre == json_data["nombre"])
        .one_or_none()
    )

    if fuente_duplicado is not None:
        return {"Mensaje": "Fuente ya registrada", "nombreRepetido":nombre}, 403

    Fuente.nombre = json_data["nombre"]

    db.session.merge(fuente_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó fuente."}