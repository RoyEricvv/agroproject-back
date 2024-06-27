from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Animal, Equipo, Sanitario, Granja, Insumo


# Tabla intermedia para la relación muchos a muchos entre IngresoxEgreso y Animal
ingreso_animal = db.Table('ingreso_animal',
    db.Column('ingreso_id', db.Integer, db.ForeignKey('IngresoxEgreso.id', name='fk_ingreso_animal_ingreso_id'), primary_key=True),
    db.Column('animal_id', db.Integer, db.ForeignKey('Animal.id', name='fk_ingreso_animal_animal_id'), primary_key=True),
    db.Column('precio_unitario', db.Float),
    db.Column('cantidad', db.Integer)
)


# Tabla intermedia para la relación muchos a muchos entre IngresoxEgreso y Equipo
ingreso_equipo = db.Table('ingreso_equipo',
    db.Column('ingreso_id', db.Integer, db.ForeignKey('IngresoxEgreso.id', name='fk_ingreso_equipo_ingreso_id'), primary_key=True),
    db.Column('equipo_id', db.Integer, db.ForeignKey('Equipo.id', name='fk_ingreso_equipo_equipo_id'), primary_key=True),
    db.Column('precio_unitario', db.Float),
    db.Column('cantidad', db.Integer)
)

# Tabla intermedia para la relación muchos a muchos entre IngresoxEgreso y Vacuna
ingreso_vacuna = db.Table('ingreso_vacuna',
    db.Column('ingreso_id', db.Integer, db.ForeignKey('IngresoxEgreso.id', name='fk_ingreso_vacuna_ingreso_id'), primary_key=True),
    db.Column('vacuna_id', db.Integer, db.ForeignKey('Sanitario.id', name='fk_ingreso_vacuna_vacuna_id'), primary_key=True),
    db.Column('precio_unitario', db.Float),
    db.Column('cantidad', db.Integer)
)

# Tabla intermedia para la relación muchos a muchos entre IngresoxEgreso y Inventario
ingreso_insumo = db.Table('ingreso_insumo',
    db.Column('ingreso_id', db.Integer, db.ForeignKey('IngresoxEgreso.id', name='fk_ingreso_insumo_ingreso_id'), primary_key=True),
    db.Column('insumo_id', db.Integer, db.ForeignKey('Insumo.id', name='fk_ingreso_insumo_insumo_id'), primary_key=True),
    db.Column('precio_unitario', db.Float),
    db.Column('cantidad', db.Integer)
)
    
class IngresoxEgreso(db.Model):
    __tablename__ = 'IngresoxEgreso'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    granja_id = db.Column(
        db.Integer,
        db.ForeignKey('Granja.id'),
        primary_key=True
    )
    tipo = db.Column(db.String(255), nullable=False)
    cliente = db.Column(db.String(255), nullable=False)
    categoria = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    telefono = db.Column(db.String(9), nullable=False)
    fecha_emision = db.Column(db.Date, nullable=False)
    comentario = db.Column(db.Text, nullable=True)
    total = db.Column(db.Float, nullable=False)
    url_boleta = db.Column(db.String(255), nullable=True)
    total = db.Column(db.Double)
    activo = db.Column(db.Boolean, default=True)


    # Relaciones muchos a muchos con tablas intermedias
    animales = db.relationship('Animal', secondary=ingreso_animal, backref=db.backref('ingresos', lazy='dynamic'))
    equipos = db.relationship('Equipo', secondary=ingreso_equipo, backref=db.backref('ingresos', lazy='dynamic'))
    vacunas = db.relationship('Sanitario', secondary=ingreso_vacuna, backref=db.backref('ingresos', lazy='dynamic'))
    granja = db.relationship('Granja', backref=db.backref('ingresosxegreso', lazy=True))
    insumos = db.relationship('Insumo', secondary=ingreso_insumo, backref=db.backref('ingresos', lazy='dynamic'))


    def __repr__(self):
        return f'<IngresoxEgreso {self.id}>'
    


# class IngresoxEgreso(db.Model):
#     __tablename__ = 'ingresoxegreso'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     tipo = db.Column(db.String(255), nullable=False)
#     cliente = db.Column(db.String(255), nullable=False)
#     categoria = db.Column(db.String(255), nullable=False)
#     direccion = db.Column(db.String(255), nullable=False)
#     telefono = db.Column(db.String(9), nullable=False)
#     fecha_emision = db.Column(db.Date, nullable=False)
#     comentario = db.Column(db.Text, nullable=True)
#     total = db.Column(db.Float, nullable=False)
#     url_boleta = db.Column(db.String(255), nullable=True)

#     # Relaciones muchos a muchos con tablas intermedias
#     animales = db.relationship('Animal', secondary=ingreso_animal, backref=db.backref('ingresos', lazy='dynamic'))
#     equipos = db.relationship('Equipo', secondary=ingreso_equipo, backref=db.backref('ingresos', lazy='dynamic'))
#     vacunas = db.relationship('Vacuna', secondary=ingreso_vacuna, backref=db.backref('ingresos', lazy='dynamic'))

#     # Relación uno a muchos con Granja
#     granja_id = db.Column(db.Integer, db.ForeignKey('granja.id', name='fk_ingresoxegreso_granja_id'))
#     granja = db.relationship('Granja', backref=db.backref('ingresosxegreso', lazy=True))

#     def __repr__(self):
#         return f'<IngresoxEgreso {self.id}>'