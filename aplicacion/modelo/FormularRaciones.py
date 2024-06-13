from aplicacion.modelo.Inventario import Inventario, InventarioSchema
from aplicacion.modelo.ContenidoNutricional import ContenidoNutricional, ContenidoNutricionalSchema
from aplicacion.modelo.Restriccion import Restriccion
from scipy.optimize import linprog

def verificar_inventario_inicial(usuario_Id):
    inventarios = Inventario.query.filter(Inventario.activo==True).filter(Inventario.usuario_id == usuario_Id).filter(Inventario.peso_total == 0).order_by(Inventario.insumo_id).all()
    if len(inventarios) > 0:
        #Se serializa la información a retornar
        inventario_schema = InventarioSchema(many=True)
        data = inventario_schema.dump(inventarios)
        return 0, data
    else:
        return 1, []

def construir_lista_objetivo(lista_inventario, holgura_tamano,aproximar):
    lista_objetivo = []
    for item  in lista_inventario:
        #Precio por kg de cada insumo      
        precio_por_kilogramo = round(item["costo_unitario"],2)
        lista_objetivo.append(precio_por_kilogramo)
    #Si se aproxima la ración, se añade costos muy altos para las holguras
    if aproximar == 1 :
        for i in range (holgura_tamano):
            lista_objetivo.append(1000000)
    print("Objetivo ",lista_objetivo)
    return lista_objetivo
    
def construir_lista_límite(lista_inventario, etapa_vida_Id,cantidadRacion,holgura_tamano,aproximar):
    lista_limites = []
    #Se añade el límite de cantidad de cada insumo
    for item  in lista_inventario:
        restricion= Restriccion.query.filter(Restriccion.activo==True).filter(Restriccion.insumo_id == item["insumo_id"]).filter(Restriccion.etapa_vida_id == etapa_vida_Id).one_or_none()
        if restricion is not None: 
            item = round (restricion.porcentaje_permitido*cantidadRacion / 100,5)
        lista_limites.append((0, item))
    #Si se aproxima la ración, se añade límites a las holguras
    if aproximar == 1 :
        for i in range(holgura_tamano):
            lista_limites.append((0, 0.1))
    print("Limites del insumo ",lista_limites)
    return lista_limites

def construir_lista_restriccion(lista_requerimiento, cantidadMSRacion):
    lista_restriccion = []
    #Para calcularlo se requiere transformar todos los requerimientos a menor o igual
    for requerimiento in lista_requerimiento:
        #Si el tipo de requerimiento es máximo se multiplicará por uno, pero si es mínimo se invertira el signo
        prefijo = 1 if requerimiento['tipo_requerimiento'] == 1 else -1
        #Si la unidad del requerimiento es porcentaje, se multiplicará por la cantidad de la ración, sino se multiplicará por la unidad
        sufijo = (cantidadMSRacion / 100) if requerimiento['nutriente']['unidad'] == 0 else cantidadMSRacion
        requisito = prefijo*requerimiento['cantidad']*sufijo
        requisito = round(requisito,5)
        lista_restriccion.append(requisito)
    print("Restricción ",lista_restriccion)
    return lista_restriccion

def construir_matriz_ecuaciones(lista_nutriente, lista_insumos_id, contenido_nutricional, holgura_tamano,aproximar):
    lista_lista_ecuacion = []

    fila=0
    #Nutriente guarda el id y tipo de requerimiento
    for nutriente in lista_nutriente:
        lista_ecuacion = []
        for insumo_id in lista_insumos_id:
            contenido = next((i for i in contenido_nutricional if i['nutriente_id'] == nutriente.id and i['insumo_id'] == insumo_id), None)
            #Si el insumo no cuenta con el nutriente se coloca un cero
            if contenido is None:
                lista_ecuacion.append(0)
            else:
                cantida = contenido['cantidad'] / 100 if nutriente.unidad == 0 else contenido['cantidad']
                cantida = round(cantida,5)
                if nutriente.tipo_requerimiento == 1:
                    lista_ecuacion.append(cantida)
                else:
                    lista_ecuacion.append(-1*cantida)
        #Si se aproxima la ración, se le coloca un valor que permitadar flexibilidad al requerimiento
        if aproximar == 1 :
            for columna in range(holgura_tamano):
                if columna == fila and not nutriente.esencial:
                    if nutriente.tipo_requerimiento == 1:
                        lista_ecuacion.append(1)
                    else:
                        lista_ecuacion.append(-1)
                else:
                    lista_ecuacion.append(0)
            
        lista_lista_ecuacion.append(lista_ecuacion)
        fila = fila + 1
        #print("Linea Matríz", lista_ecuacion)
    print("Matriz ",lista_lista_ecuacion)
    return lista_lista_ecuacion

