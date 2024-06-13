from flask import current_app as app
from aplicacion.modelo.Perfil import Perfil, PerfilSchema
# Servicios de Usuario


#Servicio para listar todos los perfiles
@app.route('/perfiles', methods=['GET'])
def perfil_listar_todos():
    #Se crea la lista de perfiles.
    perfiles = Perfil.query.filter(Perfil.activo==True).order_by(Perfil.id).all()

    #Se serializa la información a retornar
    perfiles_schema = PerfilSchema(many=True)
    data = perfiles_schema.dump(perfiles)
 
    return {"Mensaje": "Lista de perfiles", "perfiles": data}