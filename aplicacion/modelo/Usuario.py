from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo.Perfil import Perfil

class Usuario(db.Model):
    """Modelo de Dato para Usuario"""

    __tablename__ = 'Usuario'
    id = db.Column(
        db.Integer,
        primary_key=True
    )
    username = db.Column(
        db.String(45),
        unique=True
    )
    nombres = db.Column(
        db.String(45)
    )
    apellidos = db.Column(
        db.String(45)
    )
    password = db.Column(
        db.String(45)
    )
    correo = db.Column(
        db.String(80)
    )
    perfil_id = db.Column(
        db.Integer, 
        db.ForeignKey('Perfil.id')
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
    
    perfil = db.relationship("Perfil", backref="Usuario")

    def __repr__(self):
        return '<Usuario {}>'.format(self.username)

class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        sqla_session = db.session
        include_fk = True
    perfil = fields.Nested('PerfilSchema')