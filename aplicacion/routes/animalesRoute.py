from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Animal import Animal, AnimalSchema
from aplicacion.modelo.Granja import Granja
from aplicacion.modelo.Especie import Especie
from marshmallow import ValidationError

# Servicios de Animal


#Servicio para listar todos los animales de una granja
@app.route('/animales/<granja_id>/allGranja', methods=['GET'])
def animal_listar_todos_granja(granja_id):
    if granja_id == '0':
        #Se crea la lista de todos los animales.
        animales = Animal.query.filter(Animal.activo==True).order_by(Animal.nombre).all()
    else:
        #Se crea la lista de los animales de una granja.
        animales = Animal.query.filter(Animal.granja_id == granja_id).filter(Animal.activo==True).order_by(Animal.id).all()
    if len(animales) > 0:  
        #Se serializa la información a retornar
        animales_schema = AnimalSchema(many=True)
        data = animales_schema.dump(animales)
    
        return {"Mensaje": "Lista de animales", "animales": data}
    else:
        return {"Mensaje": "No se encontró el animal", "granjaId": granja_id},404

#Servicio para listar todos los animales de un usuario
@app.route('/animales/<usuario_id>/<tipo>/allAnimales', methods=['GET'])
def animal_listar_todos_usuario(usuario_id,tipo):
    if usuario_id == '0':
        #Se crea la lista de todos los animales.
        animales = Animal.query.filter(Animal.activo==True).order_by(Animal.id).all()
    else:
        #Se crea la lista de los animales de una granja.
        if tipo == 1: #Listar animales no contabilizados
            animales = Animal.query.join(Granja).filter(Granja.usuario_id == usuario_id).filter(Animal.activo==True).filter(Animal.estado_animal!=3).order_by(Animal.id).all()
        else:
            animales = Animal.query.join(Granja).filter(Granja.usuario_id == usuario_id).filter(Animal.activo==True).order_by(Animal.id).all()
        print(animales)
    if len(animales) > 0:
        #Se serializa la información a retornar
        animales_schema = AnimalSchema(many=True)
        data = animales_schema.dump(animales)
    
        return {"Mensaje": "Lista de animales", "animales": data}
    else:
        return {"Mensaje": "No se encontró animales", "usuarioId": usuario_id},404

#Servicio para listar una animales por id
@app.route('/animales/<animales_id>', methods=['GET'])
def animal_listar_uno(animales_id):
    #Se busca el animal
    animal = Animal.query.filter(Animal.id == animales_id).filter(Animal.activo==True).one_or_none()

    #Se encontró el animales
    if animal is not None:

        # Se serializa la información a retornar
        animal_schema = AnimalSchema()
        data = animal_schema.dump(animal)
        return {"Mensaje": "Animal encontrada", "animal": data}

    # No se encontró el animales
    else:
        return {"Mensaje": "No se encontró el animal", "animalId": animales_id},404

#Servicio para crear una animal
@app.route('/animales', methods=['POST'])
def animal_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    animal_schema = AnimalSchema()
    
    try:
        data = animal_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    nombre = data["nombre"]
    comentario = data["comentario"]
    granja_id = data["granja_id"]
    especie_id = data["especie_id"]
    precio_kg_animal = data["precio_kg_animal"]


    granja_existe= Granja.query.filter(Granja.id == granja_id).one_or_none()

    if granja_existe is None:
        return {"Mensaje": "El id de la granja no se encuentra registrado"}, 400

    especie_existe= Especie.query.get(especie_id)

    if especie_existe is None:
        return {"Mensaje": "El id de la especie no se encuentra registrado"}, 400

    registro_existe = Animal.query.filter(Animal.nombre == nombre).filter(Animal.granja_id == granja_id).filter(Animal.especie_id == especie_id).filter(Animal.activo==True).one_or_none()

    if registro_existe is not None:
        return {"Mensaje": "Ya existe un registro con ese nombre"}, 401

    animal_nuevo = Animal(
        activo=True,
        nombre=nombre,
        comentario=comentario,
        granja_id=granja_id,
        especie_id=especie_id,
        estado_animal=1,
        peso_animal_actual=0,
        cantidad_actual=0,
        costo_racion=0,
        costo_kg_animal=0,
        precio_animal=0,
        precio_kg_animal=precio_kg_animal,
        fecha_creacion=dt.now(),
        fecha_modificacion=dt.now()
    )
    db.session.add(animal_nuevo)  # Añade un nuevo registro a la base de datos
    db.session.commit()  # Guarda todos los cambios

    return {"Mensaje": "Se creo animal"}

#Servicio para actualizar un animal mediante ID
@app.route('/animales/<animales_id>', methods=['POST'])
def animal_actualizar(animales_id):

    #Se busca animal en base de datos
    animal_actualizar = (
        Animal.query.filter(Animal.id == animales_id).filter(Animal.activo==True)
        .one_or_none()
    )

    if animal_actualizar is None:
        return {"Mensaje": "Animal no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    animal_schema = AnimalSchema()
    try:
        data = animal_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    nombre = data["nombre"]
    comentario = data["comentario"]
    granja_id = data["granja_id"]
    estado_animal = data["estado_animal"]
    precio_kg_animal = data["precio_kg_animal"]

    granja_existe= Granja.query.filter(Granja.id == granja_id).one_or_none()

    if granja_existe is None:
        return {"Mensaje": "El id de la granja no se encuentra registrado"}, 400

    animale_existe = Animal.query.filter(Animal.id != animales_id).filter(Animal.granja_id == granja_id).filter(Animal.nombre == nombre).one_or_none()

    if animale_existe is not None:
        return {"Mensaje": "Ya existe un registro con ese nombre"}, 401


    animal_actualizar.precio_animal= round(precio_kg_animal * animal_actualizar.peso_animal_actual ,2)    
    animal_actualizar.nombre = nombre
    animal_actualizar.comentario = comentario
    animal_actualizar.granja_id = granja_id
    animal_actualizar.estado_animal=estado_animal
    animal_actualizar.precio_kg_animal=precio_kg_animal
    animal_actualizar.fecha_modificacion = dt.now()

    db.session.merge(animal_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó animal"}

#Servicio para eliminar un animal mediante ID
@app.route('/animales/<animales_id>/delete', methods=['GET'])
def animal_eliminar(animales_id):

    #Se busca usuario en base de datos
    animal_eliminar = (
        Animal.query.filter(Animal.id == animales_id).filter(Animal.activo==True)
        .one_or_none()
    )

    if animal_eliminar is None:
        return {"Mensaje": "Animal no existe"}, 404
    else:
        animal_eliminar.activo=False
        db.session.merge(animal_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó animal "}