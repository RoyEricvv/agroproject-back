from datetime import datetime
from aplicacion import db, ma, fields


class Fuente(db.Model):
    """Modelo de Dato para Fuente"""

    __tablename__ = 'Fuente'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    nombre = db.Column(
        db.String(45)
    )
    activo = db.Column(
        db.Boolean
    )

    def __repr__(self):
        return '<Fuente {}>'.format(self.nombre)

class FuenteSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Fuente
        sqla_session = db.session
