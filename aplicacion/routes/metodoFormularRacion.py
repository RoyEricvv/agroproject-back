from sqlalchemy.sql.expression import false
from aplicacion.modelo.Insumo import Insumo
from flask import request, make_response, abort
from flask import current_app as app
from aplicacion import fields
from aplicacion import db
from datetime import datetime as dt
from aplicacion.modelo.RequerimientoNutricional import RequerimientoNutricional, RequerimientoNutricionalSchema
from aplicacion.modelo.Inventario import Inventario
from aplicacion.modelo.Animal import Animal
from aplicacion.modelo.RacionFormulada import RacionFormulada
from aplicacion.modelo.NutrienteRacion import NutrienteRacion
from aplicacion.modelo.ContenidoRacion import ContenidoRacion
from aplicacion.modelo.ContenidoNutricional import ContenidoNutricional
from aplicacion.modelo.Aditivo import Aditivo
from marshmallow import ValidationError, Schema
from aplicacion.modelo.FormularRaciones import verificar_inventario_inicial, verificar_inventario_final, disminuir_inventario, algoritmo_formular_raciones

#Clase auxiliar para crear lista de inventario
class listaInvetarioSchema(Schema):
    inventario = fields.Nested('InventarioSchema', many=True)

#Servicio para verificar Inventario Inicial
@app.route('/funcionFormular/<usuario_Id>/RevisarInventario', methods=['GET'])
def revisar_inventario(usuario_Id):
    estado, inventarios = verificar_inventario_inicial(usuario_Id)
    if estado == 0:
        return {"Mensaje": "No hay inventario disponible", "inventario": inventarios}, 404
    else:
        return {"Mensaje": "Hay inventario disponible"}

#Servicio para registrar Ración con Insumo limitado
@app.route('/funcionFormular/InsumoEscazo', methods=['POST'])
def insumo_escazo():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400
    
    racion = json_data["racion"] #Información de Cantidad y Especie
    contenido = json_data["inventario"] 

    racion_formulada_nuevo = RacionFormulada(
        activo=True,
        costo_total=0,
        costo_aditivo=0,
        costo_aditivo_kg=0,
        costo_total_Kg=0,
        numero_de_aplicaciones=0,
        cantidad_animales=racion["cantidad_animales"],
        tipo = racion["tipo"],
        etapa_semana = racion["etapa_semana"],
        fuente_id= racion["fuente_id"],
        cantidad_total=racion["cantidad_total"],
        favorito=False,
        aplicar=False,
        usuario_id=racion["usuario_id"],
        animal_id=racion["animal_id"],
        estado_racion= 0, #Insumo Escazo
        fecha_creacion=dt.now(),
        fecha_modificacion=dt.now()
    )
    db.session.add(racion_formulada_nuevo)  # Añade un nuevo registro a la base de datos
    db.session.flush()
    db.session.commit()  # Guarda todos los cambios

    for insumo in contenido:
        contenido_racion_nuevo = ContenidoRacion(
            activo=True,
            cantidad_total=0,
            costo_total=0,
            costo_aditivo=0,
            insumo_id=insumo["insumo_id"],
            racion_formulada_id=racion_formulada_nuevo.id,
            fecha_creacion=dt.now(),
            fecha_modificacion=dt.now()
        )
        db.session.add(contenido_racion_nuevo)  # Añade un nuevo registro a la base de datos
        db.session.commit()  # Guarda todos los cambios
    return {"Mensaje": "Se creo ración escaza" }

