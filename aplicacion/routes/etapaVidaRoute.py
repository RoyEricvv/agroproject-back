from flask import request
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.EtapaVida import EtapaVida, EtapaVidaSchema
from aplicacion.modelo.HistorialCrecimiento import HistorialCrecimiento, HistorialCrecimientoSchema
from aplicacion.modelo.Especie import Especie
from aplicacion.modelo.Fuente import Fuente,FuenteSchema
from aplicacion.modelo.Animal import Animal
from aplicacion.modelo.RequerimientoNutricional import RequerimientoNutricional
from marshmallow import ValidationError
from sqlalchemy import desc

# Servicios de Etapa deVida


#Servicio para listar todos los Etapa de Vida de especie
@app.route('/etapaVida/<especie_id>/all', methods=['GET'])
def etapa_vida_listar_todos(especie_id):
    if especie_id == '0':
        #Se crea la lista.
        etapa_vida = EtapaVida.query.filter(EtapaVida.activo==True).order_by(EtapaVida.id).all()
    else: 
        etapa_vida = EtapaVida.query.filter(EtapaVida.activo==True).filter(EtapaVida.especie_id == especie_id).order_by(desc(EtapaVida.semana_vida_referencial_inicial)).all()
    if len(etapa_vida) > 0:
        #Se serializa la información a retornar
        etapa_vida_schema = EtapaVidaSchema(many=True)
        data = etapa_vida_schema.dump(etapa_vida)
 
        return {"Mensaje": "Lista de etapa de vida especie", "etapaVida": data}
    else:
        return {"Mensaje": "No se encontró las caracteristicas especie", "especie_id": especie_id}, 404


#Servicio para listar todos los Etapa de Vida de especie menores a la última entrada de crecimiento
@app.route('/etapaVida/<especie_id>/<animal_id>/all', methods=['GET'])
def etapa_vida_listar_validado(especie_id, animal_id):
    if especie_id == '0':
        return {"Mensaje": "No se envió especie id"}, 401

    if animal_id == '0':
        return {"Mensaje": "No se envió animal id"}, 401
    
    historial_crecimiento = HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).filter(HistorialCrecimiento.animal_id == animal_id).order_by(desc(HistorialCrecimiento.semana_crecimiento)).first()

    if historial_crecimiento is None:
        return {"Mensaje": "No existe historial de crecimiento registrado"}, 401
    
    historial_crecimiento_schema = HistorialCrecimientoSchema()
    data_historial = historial_crecimiento_schema.dump(historial_crecimiento)

    etapa_vida = EtapaVida.query.filter(EtapaVida.activo==True).filter(EtapaVida.especie_id == especie_id).filter(EtapaVida.semana_vida_referencial_inicial < historial_crecimiento.semana_crecimiento).filter(EtapaVida.semana_vida_referencial_final >= historial_crecimiento.semana_crecimiento).order_by(EtapaVida.semana_vida_referencial_inicial).first()

    if etapa_vida is None:
        return {"Mensaje": "No existe etapa de vida de la especie registrada para la última semana de crecimiento del animal seleccionado.", "especie_id": especie_id}, 404

    lista_fuentes = Fuente.query.filter(Fuente.activo==True).all()
    fuente_disponible = []
    data_fuente = []
    animal = Animal.query.filter(Animal.activo==True).filter(Animal.id == animal_id).one_or_none()

    for fuente in lista_fuentes:
        existe = RequerimientoNutricional.query.filter(RequerimientoNutricional.activo==True).filter(RequerimientoNutricional.etapa_vida_id == etapa_vida.id).filter(RequerimientoNutricional.fuente_id == fuente.id).filter(RequerimientoNutricional.departamento_id==animal.granja.departamento_id).first()
        if existe is not None:
            fuente_disponible.append(fuente)

    if len(fuente_disponible)>0:
        fuente_schema = FuenteSchema(many=True)
        data_fuente = fuente_schema.dump(fuente_disponible)

    #Se serializa la información a retornar
    etapa_vida_schema = EtapaVidaSchema()
    data_etapa_vida = etapa_vida_schema.dump(etapa_vida)

    return {"Mensaje": "Lista de etapa de vida especie", "etapaVida": data_etapa_vida,"historial":data_historial,"fuente":data_fuente}


