from flask import request, make_response, abort, jsonify
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.ConsumoSanitario import ConsumoSanitario, ConsumoSanitarioSchema, SimpleConsumoSanitarioSchema, consumo_vacuna, consumo_animal 
from aplicacion.modelo.Sanitario import Sanitario
from aplicacion.modelo.Granja import Granja
from aplicacion.modelo.Animal import Animal
from marshmallow import ValidationError

# Servicio de ConsumoSanitario
consumo_sanitario_schema = ConsumoSanitarioSchema()
consumos_sanitarios_schema = ConsumoSanitarioSchema(many=True)

simple_consumo_sanitario_schema = SimpleConsumoSanitarioSchema()
simple_consumos_sanitarios_schema = SimpleConsumoSanitarioSchema(many=True)

@app.route('/consumos_sanitarios', methods=['POST'])
def consumo_sanitario_crear():
    json_data = request.get_json()
    if not json_data:
        return jsonify({"Mensaje": "No se envió información"}), 400

    try:
        # Validar y cargar los datos recibidos
        data = consumo_sanitario_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422
    try:
        # Crear una nueva instancia de ConsumoSanitario
        nuevo_consumo_sanitario = ConsumoSanitario(
            granja_id=data['granja_id'],
            personal_solicitante=data['personal_solicitante'],
            fecha_salida=data['fecha_salida'],
            lote=data.get('lote'),
            observaciones=data.get('observaciones')
        )

        # Guardar el nuevo ConsumoSanitario en la base de datos
        db.session.add(nuevo_consumo_sanitario)
        db.session.commit()

        # Añadir relación con Sanitarios (vacunas) y número de dosis
        if 'vacunas' in data:
            for vacuna_data in data['vacunas']:
                vacuna_id = vacuna_data['vacuna_id']
                saldo_total = vacuna_data['numero_dosis']
                sanitario = Sanitario.query.filter_by(id = vacuna_id).first()
                if not sanitario:
                    return jsonify({"Mensaje": "Sanitario no encontrado"}), 404
                # Verificar si la cantidad a consumir es menor o igual al saldo disponible
                if saldo_total > sanitario.saldo:
                    return jsonify({"Mensaje": "Cantidad a consumir excede el saldo disponible"}), 400
                # Actualizar el saldo
                sanitario.saldo  -= saldo_total
                db.session.commit()
                stmt = consumo_vacuna.insert().values(consumo_id=nuevo_consumo_sanitario.id, vacuna_id=vacuna_id, numero_dosis=saldo_total)
                db.session.execute(stmt)

        # Añadir relación con Animales
        if 'animales' in data:
            for animal_data in data['animales']:
                stmt = consumo_animal.insert().values(consumo_id=nuevo_consumo_sanitario.id, animal_id=animal_data['animal_id'])
                db.session.execute(stmt)

        db.session.commit()

        return jsonify({"Mensaje": "ConsumoSanitario creado exitosamente"})

    except Exception as e:
        # En caso de cualquier error no esperado, se hace un rollback de la transacción
        db.session.rollback()
        return jsonify({"Mensaje": "Error al crear ConsumoSanitario", "Error": str(e)}), 500


# #Listar consumo
# @app.route('/consumos_sanitarios/<int:id>', methods=['GET'])
# def obtener_consumo_sanitario_por_id(id):
#     try:
#         consumo_sanitario = ConsumoSanitario.query.all()
#         # consumo_sanitario = ConsumoSanitario.query.filter_by(id=id).first()

#         if not consumo_sanitario:
#             return jsonify({"Mensaje": "ConsumoSanitario no encontrado"}), 404

#         # Serializar el consumo sanitario
#         result = simple_consumos_sanitarios_schema.dump(consumo_sanitario)

#         return jsonify(result)

#     except Exception as e:
#         return jsonify({"Mensaje": "Error al obtener ConsumoSanitario", "Error": str(e)}), 500


# #actualizar consumo
# @app.route('/consumos_sanitarios/<int:id>', methods=['PUT'])
# def actualizar_consumo_sanitario(id):
#     json_data = request.get_json()
#     if not json_data:
#         return jsonify({"Mensaje": "No se envió información"}), 400

#     try:
#         # Obtener el consumo sanitario a actualizar
#         consumo_sanitario = ConsumoSanitario.query.get(id)
#         if not consumo_sanitario:
#             return jsonify({"Mensaje": "ConsumoSanitario no encontrado"}), 404

#         # Validar y cargar los datos recibidos
#         data = consumo_sanitario_schema.load(json_data)

#         # Actualizar los campos necesarios
#         consumo_sanitario.granja_id = data.get('granja_id', consumo_sanitario.granja_id)
#         consumo_sanitario.personal_solicitante = data.get('personal_solicitante', consumo_sanitario.personal_solicitante)
#         consumo_sanitario.fecha_salida = data.get('fecha_salida', consumo_sanitario.fecha_salida)
#         consumo_sanitario.lote = data.get('lote', consumo_sanitario.lote)
#         consumo_sanitario.observaciones = data.get('observaciones', consumo_sanitario.observaciones)

