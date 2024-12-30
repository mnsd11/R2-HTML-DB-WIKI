from flask import Flask, render_template, request
from routes import register_routes
from config.settings import load_config
from os.path import splitext, exists
from os import makedirs
from flask_talisman import Talisman
import logging
from logging.handlers import RotatingFileHandler
import traceback
from datetime import datetime

# Setup logging configuration
def setup_logging(app):
    # Create logs directory if it doesn't exist
    log_dir = 'logs'
    if not exists(log_dir):
        makedirs(log_dir)

    # File handler for all logs
    file_handler = RotatingFileHandler(
        f'{log_dir}/app.log',
        maxBytes=10485760,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n%(message)s'
    ))
    file_handler.setLevel(logging.INFO)

    # Error file handler for errors only
    error_file_handler = RotatingFileHandler(
        f'{log_dir}/error.log',
        maxBytes=10485760,
        backupCount=10,
        encoding='utf-8'
    )
    error_file_handler.setFormatter(logging.Formatter(
        '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]:\n%(message)s\nTraceback:\n%(exc_info)s'
    ))
    error_file_handler.setLevel(logging.ERROR)

    # Remove default handlers
    app.logger.handlers.clear()

    # Add handlers to app logger
    app.logger.addHandler(file_handler)
    app.logger.addHandler(error_file_handler)
    app.logger.setLevel(logging.INFO)

    # Log when the application starts
    app.logger.info(f"Application startup at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

app = Flask(__name__)

# Configure Talisman security headers
# Talisman(app, force_https=False, content_security_policy={
#     'style-src': "'self' 'unsafe-inline' https://fonts.googleapis.com https://maxcdn.bootstrapcdn.com https://cdnjs.cloudflare.com https://cdn.datatables.net https://use.fontawesome.com https://ka-f.fontawesome.com",
#     'script-src': "'self' 'unsafe-inline' https://code.jquery.com https://cdnjs.cloudflare.com https://cdn.datatables.net https://maxcdn.bootstrapcdn.com",
#     'img-src': "'self' data: https://raw.githubusercontent.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://use.fontawesome.com https://ka-f.fontawesome.com"
# })

# Load configuration and setup logging
load_config(app)
setup_logging(app)

# Request logging middleware
@app.before_request
def log_request_info():
    app.logger.info(f'Request: {request.method} {request.url}\nHeaders: {dict(request.headers)}\nBody: {request.get_data()}')

@app.after_request
def log_response_info(response):
    app.logger.info(f'Response: {response.status}\nHeaders: {dict(response.headers)}')
    return response

# Register routes
register_routes(app)

@app.template_filter('remove_extension')
def remove_extension(value):
    return splitext(value)[0]

@app.route('/favicon.ico')
def favicon():
    return '<link rel="shortcut icon" href="https://raw.githubusercontent.com/Aksel911/R2-HTML-DB/refs/heads/main/static/favicon/favicon.ico" />'

# Enhanced error handlers with detailed logging
@app.errorhandler(404)
def not_found_error(error):
    app.logger.error(f"404 Error: {error}\nPath: {request.path}\nIP: {request.remote_addr}\n{traceback.format_exc()}")
    return render_template('errors/404.html', error=error), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"500 Error: {error}\nPath: {request.path}\nIP: {request.remote_addr}\n{traceback.format_exc()}")
    return render_template('errors/500.html', error=error), 500

@app.errorhandler(400)
def bad_request_error(error):
    app.logger.error(f"400 Error: {error}\nPath: {request.path}\nIP: {request.remote_addr}\n{traceback.format_exc()}")
    return render_template('errors/400.html', error=error), 400

@app.errorhandler(403)
def forbidden_error(error):
    app.logger.error(f"403 Error: {error}\nPath: {request.path}\nIP: {request.remote_addr}\n{traceback.format_exc()}")
    return render_template('errors/403.html', error=error), 403

@app.errorhandler(405)
def method_not_allowed(error):
    app.logger.error(f"405 Error: {error}\nPath: {request.path}\nIP: {request.remote_addr}\n{traceback.format_exc()}")
    return render_template('errors/405.html', error=error), 405


@app.route('/')
def home():
    return render_template('main_page.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=app.config['PORT'], debug=True)