from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Granja, Animal, Sanitario

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
        primary_key=True
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
    # Relación con la tabla Granja
    granja = db.relationship('Granja', backref=db.backref('consumos_sanitarios', lazy=True))
     # Relación con la tabla Sanitario (vacuna) y número de dosis
    vacunas = db.relationship('Sanitario', secondary=consumo_vacuna, backref=db.backref('consumos_sanitarios', lazy='dynamic'))

    # Relación con la tabla Animal (muchos a muchos)
    animales = db.relationship('Animal', secondary=consumo_animal, backref=db.backref('consumos_sanitarios', lazy='dynamic'))

    def __repr__(self):
        return '<ConsumoSanitario {}>'.format(self.nombre)



# consumo_vacuna = db.Table('consumo_vacuna',
#     db.Column('consumo_id', db.Integer, db.ForeignKey('consumo.id'), primary_key=True),
#     db.Column('vacuna_id', db.Integer, db.ForeignKey('vacuna.id'), primary_key=True),
#     db.Column('numero_dosis', db.Integer, nullable=False)
# )

    

