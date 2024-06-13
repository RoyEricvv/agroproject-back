from datetime import datetime
from aplicacion import db, ma, fields


class Insumo(db.Model):
    """Modelo de Data para Insumo"""

    __tablename__ = 'Insumo'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    nombre = db.Column(
        db.String(45)
    )
    es_aditivo = db.Column(
        db.Boolean
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

    def __repr__(self):
        return '<Insumo {}>'.format(self.nombre)

class InsumoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Insumo
        sqla_session = db.session 