def ejecutar_optimizacion(cantidadMSRacion, lista_objetivo, lista_restriccion, lista_lista_ecuacion,lista_limites, holgura_tamano,aproximar):
    limiteIgualdadIzq = []
    limiteCantidad = []
    #Se añade la restricción de que la suma de raciones sume la cantidad a formular
    for i in range(len(lista_objetivo)-(holgura_tamano * aproximar)):
        limiteCantidad.append(1)
    #Si se aproxima la ración, Registrar valor cero de las holguras
    if aproximar == 1 :
        for i in range(holgura_tamano):
            limiteCantidad.append(0)
    limiteIgualdadIzq.append(limiteCantidad)

    limiteIgualdadDer = []
    limiteIgualdadDer.append(cantidadMSRacion)

    print("limiteIgualdadIzq", limiteIgualdadIzq)
    print("limiteIgualdadDer", limiteIgualdadDer)
    objetivo = linprog(c=lista_objetivo, A_ub=lista_lista_ecuacion, b_ub=lista_restriccion, A_eq=limiteIgualdadIzq, b_eq=limiteIgualdadDer , bounds=lista_limites, method='interior-point', options={'presolve': False})

    return objetivo


def verificar_inventario_final(lista_inventario, lista_contenido_requerido):
    lista_insumo_escaso = []
    for i in range(len(lista_contenido_requerido)):
        if lista_inventario[i].peso_total < lista_contenido_requerido[i].cantidad_total:
            lista_insumo_escaso.append(lista_inventario[i])
    
    if len(lista_insumo_escaso) > 0:
        return 0, lista_insumo_escaso
    return 1, []


def disminuir_inventario(lista_inventario, lista_contenido_requerido):
    for i in range(len(lista_contenido_requerido)):
        peso_total_nuevo = round(lista_inventario[i].peso_total - lista_contenido_requerido[i].cantidad_total, 2)
        costo_total = round(peso_total_nuevo * lista_inventario[i].costo_unitario, 2)
        lista_inventario[i].peso_total = peso_total_nuevo
        lista_inventario[i].costo_total = costo_total
    return lista_inventario

class NutrienteAux:
    pass
class ContenidoRacionAux:
    pass

def algoritmo_formular_raciones(etapa_vida_id, lista_inventario, lista_requerimiento, cantidadMSRacion,aproximar):
    #Se construye la lista de insumos y nutrientes necesarios para el proceso
    lista_insumos_id = []
    for item in lista_inventario:
        lista_insumos_id.append(item["insumo_id"])
    lista_nutriente = []
    for item in lista_requerimiento:
        nutriente = NutrienteAux()
        nutriente.id = item['nutriente_id']
        nutriente.nombre = item['nutriente']['nombre']
        nutriente.tipo_requerimiento = item['tipo_requerimiento']
        nutriente.esencial = item['esencial']
        nutriente.unidad = item['nutriente']['unidad']
        lista_nutriente.append(nutriente)
    #Se obtienen todos los contenidos nutricionales de los insumos
    contenido_nutricional_query = ContenidoNutricional.query.filter(ContenidoNutricional.activo==True).filter(ContenidoNutricional.insumo_id.in_(lista_insumos_id)).order_by(ContenidoNutricional.nutriente_id).all()
    contenido_nutricional_schema = ContenidoNutricionalSchema(many=True)
    contenido_nutricional = contenido_nutricional_schema.dump(contenido_nutricional_query)
    #Se obtiene el tamaño de los elementos de la holgura, el cual es igual al tamaño de nutrientes requeridos
    holgura_tamano = len(lista_requerimiento)
    #Se construye la lista que representa la función objetivo
    lista_objetivo = construir_lista_objetivo(lista_inventario,holgura_tamano,aproximar)
    #Se construye la lista que representa las restricciones
    lista_restriccion = construir_lista_restriccion(lista_requerimiento, cantidadMSRacion)
    #Se cosntruye la lista que representa las cantidades de nutrientes presentes en los insumos
    lista_lista_ecuaciones = construir_matriz_ecuaciones(lista_nutriente, lista_insumos_id, contenido_nutricional,holgura_tamano,aproximar)
    #Se construye la lista de límite de las variables
    lista_limites = construir_lista_límite(lista_inventario,etapa_vida_id,cantidadMSRacion,holgura_tamano,aproximar)
    #Se ejecuta el solver
    objetivo = ejecutar_optimizacion(cantidadMSRacion,lista_objetivo, lista_restriccion, lista_lista_ecuaciones,lista_limites,holgura_tamano,aproximar)
    #Se obtiene el costo de la ración obtenida de la función
    costo_racion = objetivo.fun
    print("Costo",costo_racion)
    #Se obtiene el estado de la función
    exito = objetivo.success
    print("Se logró encontrar ",exito)
    #Se obtiene el mensaje de la función
    msj = objetivo.message
    print("Mensaje de la función ",msj)
    #Se obtiene la cantidad de insumos requerido para la ración
    lista_inventario_requerido = objetivo.x
    print("Cantidad Requerida ",lista_inventario_requerido)
    #Se realiza una verificación final de los insumos disponibles
    # estadofinal, lista_inventario_escaso = verificar_inventario_final(lista_inventario, lista_inventario_requerido)
    return exito, lista_inventario_requerido, costo_racion


