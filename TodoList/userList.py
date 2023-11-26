from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from TodoList.user import login_required
from TodoList.db import get_db

bp = Blueprint('userList', __name__)


@bp.route('/')
def index():
    db = get_db()
    items = db.execute(
        'SELECT i.id, listItem, created, author_id, checked, username'
        ' FROM item i JOIN user u ON i.author_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('userList/index.html', items=items)


@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        item = request.form['listItem']
        error = None

        if not item:
            error = 'List item is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO item (listItem, checked, author_id)'
                ' VALUES (?, ?, ?)',
                (item, 0, g.user['id'])
            )
            db.commit()
            return redirect(url_for('userList.index'))

    return render_template('userList/create.html')


def get_post(id, check_author=True):
    items = get_db().execute(
        'SELECT i.id, listItem, checked, created, author_id, username'
        ' FROM item i JOIN user u ON i.author_id = u.id'
        ' WHERE i.id = ?',
        (id,)
    ).fetchone()

    if items is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and items['author_id'] != g.user['id']:
        abort(403)

    return items


@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id):
    item = get_post(id)

    if request.method == 'POST':
        listitem = request.form['item']
        error = None

        if not listitem:
            error = 'Title is required.'

        if error is not None:
            flash(error)
        else:
            completed = request.form.get('checkTest')
            check = 1 if completed else 0
            print(check)
            db = get_db()
            db.execute(
                'UPDATE item SET listitem = ?, checked=?'
                ' WHERE id = ?',
                (listitem,check,id)
            )
            db.commit()
            return redirect(url_for('userList.index'))

    return render_template('userList/update.html', item=item)


@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_post(id)
    db = get_db()
    db.execute('DELETE FROM item WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('userList.index'))
