from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Nutriente, Especie, Departamento

class EtapaVida(db.Model):
    """Modelo de Data para Etapa de vida de especie"""

    __tablename__ = 'EtapaVida'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    peso_vivo_referencial = db.Column(
        db.Float
    )
    talla_referencial = db.Column(
        db.Float
    )
    cantidad_MS_referencial = db.Column(
        db.Float
    )
    semana_vida_referencial_inicial= db.Column(
        db.Integer
    )
    semana_vida_referencial_final = db.Column(
        db.Integer
    )
    especie_id = db.Column(
        db.Integer, 
        db.ForeignKey('Especie.id')
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

    especie = db.relationship('Especie', backref="EtapaVida")



    def __repr__(self):
        return '<EtapaVida {}>'.format(self.cantidad)

class EtapaVidaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EtapaVida
        include_fk = True
        sqla_session = db.session
    especie = fields.Nested('EspecieSchema')