from datetime import datetime
from aplicacion import db, ma, fields


class Especie(db.Model):
    """Modelo de Data para Especie"""

    __tablename__ = 'Especie'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    nombre = db.Column(
        db.String(45)
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
        return '<Granja {}>'.format(self.nombre)

class EspecieSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Especie
        sqla_session = db.session 