# fastique/app/__init__.py
# Flask application factory

from flask import Flask
from app.config import Config

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Register blueprints
    from app.routes.main_routes import main_bp
    from app.routes.search_routes import search_bp
    from app.routes.file_operation_routes import file_op_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(file_op_bp)
    
    # Initialize logging
    if not app.debug:
        import logging
        from logging.handlers import RotatingFileHandler
        import os
        
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/fastique.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Fastique startup')
    
    return app