#Servicio para registrar Ración con Insumo Disponible
@app.route('/funcionFormular/InsumoDisponible', methods=['POST'])
def insumo_disponible():
    # Obtener argumentos 

    json_data = request.get_json()
    print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400
    
    racion = json_data["racion"] #Información de Cantidad y Especie

    racion_formulada_nuevo = RacionFormulada(
        activo=True,
        costo_total=0,
        costo_aditivo=0,
        costo_aditivo_kg=0,
        costo_total_Kg=0,
        numero_de_aplicaciones=0,
        cantidad_animales=racion["cantidad_animales"],
        tipo = racion["tipo"],
        etapa_semana = racion["etapa_semana"],
        fuente_id= racion["fuente_id"],
        cantidad_total=racion["cantidad_total"],
        favorito=False,
        aplicar=True,
        usuario_id=racion["usuario_id"],
        animal_id=racion["animal_id"],
        estado_racion= 1, #Insumo Disponible
        fecha_creacion=dt.now(),
        fecha_modificacion=dt.now()
    )
    db.session.add(racion_formulada_nuevo)  # Añade un nuevo registro a la base de datos
    db.session.flush()
    db.session.commit()  # Guarda todos los cambios

    return {"Mensaje": "Se creo ración formulada" , "racionId":racion_formulada_nuevo.id}

