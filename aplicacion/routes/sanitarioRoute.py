from flask import request, make_response, abort, jsonify
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Sanitario import Sanitario, SanitarioSchema, SimpleSanitarioSchema
from aplicacion.modelo.Granja import Granja
from aplicacion.modelo.Especie import Especie
from marshmallow import ValidationError

# Servicios de Sanitario
sanitario_schema = SanitarioSchema()
sanitarios_schema = SanitarioSchema(many=True)
simple_sanitario_schema = SimpleSanitarioSchema()
simple_sanitarios_schema = SimpleSanitarioSchema(many=True)


# Crear un nuevo sanitario
@app.route('/sanitarios', methods=['POST'])
def sanitario_crear():
    json_data = request.get_json()

    if not json_data:
        return jsonify({"Mensaje": "No se envió información"}), 400

    try:
        # Validar y cargar los datos recibidos
        data = sanitario_schema.load(json_data)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # Crear una nueva instancia de Sanitario
    nuevo_sanitario = Sanitario(
        granja_id=data['granja_id'],
        especie_id=data['especie_id'],
        rubro=data['rubro'],
        fecha_ingreso=data['fecha_ingreso'],  # No necesita conversión si está en el formato correcto
        fecha_vencimiento=data['fecha_vencimiento'],  # No necesita conversión si está en el formato correcto
        frascos=data['frascos'],
        marca=data['marca'],
        dosis=data['dosis'],
        ml_animal=data['ml_animal'],
        estado_sanitario=data['estado_sanitario'],
        observaciones=data.get('observaciones'),
        saldo=data['frascos']*data['dosis'],
        activo=True
    )

    # Guardar el nuevo sanitario en la base de datos
    db.session.add(nuevo_sanitario)
    db.session.commit()

    return jsonify({"Mensaje": "Sanitario creado exitosamente"})


# Obtener todos los sanitarios de una granja por su ID
@app.route('/sanitarios/granja/<granja_id>', methods=['GET'])
def sanitario_listar_por_granja(granja_id):
    estado_sanitario = request.args.get('estado_sanitario', None)
    query = Sanitario.query.filter_by(granja_id=granja_id, activo=True)

    if estado_sanitario:
        query = query.filter_by(estado_sanitario=estado_sanitario)

    sanitarios = query.all()

    if sanitarios:
        resultado = sanitarios_schema.dump(sanitarios)
        return jsonify({"Mensaje": "Lista de sanitarios", "sanitarios": resultado})
    else:
        return jsonify({"Mensaje": "No se encontraron sanitarios para la granja especificada", "granjaId": granja_id}), 404


# Obtener un sanitario por su ID
@app.route('/sanitarios/<sanitario_id>', methods=['GET'])
def sanitario_obtener_por_id(sanitario_id):
    sanitario = Sanitario.query.get(sanitario_id)

    if sanitario and sanitario.activo:
        resultado = simple_sanitario_schema.dump(sanitario)
        # resultado = sanitario_schema.dump(sanitario)
        return jsonify({"Mensaje": "Sanitario encontrado", "sanitario": resultado})
    else:
        return jsonify({"Mensaje": "No se encontró el sanitario", "sanitarioId": sanitario_id}), 404


# @app.route('/sanitarios/rubro', methods=['GET'])
# def obtener_rubro_sanitario():
#     try:
#         estado_sanitario = request.args.get('estado_sanitario')

#         # Consultar todos los sanitarios
#         sanitarios_query = Sanitario.query

#         # Filtrar por estado_sanitario si está presente en los argumentos de la solicitud
#         if estado_sanitario:
#             sanitarios_query = sanitarios_query.filter_by(estado_sanitario=estado_sanitario)

#         # Ejecutar la consulta y obtener los resultados
#         sanitarios = sanitarios_query.all()

#         # Verificar si se encontraron sanitarios
#         if not sanitarios:
#             return jsonify({"Mensaje": "No se encontraron sanitarios"}), 404

#         # Serializar los resultados usando simple_sanitario_schema
#         result = rubro_sanitario_schema.dump(sanitarios)

#         # Devolver la respuesta JSON
#         return jsonify(result)

#     except Exception as e:
#         # Manejar cualquier error y devolver una respuesta de error
#         return jsonify({"Mensaje": "Error al obtener rubro de Sanitario", "Error": str(e)}), 500


# Actualizar un sanitario por su ID
@app.route('/sanitarios/<sanitario_id>', methods=['PUT'])
def sanitario_actualizar(sanitario_id):
    sanitario = Sanitario.query.get(sanitario_id)

    if not sanitario or not sanitario.activo:
        return jsonify({"Mensaje": "Sanitario no encontrado"}), 404

    json_data = request.get_json()

    if not json_data:
        return jsonify({"Mensaje": "No se envió información"}), 400

    try:
        data = sanitario_schema.load(json_data, partial=True)
    except ValidationError as err:
        return jsonify(err.messages), 422

    # Actualizar los campos del sanitario
    sanitario.granja_id = data['granja_id']
    sanitario.especie_id = data['especie_id']
    sanitario.rubro = data['rubro']
    sanitario.fecha_vencimiento = data['fecha_vencimiento']
    sanitario.frascos = data['frascos']
    sanitario.marca = data['marca']
    sanitario.dosis = data['dosis']
    sanitario.ml_animal = data['ml_animal']
    sanitario.estado_sanitario = data['estado_sanitario']
    sanitario.observaciones = data.get('observaciones')
    sanitario.saldo=data['frascos']*data['dosis']

    db.session.commit()

    return jsonify({"Mensaje": "Sanitario actualizado exitosamente"})


# Eliminar un sanitario por su ID
@app.route('/sanitarios/<sanitario_id>', methods=['DELETE'])
def sanitario_eliminar(sanitario_id):
    sanitario = Sanitario.query.get(sanitario_id)

    if not sanitario or not sanitario.activo:
        return jsonify({"Mensaje": "Sanitario no encontrado"}), 404

    sanitario.activo = False
    db.session.commit()

    return jsonify({"Mensaje": "Sanitario eliminado exitosamente"})


# Manejar errores 404
@app.errorhandler(404)
def no_encontrado(error):
    return jsonify({"Mensaje": "Recurso no encontrado"}), 404