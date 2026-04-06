from flask import Flask
from .config import Config
from .extensions import db, migrate, jwt, cors

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(app, resources={r"/*":{"origins": "*"}})

    from .models import User, Vehicle, VehicleLog
    from .routes.auth import auth_bp
    from .routes.health import health_bp
    from .routes.vehicles import vehicles_bp
    from .routes.vehicle_logs import vehicle_logs_bp
    from .routes.ai import ai_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(health_bp, url_prefix="/health")
    app.register_blueprint(vehicles_bp, url_prefix="/vehicle")
    app.register_blueprint(vehicle_logs_bp, url_prefix="/vehicle")
    app.register_blueprint(ai_bp)

    return app
