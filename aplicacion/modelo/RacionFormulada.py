from datetime import datetime
from aplicacion import db, ma, fields
from sqlalchemy import Column
from aplicacion.modelo.Usuario import Usuario,UsuarioSchema
from aplicacion.modelo.Animal import Animal,AnimalSchema
from aplicacion.modelo.Fuente import Fuente,FuenteSchema


class RacionFormulada(db.Model):
    """Modelo de Data para RacionFormulada"""

    __tablename__ = 'RacionFormulada'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    costo_aditivo = db.Column(
        db.Float
    )
    costo_aditivo_kg = db.Column(
        db.Float
    )
    costo_total = db.Column(
        db.Float
    )
    costo_total_Kg = db.Column(
        db.Float
    )
    cantidad_total = db.Column(
        db.Float
    )
    estado_racion = db.Column(
        db.Integer
    )
    tipo = db.Column(
        db.Integer
    )
    etapa_semana = db.Column(
        db.Integer
    )
    cantidad_animales = db.Column(
        db.Integer
    )
    numero_de_aplicaciones = db.Column(
        db.Integer
    )
    fuente_id = db.Column(
        db.Integer,
        db.ForeignKey('Fuente.id')
    )
    aplicar = db.Column(
        db.Boolean
    )
    favorito = db.Column(
        db.Boolean
    )
    usuario_id = db.Column(
        db.Integer, 
        db.ForeignKey('Usuario.id')
    )
    animal_id = Column(
        db.Integer, 
        db.ForeignKey('Animal.id')
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
    fuente= db.relationship("Fuente", backref="RacionFormulada")
    animal= db.relationship("Animal", backref="RacionFormulada")
    usuario= db.relationship("Usuario", backref="RacionFormulada")

    def __repr__(self):
        return '<RacionFormulada {}>'.format(self.aplicar)

class RacionFormuladaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RacionFormulada
        include_fk = True
        sqla_session = db.session
    usuario = fields.Nested('UsuarioSchema') 
    animal = fields.Nested('AnimalSchema') 
    fuente = fields.Nested('FuenteSchema') 