from datetime import datetime
from aplicacion import db, ma, fields
from sqlalchemy import Column
from aplicacion.modelo import Insumo

class Aditivo(db.Model):
    """Modelo de Data para Aditivo"""

    __tablename__ = 'Aditivo'
    aditivo_id = Column(
        db.Integer, 
        db.ForeignKey('Insumo.id'),
        primary_key=True
    )
    insumo_id = Column(
        db.Integer, 
        db.ForeignKey('Insumo.id'),
        primary_key=True
    )
    relacion = db.Column(
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


    aditivo = db.relationship("Insumo", backref="aditivo", uselist=False, foreign_keys=[aditivo_id])
    insumo = db.relationship("Insumo", backref="insumo", uselist=False, foreign_keys=[insumo_id])



    def __repr__(self):
        return '<Aditivo {}>'.format(self.relacion)

class AditivoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Aditivo
        include_fk = True
        sqla_session = db.session
    aditivo = fields.Nested('InsumoSchema')
    insumo = fields.Nested('InsumoSchema')