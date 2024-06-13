import sys
import unittest
from aplicacion.modelo.FormularRaciones import *
from aplicacion.modelo.Inventario import Inventario
from aplicacion.modelo.ContenidoRacion import ContenidoRacion

class NutrienteAux:
    pass

class TestFormularRaciones(unittest.TestCase):
    #Datos Prueba 1
    lista_inventario = [{'costo_unitario':6},{'costo_unitario':6}]
    #Datos Prueba 2
    lista_requerimiento = [{'tipo_requerimiento':0,'cantidad':10,'nutriente':{'nombre':'PC','unidad':0}},{'tipo_requerimiento':0,'cantidad':20,'nutriente':{'nombre':'Na','unidad':0}}]
    cantidadMSRacion =10
    #Datos Prueba 3
    lista_nutriente = []
    nut1 = NutrienteAux()
    nut1.id = 1
    nut1.nombre= 'PC'
    nut1.tipo_requerimiento = 0
    nut1.unidad = 0
    lista_nutriente.append(nut1)
    nut2 = NutrienteAux()
    nut2.id = 2
    nut2.nombre= 'NA'
    nut2.tipo_requerimiento = 0
    nut2.unidad = 0
    lista_nutriente.append(nut2)

    lista_insumos_id = [1,2]
    
    contenido_nutricional = [{'nutriente_id':1,'insumo_id':1,'cantidad':10},{'nutriente_id':2,'insumo_id':1,'cantidad':15},{'nutriente_id':1,'insumo_id':2,'cantidad':13},{'nutriente_id':2,'insumo_id':2,'cantidad':10}]
    #Datos Prueba 4, 5 y 6
    lista_inventario_inicial = []
    inv1 = Inventario()
    inv1.peso_total = 10
    inv1.costo_unitario = 2
    lista_inventario_inicial.append(inv1)
    inv2 = Inventario()
    inv2.peso_total = 10
    inv2.costo_unitario = 2
    lista_inventario_inicial.append(inv2)

    lista_inventario_escaso = []
    inv1 = Inventario()
    inv1.peso_total = 1
    inv1.costo_unitario = 2
    lista_inventario_escaso.append(inv1)
    inv2 = Inventario()
    inv2.peso_total = 1
    inv2.costo_unitario = 2
    lista_inventario_escaso.append(inv2)

    lista_inventario_requerido = []
    item1 = ContenidoRacion()
    item1.insumo_id =1
    item1.cantidad_total = 2
    lista_inventario_requerido.append(item1)
    item2 = ContenidoRacion()
    item2.insumo_id =2
    item2.cantidad_total = 3
    lista_inventario_requerido.append(item2)

    def test_construir_lista_objetivo(self):
        lista_objetivo = construir_lista_objetivo(self.lista_inventario)
        self.assertEqual(len(self.lista_inventario),len(lista_objetivo))
    
    def test_construir_lista_restriccion(self):
        lista_restriccion = construir_lista_restriccion(self.lista_requerimiento,self.cantidadMSRacion)
        self.assertEqual(len(self.lista_requerimiento),len(lista_restriccion))
    
    def test_construir_matriz_ecuaciones(self):
        lista_lista_ecuacion = construir_matriz_ecuaciones(self.lista_nutriente, self.lista_insumos_id, self.contenido_nutricional)
        self.assertEqual(len(lista_lista_ecuacion),len(self.lista_nutriente))
        for item in lista_lista_ecuacion:
            self.assertEqual(len(item), len(self.lista_insumos_id))

    def test_verificar_inventario_final_no_escaso(self):
        estado, lista_insumo_escaso = verificar_inventario_final(self.lista_inventario_inicial, self.lista_inventario_requerido)
        self.assertEqual(estado,1)
        self.assertEqual(len(lista_insumo_escaso),0)

    def test_verificar_inventario_final_escaso(self):
        estado, lista_insumo_escaso = verificar_inventario_final(self.lista_inventario_escaso, self.lista_inventario_requerido)
        self.assertEqual(estado,0)
        self.assertNotEqual(len(lista_insumo_escaso),0)

    def test_disminuir_inventario(self):
        lista_inventario = disminuir_inventario(self.lista_inventario_inicial, self.lista_inventario_requerido)
        self.assertEqual(len(lista_inventario), len(self.lista_inventario_requerido))

#if __name__ == '__main__':
    # begin the unittest.main()
    #unittest.main()

def main(out = sys.stderr, verbosity = 2):
    loader = unittest.TestLoader()
  
    suite = loader.loadTestsFromModule(sys.modules[__name__])
    unittest.TextTestRunner(out, verbosity = verbosity).run(suite)
      
if __name__ == '__main__':
    with open('testing.out', 'w') as f:
        main(f)