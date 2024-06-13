from datetime import datetime
from aplicacion import db, ma, fields
from sqlalchemy import Column
from aplicacion.modelo import Nutriente, RacionFormulada

class NutrienteRacion(db.Model):
    """Modelo de Data para Nutriente Ración"""

    __tablename__ = 'NutrienteRacion'
    nutriente_id = Column(
        db.Integer, 
        db.ForeignKey('Nutriente.id'),
        primary_key=True
    )
    racion_id = Column(
        db.Integer, 
        db.ForeignKey('RacionFormulada.id'),
        primary_key=True
    )
    cantidad_racion = Column(
        db.Float
    )
    cantidad_fuente = Column(
        db.Float
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


    nutriente = db.relationship('Nutriente', backref="NutrienteRacion")
    racionFormulada = db.relationship('RacionFormulada', backref="NutrienteRacion")



    def __repr__(self):
        return '<NutrienteRacion {}>'.format(self.cantidad_racion)

class NutrienteRacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = NutrienteRacion
        include_fk = True
        sqla_session = db.session 
    nutriente = fields.Nested('NutrienteSchema')
    racionFormulada = fields.Nested('RacionFormuladaSchema')