#Servicio para listar una Etapa de Vida de especie por id
@app.route('/etapaVida/<etapaVida_id>', methods=['GET'])
def etapa_vida_listar_uno(etapaVida_id):
    #Se busca el racionFormulada
    caracteristica_especie = EtapaVida.query.filter(EtapaVida.activo==True).filter(EtapaVida.id == etapaVida_id).one_or_none()

    #Se encontró el racionFormuladas
    if caracteristica_especie is not None:

        # Se serializa la información a retornar
        etapa_vida_schema = EtapaVidaSchema()
        data = etapa_vida_schema.dump(caracteristica_especie)
        return {"Mensaje": "etapa de vida de especie encontrada", "etapaVida": data}

    # No se encontró el racionFormuladas
    else:
        return {"Mensaje": "No se encontró el etapa de vida", "etapaVida_id": etapaVida_id}, 404
        

#Servicio para crear una Etapa de Vida de especie
@app.route('/etapaVida', methods=['POST'])
def etapa_vida_crear():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    etapa_vida_schema = EtapaVidaSchema()
    
    try:
        data = etapa_vida_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422
    

    peso_vivo_referencial = data["peso_vivo_referencial"]
    talla_referencial = data["talla_referencial"]
    semana_vida_referencial_inicial = data["semana_vida_referencial_inicial"]
    semana_vida_referencial_final = data["semana_vida_referencial_final"]
    cantidad_MS_referencial = data["cantidad_MS_referencial"]
    especie_id = data["especie_id"]

    especie_existe = Especie.query.get(especie_id)

    if especie_existe is None:
        return {"Mensaje": "El id de la especie no se encuentra registrado"}, 400

    if especie_id:
        etapa_vida_nuevo = EtapaVida(
            activo=True,
            peso_vivo_referencial=peso_vivo_referencial,
            talla_referencial=talla_referencial,
            semana_vida_referencial_inicial=semana_vida_referencial_inicial,
            semana_vida_referencial_final=semana_vida_referencial_final,
            cantidad_MS_referencial=cantidad_MS_referencial,
            especie_id=especie_id,
            fecha_creacion=dt.now(),
            fecha_modificacion=dt.now()
            
        )
        db.session.add(etapa_vida_nuevo)  # Añade un nuevo registro a la base de datos
        db.session.commit()  # Guarda todos los cambios

        return {"Mensaje": "Se creo etapa de vida"}

#Servicio para actualizar una Etapa de Vida de especie mediante ID
@app.route('/etapaVida/<etapaVida_id>', methods=['POST'])
def etapa_vida_actualizar(etapaVida_id):

    #Se busca etapa de vida en base de datos
    etapa_vida_actualizar = (
        EtapaVida.query.filter(EtapaVida.id == etapaVida_id).filter(EtapaVida.activo==True)
        .one_or_none()
    )

    if etapa_vida_actualizar is None:
        return {"Mensaje": "Etapa de vida no existe"}, 404

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404
    etapa_vida_schema = EtapaVidaSchema()
    try:
        data = etapa_vida_schema.load(json_data, partial=True)
    except ValidationError as err:
        return err.messages, 422

    peso_vivo_referencial = data["peso_vivo_referencial"]
    talla_referencial = data["talla_referencial"]
    semana_vida_referencial_inicial = data["semana_vida_referencial_inicial"]
    semana_vida_referencial_final = data["semana_vida_referencial_final"]
    cantidad_MS_referencial = data["cantidad_MS_referencial"]
    especie_id = data["especie_id"]

    especie_existe = Especie.query.get(especie_id)

    if especie_existe is None:
        return {"Mensaje": "El id del usuario no se encuentra registrado"}, 400

    etapa_vida_actualizar.peso_vivo_referencial = peso_vivo_referencial
    etapa_vida_actualizar.talla_referencial = talla_referencial
    etapa_vida_actualizar.semana_vida_referencial_inicial = semana_vida_referencial_inicial
    etapa_vida_actualizar.semana_vida_referencial_final = semana_vida_referencial_final
    etapa_vida_actualizar.cantidad_MS_referencial = cantidad_MS_referencial
    etapa_vida_actualizar.especie_id = especie_id
    etapa_vida_actualizar.fecha_modificacion = dt.now()

    db.session.merge(etapa_vida_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó Etapa de Vida de especie"}

#Servicio para eliminar una Etapa de Vida de especie mediante ID
@app.route('/etapaVida/<etapaVida_id>/delete', methods=['GET'])
def etapa_vida_eliminar(etapaVida_id):

    #Se busca usuario en base de datos
    etapa_vida_eliminar = (
        EtapaVida.query.filter(EtapaVida.id == etapaVida_id).filter(EtapaVida.activo==True)
        .one_or_none()
    )

    if etapa_vida_eliminar is None:
        return {"Mensaje": "Etapa de Vida de especie no existe"}, 404
    else:
        etapa_vida_eliminar.activo=False
        db.session.merge(etapa_vida_eliminar)
        db.session.commit()

        return {"Mensaje": "Se eliminó Etapa de Vida de especie "}