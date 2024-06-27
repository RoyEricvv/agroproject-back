from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import fields
from flask_cors import CORS
from flask_migrate import Migrate

db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
def init_app():
    """Construct the core application."""
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object('config.Config')

    CORS(app)
    
    db.init_app(app)
    migrate.init_app(app, db)


    with app.app_context():
        from aplicacion.routes import nutrienteRacionRoute, reporteRoute,profileRoute, aditivoRoute,fuenteRoute, restriccionRoute, etapaVidaRoute, departamentoRoute, historialCrecimientoRoute, animalesRoute, contenidoNutricionalRoute, contenidoRacionRouter, especieRoute, granjaRoute, insumoRoute, inventarioRoute, nutrienteRouter, racionFormuladaRoute, requerimientoNutricionalRoute, usuarioRoute, metodoFormularRacion, materiaSecaRoute, sanitarioRoute, consumoSanitarioRoute, equiposRoute, ingresoxEgresoRoute, rubroRoute, route  # Import routes      
        db.create_all()  # Create sql tables for our data models
        return app  