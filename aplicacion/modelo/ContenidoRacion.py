from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import RacionFormulada, Insumo

#RacionxInsumo

class ContenidoRacion(db.Model):
    """Modelo de Data para ContenidoRacion"""

    __tablename__ = 'ContenidoRacion'
    racion_formulada_id = db.Column(
        db.Integer, 
        db.ForeignKey('RacionFormulada.id'),
        primary_key=True
    )
    insumo_id = db.Column(
        db.Integer, 
        db.ForeignKey('Insumo.id'),
        primary_key=True
    )
    cantidad_total = db.Column(
        db.Float
    )
    cantidad_porcentual = db.Column(
        db.Float
    )
    costo_total = db.Column(
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



    racionFormulada = db.relationship('RacionFormulada', backref="ContenidoRacion")
    insumo = db.relationship('Insumo', backref="ContenidoRacion")



    def __repr__(self):
        return '<ContenidoRacion {}>'.format(self.cantidad)

class ContenidoRacionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ContenidoRacion
        include_fk = True
        sqla_session = db.session
    racionFormulada = fields.Nested('RacionFormuladaSchema')
    insumo = fields.Nested('InsumoSchema')