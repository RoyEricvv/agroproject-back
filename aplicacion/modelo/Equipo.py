from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Granja

#Equipos
class Equipo(db.Model):
    __tablename__ = 'Equipo'

    id = db.Column(
        db.Integer, 
        primary_key=True,
        autoincrement=True
    )
    
    granja_id = db.Column(
        db.Integer,
        db.ForeignKey('Granja.id', name='fk_equipo_granja_id'),
        primary_key=True
    )
    estado_equipo = db.Column(
        db.Integer
    )
    nombre = db.Column(db.String(100), nullable=False)
    numero_serie = db.Column(db.String(50), unique=True, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)  # Se asume que el precio es un valor numérico
    moneda = db.Column(db.String(10), nullable=False)  # Se puede usar una enumeración para manejar las monedas
    comentario = db.Column(db.Text)
    documento = db.Column(db.String(255))  # Ruta al archivo adjunto del documento

    fecha_compra = db.Column(db.Date)  # Fecha en que se compró el equipo
    estado = db.Column(db.String(50))  # Estado actual del equipo (activo, inactivo, mantenimiento, etc.)
    proveedor = db.Column(db.String(100))  # Proveedor o empresa de la cual se adquirió el equipo
    vida_estimada = db.Column(db.Integer)  # Vida útil estimada del equipo en años
    tipo_depreciacion = db.Column(db.String(50))  # Tipo de depreciación (lineal, acelerada, etc.)
    fecha_limite_garantia = db.Column(db.Date)  # Fecha límite de garantía del equipo

    granja = db.relationship('Granja', backref=db.backref('Equipo', lazy=True))
    
    def __repr__(self):
        return f'<Equipo {self.nombre} - Número de Serie: {self.numero_serie}>'
    

class EquipoSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Equipo
        include_fk = True
        sqla_session = db.session 
    granja = fields.Nested('GranjaSchema')