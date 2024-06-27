from flask import request, make_response, abort, jsonify
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Rubro import Rubro, RubroSchema
from marshmallow import ValidationError

# Instanciar esquemas
rubro_schema = RubroSchema()
rubros_schema = RubroSchema(many=True)

@app.route('/rubros', methods=['GET'])
def get_rubros():
    estado_rubro = request.args.get('estado_rubro', None)
    query = Rubro.query.filter_by(activo=True)

    if estado_rubro:
        query = query.filter_by(tipo=estado_rubro)

    rubros = query.all()
    data = rubros_schema.dump(rubros)
    return jsonify(data)

@app.route('/rubro/<int:id>', methods=['GET'])
def get_rubro(id):
    estado_rubro = request.args.get('estado_rubro', None)
    query = Rubro.query.filter_by(id=id, activo=True)

    if estado_rubro:
        query = query.filter_by(tipo=estado_rubro)

    rubros = query.all()
    data = rubros_schema.dump(rubros)
    return jsonify(data)

@app.route('/rubro', methods=['POST'])
def add_rubro():
    try:
        data = request.json

        # Crear una instancia de modelo Rubro con los datos del JSON
        nuevo_rubro = Rubro(
            nombre=data['nombre'],
            activo=data.get('activo', True),
            tipo=data['tipo']
        )

        # Agregar el nuevo rubro a la sesión de la base de datos
        db.session.add(nuevo_rubro)
        db.session.commit()

        # Serializar el objeto Rubro a JSON usando el esquema RubroSchema
        rubro_schema = RubroSchema()
        result = rubro_schema.dump(nuevo_rubro)

        # Devolver el JSON del nuevo rubro con código de estado 201 (Created)
        return jsonify(result), 201


    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/rubro/<int:id>', methods=['PUT'])
def update_rubro(id):
    try:
        data = request.json
        rubro = Rubro.query.get(id)
        if not rubro:
            return jsonify({'message': 'Rubro not found'}), 404
        
        rubro = rubro_schema.load(data, instance=rubro, partial=True)
        db.session.commit()
        return rubro_schema.jsonify(rubro), 200
    except ValidationError as err:
        return jsonify(err.messages), 400

@app.route('/rubro/<int:id>', methods=['DELETE'])
def delete_rubro(id):
    rubro = Rubro.query.get(id)
    if not rubro:
        return jsonify({'message': 'Rubro not found'}), 404
    
    db.session.delete(rubro)
    db.session.commit()
    return jsonify({'message': 'Rubro deleted successfully'}), 200