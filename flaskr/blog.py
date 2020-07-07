from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('blog', __name__)

def get_post(id, check_author=True):
    post = get_db().execute(
        'SELECT p.id, title, body, created, date_posted, author_id, username, name'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' WHERE p.id = ?',
        (id,)
    ).fetchone()

    if post is None:
        abort(404, "Post id {0} doesn't exist.".format(id))

    if check_author and post['author_id'] != g.user['id']:
        abort(403)

    return post

@bp.route('/')
def index():
    db = get_db()
    posts = db.execute(
        'SELECT p.id, title, body, created, date_posted, author_id, username, name'
        ' FROM post p JOIN user u ON p.author_id = u.id'
        ' ORDER BY date_posted DESC'
    ).fetchall()
    return render_template('blog/index.html', posts=posts)

@bp.route('/<int:id>/display', methods=('GET', 'POST'))
def display(id):
    post = get_post(id,False)
    return render_template('blog/display.html',post=post)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        date_posted = request.form['date_posted']

        error = None
        if not title or not date_posted:
            error = 'Title/Date is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO post (title, body, date_posted, author_id)'
                ' VALUES (?, ?, ?, ?)',
                (title, body, date_posted, g.user['id'])
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/create.html')

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        date_posted = request.form['date_posted']
        title = request.form['title']
        body = request.form['body']

        error = None
        if not title:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE post SET date_posted=?, title = ?, body = ?'
                ' WHERE id = ?',
                (date_posted, title, body, id)
            )
            db.commit()
            return redirect(url_for('blog.index'))

    return render_template('blog/update.html', post=post)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM post WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('blog.index'))
