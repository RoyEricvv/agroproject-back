from flask import request, make_response, abort
from datetime import datetime as dt
from flask import current_app as app
from aplicacion import db
from aplicacion.modelo.Animal import Animal, AnimalSchema
from aplicacion.modelo.HistorialCrecimiento import HistorialCrecimiento
from aplicacion.modelo.RacionFormulada import RacionFormulada
from aplicacion.modelo.EtapaVida import EtapaVida
from marshmallow import ValidationError
from sqlalchemy import desc

#Servicio para listar data de reportes
@app.route('/reporte/<animal_id>', methods=['GET'])
def reporte_animal_Peso(animal_id):
    animal=Animal.query.filter(Animal.activo==True).filter(Animal.id == animal_id).one_or_none()
    respuestaPeso=[]
    respuestaGanancia=[]
    respuestConsumo=[]
    listaHistorial=HistorialCrecimiento.query.filter(HistorialCrecimiento.activo==True).filter(HistorialCrecimiento.animal_id==animal_id).order_by(HistorialCrecimiento.semana_crecimiento).all()
    cabeceraPeso=["Semana","Registrado","Recomendado"]
    cabeceraGanancia=["Semana","Peso Ganado"]
    cabeceraConsumo=["Semana","Consumo"]
    respuestaPeso.append(cabeceraPeso)
    respuestaGanancia.append(cabeceraGanancia)
    respuestConsumo.append(cabeceraConsumo)
    pesoAnterior=0
    for historia in listaHistorial:
        recomendado=EtapaVida.query.filter(EtapaVida.activo==True).filter(EtapaVida.especie_id == animal.especie_id).filter(EtapaVida.semana_vida_referencial_inicial < historia.semana_crecimiento).filter(EtapaVida.semana_vida_referencial_final >= historia.semana_crecimiento).one_or_none()
        respuestaPeso.append([str(historia.semana_crecimiento),round(historia.peso_total/historia.cantidad,2),recomendado.peso_vivo_referencial])
        pesoGanado=round(historia.peso_total - pesoAnterior,2)
        respuestaGanancia.append([str(historia.semana_crecimiento),round(pesoGanado/historia.cantidad,2)])
        pesoAnterior=historia.peso_total

        raciones=RacionFormulada.query.filter(RacionFormulada.animal_id==animal_id).filter(RacionFormulada.activo==True).filter(RacionFormulada.etapa_semana==historia.semana_crecimiento).filter(RacionFormulada.numero_de_aplicaciones > 0).all()
        cantidad_racion=0
        if len(raciones)>0:
            for racion in raciones:
                cantidad_racion = cantidad_racion + round(racion.cantidad_total * racion.numero_de_aplicaciones,2)
        respuestConsumo.append([str(historia.semana_crecimiento),round(cantidad_racion/historia.cantidad,2)])

    return {"Mensaje": "Data de reporte", "reporte": respuestaPeso,"reporteGanancia":respuestaGanancia,"reporteConsumo":respuestConsumo}