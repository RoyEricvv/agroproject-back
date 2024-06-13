from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.MateriaSeca import MateriaSeca, MateriaSecaSchema
from aplicacion.modelo.Departamento import Departamento
from aplicacion.modelo.Insumo import Insumo

#Servicio para listar todas las materias secas
@app.route('/materiaSeca/<insumo_id>/all', methods=['GET'])
def materia_seca_todos(insumo_id):
    if insumo_id == '0':
        #Se crea la lista de toda la materia seca.
        materia_secas = MateriaSeca.query.filter(MateriaSeca.activo==True).order_by(MateriaSeca.departamento_id).all()
    else:
        #Se crea la lista de toda la materia seca de un insumo.
        materia_secas = MateriaSeca.query.filter(MateriaSeca.activo==True).filter(MateriaSeca.insumo_id == insumo_id).order_by(MateriaSeca.departamento_id).all()
    if len(materia_secas) > 0:  
        #Se serializa la información a retornar
        materia_secas_schema = MateriaSecaSchema(many=True)
        data = materia_secas_schema.dump(materia_secas)
    
        return {"Mensaje": "Lista de materia seca", "materiaSeca": data}
    else:
        return {"Mensaje": "No se encontró materia seca relacionada", "insumoId": insumo_id},404

#Servicio para actualizar una materia seca mediante ID
@app.route('/materiaSeca/update', methods=['POST'])
def materia_seca_actualizar():

    # Obtener argumentos 
    json_data = request.get_json()
    print('Data :',json_data)
    if not json_data:
        return {"Mensaje": "No se envío data"}, 404

    #Se busca contenido nutricional en base de datos
    materia_seca_actualizar = (
        MateriaSeca.query.filter(MateriaSeca.departamento_id == json_data["departamento_id"]).filter(MateriaSeca.insumo_id == json_data["insumo_id"]).filter(MateriaSeca.activo==True)
        .one_or_none()
    )

    if materia_seca_actualizar is None:
        return {"Mensaje": "Materia Seca no existe"}, 404

    departmento_existe = Departamento.query.get(json_data["departamento_id"])

    if departmento_existe is None:
        return {"Mensaje": "El id del nutriente no se encuentra registrado"}, 400

    insumo_existe = Insumo.query.get(json_data["insumo_id"])

    if insumo_existe is None:
        return {"Mensaje": "El id del insumo no se encuentra registrado"}, 400


    materia_seca_actualizar.porcentaje = json_data["porcentaje"]
    materia_seca_actualizar.fecha_modificacion = dt.now()

    db.session.merge(materia_seca_actualizar)
    db.session.commit()

    return {"Mensaje": "Se actualizó materia seca."}