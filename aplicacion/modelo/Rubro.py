from datetime import datetime
from aplicacion import db, ma, fields
from marshmallow import fields, Schema, validates, ValidationError


class Rubro(db.Model):
    """Modelo de Data para Rubro"""

    __tablename__ = 'Rubro'
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    #1:
    nombre = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)
    tipo = db.Column(db.String(50), nullable=False)
    

    def __repr__(self):
        return '<Rubro {}>'.format(self.nombre)


class RubroSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rubro
        include_fk = True
        sqla_session = db.session
        load_instance = True  # Cargar instancias de modelo al deserializar
