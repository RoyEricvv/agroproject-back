from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Nutriente, EtapaVida, Departamento, Fuente

class RequerimientoNutricional(db.Model):
    """Modelo de Data para RequerimientoNutricional"""

    __tablename__ = 'RequerimientoNutricional'
    fuente_id = db.Column(
        db.Integer,
        db.ForeignKey('Fuente.id'),
        primary_key=True
    )
    nutriente_id = db.Column(
        db.Integer, 
        db.ForeignKey('Nutriente.id'),
        primary_key=True
    )
    etapa_vida_id = db.Column(
        db.Integer, 
        db.ForeignKey('EtapaVida.id'),
        primary_key=True
    )
    departamento_id = db.Column(
        db.Integer, 
        db.ForeignKey('Departamento.id'),
        primary_key=True
    )
    cantidad = db.Column(
        db.Float
    )
    tipo_requerimiento = db.Column(
        db.Integer
    )
    esencial = db.Column(
        db.Boolean
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

    fuente = db.relationship("Fuente", backref="RequerimientoNutricional")
    departamento = db.relationship("Departamento", backref="RequerimientoNutricional")
    nutriente = db.relationship('Nutriente', backref="RequerimientoNutricional")
    etapa_vida = db.relationship('EtapaVida', backref="RequerimientoNutricional")


    def __repr__(self):
        return '<RequerimientoNutricional {}>'.format(self.cantidad)

class RequerimientoNutricionalSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = RequerimientoNutricional
        include_fk = True
        sqla_session = db.session
    nutriente = fields.Nested('NutrienteSchema')
    etapa_vida = fields.Nested('EtapaVidaSchema')
    departamento = fields.Nested('DepartamentoSchema')
    fuente = fields.Nested('FuenteSchema')