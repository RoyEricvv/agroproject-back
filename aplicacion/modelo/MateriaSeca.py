from datetime import datetime
from aplicacion import db, ma, fields
from aplicacion.modelo import Insumo, Departamento

#MateriaSeca

class MateriaSeca(db.Model):
    """Modelo de Data para Animal"""

    __tablename__ = 'Materia_Seca'
    insumo_id = db.Column(
        db.Integer, 
        db.ForeignKey('Insumo.id'),
        primary_key=True
    )
    departamento_id = db.Column(
        db.Integer, 
        db.ForeignKey('Departamento.id'),
        primary_key=True
    )
    porcentaje = db.Column(
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



    insumo = db.relationship('Insumo', backref="Materia_Seca")
    departamento = db.relationship('Departamento', backref="Materia_Seca")



    def __repr__(self):
        return '<Materia_Seca {}>'.format(self.porcentaje)

class MateriaSecaSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = MateriaSeca
        include_fk = True
        sqla_session = db.session 
    insumo = fields.Nested('InventarioSchema')
    departamento = fields.Nested('DepartamentoSchema')