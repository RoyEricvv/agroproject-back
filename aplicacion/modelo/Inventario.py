from datetime import datetime
from aplicacion import db, ma, fields
from sqlalchemy import Column
from aplicacion.modelo import Usuario, Insumo

class Inventario(db.Model):
    """Modelo de Data para Inventario"""

    __tablename__ = 'Inventario'
    usuario_id = db.Column(
        db.Integer, 
        db.ForeignKey('Usuario.id'),
        primary_key=True
    )
    insumo_id = Column(
        db.Integer, 
        db.ForeignKey('Insumo.id'),
        primary_key=True
    )
    costo_total = db.Column(
        db.Float
    )
    costo_unitario = db.Column(
        db.Float
    )
    peso_total = db.Column(
        db.Float
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


    usuario = db.relationship('Usuario', backref="Inventario")
    insumo = db.relationship('Insumo', backref="Inventario")



    def __repr__(self):
        return '<Inventario {}>'.format(self.costo_total)

class InventarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Inventario
        include_fk = True
        sqla_session = db.session
    usuario = fields.Nested('UsuarioSchema')
    insumo = fields.Nested('InsumoSchema')