#Servicio para registrar Ración con Insumo Disponible
@app.route('/funcionFormular/Algoritmo', methods=['POST'])
def algoritmo():
    #Lista de Insumos disponibles en el inventario
    json_data = request.get_json()
    #print('Data :', json_data)
    if not json_data:
        return {"Mensaje": "No se envío información"}, 400

    usuario_id = json_data["usuario_id"]
    racion_formulada_id = json_data["racion_formulada_id"]
    etapa_vida_id = json_data["etapa_vida_id"]
    cantidad_por_formular = json_data["cantidad_por_formular"]
    departamento_id = json_data["departamento_id"]
    fuente_id = json_data["fuente_id"]
    lista_inventario = json_data["lista_inventario"]
    aproximar = json_data["aproximar"]# 0: Sin Holguras, 1:Con Holguras
    #Leer inventario
    #lista_inventario = Inventario.query.filter(Inventario.usuario_id == usuario_id).order_by(Inventario.insumo_id).all()

    #Leer Requerimiento Especie
    requerimiento_nutricionales = RequerimientoNutricional.query.filter(RequerimientoNutricional.activo==True).filter(RequerimientoNutricional.etapa_vida_id == etapa_vida_id).filter(RequerimientoNutricional.departamento_id == departamento_id).filter(RequerimientoNutricional.fuente_id == fuente_id).order_by(RequerimientoNutricional.nutriente_id).all()

    requerimiento_nutricional_schema = RequerimientoNutricionalSchema(many=True)
    requerimiento_especie = requerimiento_nutricional_schema.dump(requerimiento_nutricionales)

    estado,lista_cantidad_requerida, costo_Total = algoritmo_formular_raciones(etapa_vida_id, lista_inventario, requerimiento_especie, cantidad_por_formular,aproximar)
    print(costo_Total)

    if estado:
        costo_calculado = 0

        cantidad_aditivo_total=0
        #Crear contenido de la ración , insumos
        for i in range(len(lista_inventario)):
            contenido_racion = ContenidoRacion(
                activo=True,
                cantidad_porcentual=round(lista_cantidad_requerida[i]/cantidad_por_formular * 100,2),
                cantidad_total=round(lista_cantidad_requerida[i],2),
                costo_total=round(lista_inventario[i]["costo_total"] / lista_inventario[i]["peso_total"] *lista_cantidad_requerida[i],2),
                insumo_id=lista_inventario[i]["insumo_id"],
                racion_formulada_id=racion_formulada_id,
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            costo_calculado = round(lista_inventario[i]["costo_total"] / lista_inventario[i]["peso_total"] * lista_cantidad_requerida[i],2) + costo_calculado
            db.session.add(contenido_racion)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

        #Crear Nutriente Ración
        for requerimiento in requerimiento_especie:
            valor_acumulado = 0
            for i in range(len(lista_inventario)):
                if lista_cantidad_requerida[i] > 0:
                    contenido_nutriente=ContenidoNutricional.query.filter(ContenidoNutricional.activo==True).filter(ContenidoNutricional.nutriente_id == requerimiento['nutriente_id']).filter(ContenidoNutricional.insumo_id == lista_inventario[i]["insumo_id"]).one_or_none()
                    if contenido_nutriente is not None:
                        valor_acumulado = valor_acumulado + round(lista_cantidad_requerida[i]*contenido_nutriente.cantidad,2)

            nutriente_racion = NutrienteRacion(
                activo=True,
                cantidad_racion=round(valor_acumulado / cantidad_por_formular,2),
                cantidad_fuente=round(requerimiento['cantidad'],2),
                nutriente_id=requerimiento['nutriente_id'],
                racion_id=racion_formulada_id,
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            db.session.add(nutriente_racion)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

        
        #Crear contenido de la ración , aditivos
        inventario_aditivo=Inventario.query.join(Insumo).filter(Insumo.activo==True).filter(Inventario.activo==True).filter(Inventario.usuario_id == usuario_id).filter(Insumo.es_aditivo == True).all()
        costo_aditivo_total=0
        cantidad_aditivo_total=0
        if len(inventario_aditivo) > 0:
            for item in inventario_aditivo:
                aditivos_relacion=Aditivo.query.filter(Aditivo.activo==True).filter(Aditivo.aditivo_id == item.insumo_id).all()
                costo_aditivo_contenido=0
                cantidad_aditivo_contenido=0
                if len(aditivos_relacion) > 0:
                    for aditivo in aditivos_relacion:
                        insumo_id=aditivo.insumo_id
                        insumo_afectado=ContenidoRacion.query.filter(ContenidoRacion.activo==True).filter(ContenidoRacion.insumo_id==insumo_id).filter(ContenidoRacion.racion_formulada_id==racion_formulada_id).one_or_none()
                        if insumo_afectado is not None:
                            cantidad_aditivo_contenido += round(insumo_afectado.cantidad_total * aditivo.relacion / 100,2)
                            costo_aditivo_contenido = round(cantidad_aditivo_contenido * item.costo_unitario,2)
                    costo_aditivo_total += costo_aditivo_contenido
                    cantidad_aditivo_total += cantidad_aditivo_contenido

                    if cantidad_aditivo_total > 0:
                        aditivo_racion = ContenidoRacion(
                                    activo=True,
                                    cantidad_total=cantidad_aditivo_contenido,
                                    costo_total=costo_aditivo_contenido,
                                    insumo_id=item.insumo_id,
                                    racion_formulada_id=racion_formulada_id,
                                    fecha_creacion=dt.now(),
                                    fecha_modificacion=dt.now()
                                )
                        db.session.add(aditivo_racion)  # Añade un nuevo registro a la base de datos
                        db.session.commit()  # Guarda todos los cambios


        #Actualizar ración formulada
        racion_formulada_actualizar = RacionFormulada.query.filter(RacionFormulada.activo==True).filter(RacionFormulada.id == racion_formulada_id).one_or_none()
        racion_formulada_actualizar.costo_total = round(costo_calculado,2)
        racion_formulada_actualizar.costo_total_Kg = round(costo_calculado/cantidad_por_formular,2)
        racion_formulada_actualizar.costo_aditivo = round(costo_aditivo_total,2)
        racion_formulada_actualizar.costo_aditivo_kg = round(round((costo_aditivo_total+costo_calculado)/(cantidad_por_formular + cantidad_aditivo_total),2) - round(costo_calculado/cantidad_por_formular,2),2)


        if aproximar == 1:
            racion_formulada_actualizar.estado_racion = 5 #Ración Elaborada Con Holgura
        else:
            racion_formulada_actualizar.estado_racion = 2 #Ración Elaborada Sin Holgura

        db.session.merge(racion_formulada_actualizar)
        db.session.commit()

        return {"Mensaje": "Formulación correcta"}
    else:
        #Actualizar ración formulada Infeasible
        racion_formulada_actualizar = RacionFormulada.query.filter(RacionFormulada.activo==True).filter(RacionFormulada.id == racion_formulada_id).one_or_none()
        racion_formulada_actualizar.costo_total = 0
        racion_formulada_actualizar.costo_aditivo = 0
        racion_formulada_actualizar.estado_racion = 4 #Ración Infeasible
        racion_formulada_actualizar.aplicar = False

        db.session.merge(racion_formulada_actualizar)
        db.session.commit()

        #Crear contenido de la ración Infeasible con los insumos
        for i in range(len(lista_inventario)):
            contenido_racion = ContenidoRacion(
                activo=True,
                cantidad_porcentual=0,
                cantidad_total=0,
                costo_total=0,
                insumo_id=lista_inventario[i]["insumo_id"],
                racion_formulada_id=racion_formulada_id,
                fecha_creacion=dt.now(),
                fecha_modificacion=dt.now()
            )
            db.session.add(contenido_racion)  # Añade un nuevo registro a la base de datos
            db.session.commit()  # Guarda todos los cambios

        return {"Mensaje": "Respuesta infactible"},404

#Servicio para Aplicar Ración Formulada
@app.route('/funcionFormular/<racion_Id>/<aditivos>/Aplicar', methods=['GET'])
def aplicar_racion(racion_Id,aditivos):
    racion_formulada_actualizar = (
        RacionFormulada.query.filter(RacionFormulada.activo==True).filter(RacionFormulada.id == racion_Id)
        .one_or_none()
    )
    if racion_formulada_actualizar is None:
        return {"Mensaje": "Racion formulada no existe"}, 404

    if racion_formulada_actualizar.aplicar == False:
        return {"Mensaje": "Racion formulada no aplicable"}, 404
    aditivos=int(aditivos)

    if aditivos == 0:
        #Se lista solo insumos
        lista_contenido_requerido = ContenidoRacion.query.join(Insumo).filter(ContenidoRacion.activo==True).filter(Insumo.activo==True).filter(Insumo.es_aditivo == False).filter(ContenidoRacion.racion_formulada_id == racion_Id).order_by(ContenidoRacion.insumo_id).all()
    else:
        #Se lista insumos y aditivos
        lista_contenido_requerido = ContenidoRacion.query.filter(ContenidoRacion.activo==True).filter(ContenidoRacion.racion_formulada_id == racion_Id).order_by(ContenidoRacion.insumo_id).all()
    
    
    lista_inventario = []

    for contenido in lista_contenido_requerido:
        insumo= Inventario.query.filter(Inventario.activo==True).filter(Inventario.insumo_id == contenido.insumo_id).filter(Inventario.usuario_id == racion_formulada_actualizar.usuario_id).one_or_none()
        if insumo is None:
            return {"Mensaje": "No se cuenta con el siguiente insumo", "insumo": contenido.insumo}, 404
        else:
            lista_inventario.append(insumo)
        

    estado, inventario = verificar_inventario_final(lista_inventario, lista_contenido_requerido)
    if estado == 0:
        return {"Mensaje": "No hay inventario disponible", "inventario": inventario}, 404
    else:
        nuevo_inventario = disminuir_inventario(lista_inventario, lista_contenido_requerido)
        for inventario in nuevo_inventario:
            db.session.merge(inventario)
            db.session.commit()

        racion_formulada_actualizar.estado_racion = 3
        racion_formulada_actualizar.numero_de_aplicaciones = 1 + racion_formulada_actualizar.numero_de_aplicaciones
        racion_formulada_actualizar.fecha_modificacion = dt.now()

        db.session.merge(racion_formulada_actualizar)
        db.session.commit()

        animal_relacionado = Animal.query.filter(Animal.activo==True).filter(Animal.id == racion_formulada_actualizar.animal_id).one_or_none()
        if aditivos == 0:
            animal_relacionado.costo_racion +=racion_formulada_actualizar.costo_total
        else:
            animal_relacionado.costo_racion +=racion_formulada_actualizar.costo_total + racion_formulada_actualizar.costo_aditivo

        animal_relacionado.costo_kg_animal = round(animal_relacionado.costo_racion / animal_relacionado.peso_animal_actual,2)

        db.session.merge(animal_relacionado)
        db.session.commit()

        return {"Mensaje": "Se actualizó inventario"}

