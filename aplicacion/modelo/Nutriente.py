from datetime import datetime
from aplicacion import db, ma

class Nutriente(db.Model):
    """Modelo de Data para Nutriente"""

    __tablename__ = 'Nutriente'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    nombre = db.Column(
        db.String(100)
    )
    abreviatura = db.Column(
        db.String(45)
    )
    unidad = db.Column(
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

    def __repr__(self):
        return '<Nutriente {}>'.format(self.nombre)

class NutrienteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Nutriente
        sqla_session = db.session 