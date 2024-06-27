from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Granja, Especie, Rubro

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
        nullable=False
    )
    especie_id = db.Column(
        db.Integer,
        db.ForeignKey('Especie.id'),
        nullable=False
    )
    rubro_id = db.Column(
        db.Integer,
        db.ForeignKey('Rubro.id'),
        nullable=False
    )
    #1:
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
    saldo = db.Column(
        db.Double
    )
    activo = db.Column(
        db.Boolean,
        default=True
    )

    granja = db.relationship('Granja', backref="Sanitario")
    especie = db.relationship('Especie', backref="Sanitario")
    rubro = db.relationship('Rubro', backref="Sanitario")


    def __repr__(self):
        return '<Sanitario {}>'.format(self.nombre)

class SanitarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sanitario
        include_fk = True
        sqla_session = db.session 
    granja = fields.Nested('GranjaSchema')
    especie = fields.Nested('EspecieSchema')
    rubro = fields.Nested('RubroSchema')
     

class SimpleSanitarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sanitario
        include_fk = True
        sqla_session = db.session

    # Relación con vacunas (Sanitario)
    # vacunas = fields.List(fields.Nested(SanitarioSchema), required=True)
    # # Relación con animales
    # animales = fields.List(fields.Integer(), required=True)

# class RubroSanitarioSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = Sanitario
#         include_fk = True
#         fields = ('rubro',)

