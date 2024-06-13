from datetime import datetime
from aplicacion import db, ma, fields


class Departamento(db.Model):
    """Modelo de Dato para Departamento"""

    __tablename__ = 'Departamento'
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
        return '<Departamento {}>'.format(self.nombre)

class DepartamentoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Departamento
        sqla_session = db.session
