import os
from flask import Blueprint, render_template, send_file
from flask_login import current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    return render_template('index.html')


@main_bp.route('/page143896526.html')
def tilda_page():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'page143896526.html')
    return send_file(path)
