from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo.Insumo import Insumo
from aplicacion.modelo.Especie import Especie
from aplicacion.modelo.EtapaVida import EtapaVida


#Restriccion

class Restriccion(db.Model):
    """Modelo de Data para Animal"""

    __tablename__ = 'Restriccion'
    insumo_id = db.Column(
        db.Integer, 
        db.ForeignKey('Insumo.id'),
        primary_key=True
    )
    especie_id = db.Column(
        db.Integer, 
        db.ForeignKey('Especie.id'),
        primary_key=True
    )
    etapa_vida_id =db.Column(
        db.Integer, 
        db.ForeignKey('EtapaVida.id'),
        primary_key=True
    )
    porcentaje_permitido = db.Column(
        db.Integer
    )
    fecha_creacion = db.Column(
        db.DateTime
    )  
    fecha_modificacion = db.Column(
        db.DateTime
    ) 
    activo = db.Column(
        db.Boolean
    )

    etapa_vida = db.relationship('EtapaVida', backref="Restriccion")
    insumo = db.relationship('Insumo', backref="Restriccion")
    especie = db.relationship('Especie', backref="Restriccion")


    def __repr__(self):
        return '<Restriccion {}>'.format(self.porcentaje)

class RestriccionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Restriccion
        include_fk = True
        sqla_session = db.session 
    etapa_vida = fields.Nested('EtapaVidaSchema')
    insumo = fields.Nested('InventarioSchema')
    especie = fields.Nested('EspecieSchema')