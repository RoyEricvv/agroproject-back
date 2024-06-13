from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Granja, Especie

#GranjaXEspecie

class Sanitario(db.Model):
    """Modelo de Data para Animal"""

    __tablename__ = 'Sanitario'
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    granja_id = db.Column(
        db.Integer,
        db.ForeignKey('Granja.id'),
        primary_key=True
    )
    especie_id = db.Column(
        db.Integer,
        db.ForeignKey('Especie.id'),
        primary_key=True
    )
    #1:
    rubro = db.Column(
        db.String(255), nullable=False
    )
    fecha_ingreso = db.Column(
        db.Date, nullable=False
    )
    fecha_vencimiento = db.Column(
        db.Date, nullable=False
        )
    frascos = db.Column(
        db.Integer, nullable=False
    )
    marca = db.Column(
        db.String(255), nullable=False
    )
    dosis = db.Column(
        db.Integer, nullable=False
    )
    ml_animal = db.Column(
        db.Integer, nullable=False
    )
    estado_sanitario = db.Column(
        db.String(50), nullable=False
    )  # Campo estado
    observaciones = db.Column(
        db.String(255)
    )  # Campo observaciones

    activo = db.Column(
        db.Boolean,
        default=True
    )

    granja = db.relationship('Granja', backref="Sanitario")
    especie = db.relationship('Especie', backref="Sanitario")


    def __repr__(self):
        return '<Sanitario {}>'.format(self.nombre)

class SanitarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sanitario
        include_fk = True
        sqla_session = db.session 
    granja = fields.Nested('GranjaSchema')
    especie = fields.Nested('EspecieSchema')


