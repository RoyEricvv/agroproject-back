from datetime import datetime
from aplicacion import db, ma, fields
#from aplicacion.modelo import Animal

class HistorialCrecimiento(db.Model):
    """Modelo de Dato para HistorialCrecimiento"""

    __tablename__ = 'HistorialCrecimiento'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    altura_promedio = db.Column(
        db.Float
    )
    peso_total = db.Column(
        db.Float
    )
    cantidad = db.Column(
        db.Integer
    )
    semana_crecimiento = db.Column(
        db.Integer
    )
    comentario = db.Column(
        db.String(250)
    )
    animal_id = db.Column(
        db.Integer, 
        db.ForeignKey('Animal.id')
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

    __table_args__ = (
        db.Index('animal_id_semana_crecimiento', 'animal_id', 'semana_crecimiento'),
    )

    #animal = db.relationship('Animal', backref="HistorialCrecimiento")

    def __repr__(self):
        return '<HistorialCrecimiento {}>'.format(self.cantidad)

class HistorialCrecimientoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = HistorialCrecimiento
        sqla_session = db.session
        include_fk = True
    #animal = fields.Nested('AnimalSchema')