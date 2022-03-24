import requests
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.db import get_db

bp = Blueprint('poke', __name__)


@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT id, name, quote, created, image'
        ' FROM person'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('poke/index.html', posts=posts)
