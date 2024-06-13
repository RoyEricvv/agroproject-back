from datetime import datetime
from aplicacion import db, ma, fields


class Perfil(db.Model):
    """Modelo de Dato para Perfil"""

    __tablename__ = 'Perfil'
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
        return '<Perfil {}>'.format(self.nombre)

class PerfilSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Perfil
        sqla_session = db.session