#         # Guardar los cambios en la base de datos
#         db.session.commit()

#         return jsonify({"Mensaje": "ConsumoSanitario actualizado exitosamente"})

#     except ValidationError as err:
#         return jsonify(err.messages), 422
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"Mensaje": "Error al actualizar ConsumoSanitario", "Error": str(e)}), 500


# #eliminar consumo
# @app.route('/consumos_sanitarios/<int:id>', methods=['DELETE'])
# def eliminar_consumo_sanitario(id):
#     try:
#         consumo_sanitario = ConsumoSanitario.query.get(id)
#         if not consumo_sanitario:
#             return jsonify({"Mensaje": "ConsumoSanitario no encontrado"}), 404

#         # Eliminar relaciones (por ejemplo, consumo_vacuna y consumo_animal)
#         consumo_vacuna.delete().where(consumo_vacuna.c.consumo_id == id).execute()
#         consumo_animal.delete().where(consumo_animal.c.consumo_id == id).execute()

#         # Eliminar el consumo sanitario
#         db.session.delete(consumo_sanitario)
#         db.session.commit()

#         return jsonify({"Mensaje": "ConsumoSanitario eliminado exitosamente"})

#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"Mensaje": "Error al eliminar ConsumoSanitario", "Error": str(e)}), 500

#listar consumos sanitarios
# @app.route('/consumos_sanitarios', methods=['GET'])
# def listar_consumos_sanitarios():
#     try:
#         consumos_sanitarios = ConsumoSanitario.query.all()
#         # Serializar la lista de consumos sanitarios
#         result = consumos_sanitarios_schema.dump(consumos_sanitarios)
#         return jsonify(result)

#     except Exception as e:
#         return jsonify({"Mensaje": "Error al listar ConsumosSanitarios", "Error": str(e)}), 500


# @app.route('/consumos_sanitarios', methods=['GET'])
# def listar_consumos_sanitarios():
#     try:
#         consumos_sanitarios = ConsumoSanitario.query.all()

#         # Crear una lista para almacenar los consumos sanitarios serializados
#         consumos_serializados = []
        
#         for consumo in consumos_sanitarios:
#             # Serializar el consumo sanitario principal
#             print("vuamso")
#             print(consumos_sanitarios)
#             consumo_serializado = consumo_sanitario_schema.dump(consumo)
            
#             # Obtener detalles de las vacunas asociadas usando la relación de tabla intermedia
#             vacunas = []
#             for cv in consumo.consumos_vacunas:
#                 vacuna_detalle = {
#                     "vacuna_id": cv.vacuna_id,
#                     "numero_dosis": cv.numero_dosis
#                 }
#                 vacunas.append(vacuna_detalle)

#             # Obtener detalles de los animales asociados usando la relación de tabla intermedia
#             animales = []
#             for ca in consumo.consumos_animales:
#                 animal_detalle = {
#                     "animal_id": ca.animal_id
#                 }
#                 animales.append(animal_detalle)

#             # Agregar detalles de vacunas y animales al consumo sanitario serializado
#             consumo_serializado["vacunas"] = vacunas
#             consumo_serializado["animales"] = animales

#             # Agregar el consumo sanitario serializado a la lista
#             consumos_serializados.append(consumo_serializado)

#         # Retornar la lista de consumos sanitarios serializados como JSON
#         return jsonify(consumos_serializados)

#     except Exception as e:
#         return jsonify({"Mensaje": "Error al listar ConsumosSanitarios", "Error": str(e)}), 500

#     try:
#         print("vuamos2")
#         # Crear una nueva instancia de ConsumoSanitario
#         nuevo_consumo_sanitario = ConsumoSanitario(
#             granja_id=data['granja_id'],
#             personal_solicitante=data['personal_solicitante'],
#             fecha_salida=data['fecha_salida'],
#             lote=data.get('lote'),
#             observaciones=data.get('observaciones')
#         )

#         # Guardar el nuevo ConsumoSanitario en la base de datos
#         db.session.add(nuevo_consumo_sanitario)
#         db.session.commit()
#         # Añadir relación con Sanitarios (vacunas) y número de dosis
#         if 'vacunas' in data:
#             for vacuna_data in data['vacunas']:
#                 stmt = consumo_vacuna.insert().values(consumo_id=nuevo_consumo_sanitario.id, vacuna_id=vacuna_data['vacuna_id'], numero_dosis=vacuna_data['numero_dosis'])
#                 db.session.execute(stmt)

#         # Añadir relación con Animales
#         if 'animales' in data:
#             for animal_data in data['animales']:
#                 stmt = consumo_animal.insert().values(consumo_id=nuevo_consumo_sanitario.id, animal_id=animal_data['animal_id'])
#                 db.session.execute(stmt)