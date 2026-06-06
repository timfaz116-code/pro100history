from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from app.models import User
from app.extensions import db
from app.auth.forms import RegisterForm, LoginForm

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing = User.query.filter_by(email=form.email.data).first()
        if existing:
            flash('Пользователь с таким email уже существует', 'danger')
            return render_template('auth/register.html', form=form)
        user = User(
            username=form.username.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Регистрация прошла успешно! Теперь войдите в систему.', 'success')
        return redirect(url_for('auth.login'))
    if request.method == 'POST' and request.form.get('email'):
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        username = request.form.get('username', '').strip()
        if not all([email, password, username]):
            return 'Заполните все поля', 400
        if User.query.filter_by(email=email).first():
            return 'Пользователь с таким email уже существует', 409
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return 'Регистрация прошла успешно!', 200
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('dashboard.dashboard'))
        flash('Неверный email или пароль', 'danger')
    if request.method == 'POST' and request.form.get('email'):
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard.dashboard'))
        return 'Неверный email или пароль', 401
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))
