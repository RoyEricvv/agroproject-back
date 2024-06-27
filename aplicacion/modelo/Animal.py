from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Granja, Especie, HistorialCrecimiento

#GranjaXEspecie

class Animal(db.Model):
    """Modelo de Data para Animal"""

    __tablename__ = 'Animal'
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
    estado_animal = db.Column(
        db.Integer
    )
    cantidad_actual = db.Column(
        db.Integer
    )
    peso_animal_actual = db.Column(
        db.Float
    )
    costo_racion = db.Column(
        db.Float
    )
    costo_kg_animal = db.Column(
        db.Float
    )
    precio_animal = db.Column(
        db.Float
    )
    precio_kg_animal = db.Column(
        db.Float
    )
    nombre = db.Column(
        db.String(45)
    )
    comentario = db.Column(
        db.String(250)
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

    granja = db.relationship('Granja', backref="Animal")
    especie = db.relationship('Especie', backref="Animal")


    def __repr__(self):
        return '<Animal {}>'.format(self.nombre)

class AnimalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Animal
        include_fk = True
        sqla_session = db.session 
    granja = fields.Nested('GranjaSchema')
    especie = fields.Nested('EspecieSchema')


class SimpleAnimalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Animal
        include_fk = True
        sqla_session = db.session
