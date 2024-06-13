from datetime import datetime
from aplicacion import db, ma, fields
from sqlalchemy import Column
from aplicacion.modelo import Nutriente, Insumo

class ContenidoNutricional(db.Model):
    """Modelo de Data para Contenido Nutricional"""

    __tablename__ = 'ContenidoNutricional'
    nutriente_id = Column(
        db.Integer, 
        db.ForeignKey('Nutriente.id'),
        primary_key=True
    )
    insumo_id = Column(
        db.Integer, 
        db.ForeignKey('Insumo.id'),
        primary_key=True
    )
    cantidad = Column(
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


    nutriente = db.relationship('Nutriente', backref="ContenidoNutricional")
    insumo = db.relationship('Insumo', backref="ContenidoNutricional")



    def __repr__(self):
        return '<ContenidoNutricional {}>'.format(self.cantidad)

class ContenidoNutricionalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ContenidoNutricional
        include_fk = True
        sqla_session = db.session 
    nutriente = fields.Nested('NutrienteSchema')
    insumo = fields.Nested('InsumoSchema')