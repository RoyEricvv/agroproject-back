from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo.Usuario import UsuarioSchema
from aplicacion.modelo.Departamento import Departamento

class Granja(db.Model):
    """Modelo de Data para Granja"""

    __tablename__ = 'Granja'
    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    usuario_id = db.Column(
        db.Integer, 
        db.ForeignKey('Usuario.id'),
        primary_key=True
    )
    departamento_id = db.Column(
        db.Integer, 
        db.ForeignKey('Departamento.id'),
        primary_key=True
    )
    nombre = db.Column(
        db.String(45)
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


    usuario = db.relationship("Usuario", backref="Granja")
    departamento = db.relationship("Departamento", backref="Granja")

    def __repr__(self):
        return '<Granja {}>'.format(self.nombre)

class GranjaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Granja
        include_fk = True
        sqla_session = db.session
    usuario = fields.Nested('UsuarioSchema')
    departamento = fields.Nested('DepartamentoSchema')