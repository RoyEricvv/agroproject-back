from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Granja, Animal, Sanitario
from aplicacion.modelo.Sanitario import SimpleSanitarioSchema
from marshmallow import fields, Schema, validates, ValidationError

# Tabla intermedia para la relación muchos a muchos entre ConsumoSanitario y Sanitario (vacuna)
consumo_vacuna = db.Table('consumo_vacuna',
    db.Column('consumo_id', db.Integer, db.ForeignKey('ConsumoSanitario.id'), primary_key=True),
    db.Column('vacuna_id', db.Integer, db.ForeignKey('Sanitario.id'), primary_key=True),
    db.Column('numero_dosis', db.Integer)
)
consumo_animal = db.Table('consumo_animal',
    db.Column('consumo_id', db.Integer, db.ForeignKey('ConsumoSanitario.id'), primary_key=True),
    db.Column('animal_id', db.Integer, db.ForeignKey('Animal.id'), primary_key=True)
)


class ConsumoSanitario(db.Model):
    """Modelo de Data para Animal"""

    __tablename__ = 'ConsumoSanitario'
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
    #1:
    personal_solicitante = db.Column(
        db.String(255), nullable=False
    )
    fecha_salida = db.Column(
        db.Date, nullable=False
    )
    lote = db.Column(
        db.String(50)
    )  # Representa a qué animal hace referencia
    observaciones = db.Column(
        db.String(255)
    )
    activo = db.Column(db.Boolean, default=True)

    # Relación con la tabla Granja
    granja = db.relationship('Granja', backref=db.backref('consumos_sanitarios', lazy=True))
     # Relación con la tabla Sanitario (vacuna) y número de dosis
    vacunas = db.relationship('Sanitario', secondary=consumo_vacuna, backref=db.backref('consumos_sanitarios', lazy='dynamic'))

    # Relación con la tabla Animal (muchos a muchos)
    animales = db.relationship('Animal', secondary=consumo_animal, backref=db.backref('consumos_sanitarios', lazy='dynamic'))


    def __repr__(self):
        return '<ConsumoSanitario {}>'.format(self.nombre)


class ConsumoVacunaSchema(ma.Schema):
    vacuna_id = fields.Int()
    numero_dosis = fields.Int()
    # vacunas = fields.Nested('SimpleSanitarioSchema', many=True)


class IntermediateConsumoSanitarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsumoSanitario
        include_fk = True

    consumo_vacunas = fields.Method("get_vacunas")
    animales = fields.List(fields.Nested('SimpleAnimalSchema'))
    granja = fields.Nested('GranjaSchema')
    vacunas = fields.List(fields.Nested(SimpleSanitarioSchema))
    def get_vacunas(self, obj):
        results = db.session.query(consumo_vacuna) \
                    .filter(consumo_vacuna.c.consumo_id == obj.id) \
                    .all()

        return [ConsumoVacunaSchema().dump({
            'vacuna_id': r.vacuna_id,
            'numero_dosis': r.numero_dosis,
        }) for r in results]
    
    # class Meta:
    #     model = ConsumoSanitario
    #     include_fk = True
    #     include_relationships = True
    #     load_instance = True
    #     sqla_session = db.session

    # # Incluir las relaciones con vacunas y animales usando los esquemas de las tablas intermedias
    # # vacunas = fields.Nested(ConsumoVacunaSchema, many=True)
    # # vacunas = fields.List(fields.Nested('ConsumoVacunaSchema'))
    # consumo_vacuna = fields.List(fields.Nested(ConsumoVacunaSchema))
    # # animales = fields.List(fields.Nested('SimpleAnimalSchema'))


class SimpleConsumoSanitarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsumoSanitario
        include_fk = True
        sqla_session = db.session
    granja = fields.Nested('GranjaSchema')
    vacunas = fields.List(fields.Nested(SimpleSanitarioSchema))
    animales = fields.List(fields.Nested('SimpleAnimalSchema'))
    # vacunas = fields.Nested('SimpleSanitarioSchema')

class ConsumoSanitarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConsumoSanitario
        include_fk = True
        sqla_session = db.session

    granja_id = fields.Integer(required=True)
    personal_solicitante = fields.String(required=True)
    fecha_salida = fields.Date(format='%Y-%m-%d', required=True)
    lote = fields.String()
    observaciones = fields.String()

    # Relación con vacunas (Sanitario)
    vacunas = fields.List(fields.Dict(), required=True)
    animales = fields.List(fields.Dict(), required=True)
    @staticmethod
    def validate_vacuna_id(value):
        if not isinstance(value, int):
            raise ValidationError('Field "vacuna_id" must be an integer.')

    @staticmethod
    def validate_numero_dosis(value):
        if not isinstance(value, int) or value <= 0:
            raise ValidationError('Field "numero_dosis" must be a positive integer.')

    @validates('vacunas')
    def validate_vacunas(self, value):
        for vacuna in value:
            self.validate_vacuna_id(vacuna.get('vacuna_id'))
            self.validate_numero_dosis(vacuna.get('numero_dosis'))
    

    @validates('animales')
    def validate_vacunas(self, value):
        for animal in value:
            self.validate_vacuna_id(animal.get('animal_id'))
    

# class SimpleConsumoSanitarioSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = ConsumoSanitario
#         include_fk = True
#         sqla_session = db.session

#     granja_id = fields.Integer(required=True)
#     personal_solicitante = fields.String(required=True)
#     fecha_salida = fields.Date(format='%Y-%m-%d', required=True)
#     lote = fields.String()
#     observaciones = fields.String()

#     vacuna = fields.Nested('SimpleSanitarioSchema')
#     animal = fields.Nested('AnimalSchema')


# class ConsumoSanitarioSchema(ma.SQLAlchemyAutoSchema):
#     class Meta:
#         model = ConsumoSanitario
#         include_fk = True
#         load_instance = True
#         sqla_session = db.session

#     granja_id = fields.Integer(required=True)
#     personal_solicitante = fields.String(required=True)
#     fecha_salida = fields.Date(format='%Y-%m-%d', required=True)
#     lote = fields.String()
#     observaciones = fields.String()

#     # Relación many-to-many con Sanitario (vacunas) a través de ConsumoVacuna
#     vacunas = fields.Nested('SimpleSanitarioSchema', many=True, exclude=('consumo',))

#     # Relación many-to-many con Animal a través de ConsumoAnimal
#     animales = fields.Nested('AnimalSchema', many=True, exclude=('consumo',))

#     @validates('vacunas')
#     def validate_vacunas(self, value):
#         for data in value:
#             if 'vacuna_id' not in data:
#                 raise ValidationError('Field "vacuna_id" is required.')
#             if 'numero_dosis' not in data or not isinstance(data['numero_dosis'], int) or data['numero_dosis'] <= 0:
#                 raise ValidationError('Field "numero_dosis" must be a positive integer.')

#     @validates('animales')
#     def validate_animales(self, value):
#         for data in value:
#             if 'animal_id' not in data:
#                 raise ValidationError('Field "animal_id" is required.')