from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo

app = Flask(__name__)
app.config['SECRET_KEY'] = "secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Force Werkzeug to use sha256 instead of scrypt for compatibility
import os
os.environ['WERKZEUG_HASH_METHOD'] = 'sha256'

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(128), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    joined_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    journal_entries = db.relationship('JournalEntry', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        # Use sha256 method explicitly for compatibility
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime(), index=True, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return '<JournalEntry {}>'.format(self.title)


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


#Login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('login')


class JournalEntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Save Entry')


#registration route
@app.route('/register', methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegistrationForm(meta={'csrf': False})
    if form.validate_on_submit():
        # Check if user already exists
        if User.query.filter_by(email=form.email.data).first():
            flash('Email already registered. Please use a different email.', 'error')
            return render_template('register.html', title='Register', form=form)
        
        if User.query.filter_by(username=form.username.data).first():
            flash('Username already taken. Please choose a different username.', 'error')
            return render_template('register.html', title='Register', form=form)
        
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


#user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm(meta={'csrf': False})
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route("/")
def index():
    current_users = User.query.all()
    return render_template('landing_page.html', current_users=current_users)


# Journal routes
@app.route('/journal')
@login_required
def journal():
    entries = current_user.journal_entries.order_by(JournalEntry.created_at.desc()).all()
    return render_template('journal.html', entries=entries)


@app.route('/journal/new', methods=['GET', 'POST'])
@login_required
def new_journal_entry():
    form = JournalEntryForm(meta={'csrf': False})
    if form.validate_on_submit():
        entry = JournalEntry(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        db.session.add(entry)
        db.session.commit()
        flash('Journal entry created successfully!', 'success')
        return redirect(url_for('journal'))
    return render_template('new_journal_entry.html', form=form)


@app.route('/journal/<int:entry_id>')
@login_required
def view_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You can only view your own journal entries.', 'error')
        return redirect(url_for('journal'))
    return render_template('view_journal_entry.html', entry=entry)


@app.route('/journal/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You can only edit your own journal entries.', 'error')
        return redirect(url_for('journal'))
    
    form = JournalEntryForm(meta={'csrf': False})
    if form.validate_on_submit():
        entry.title = form.title.data
        entry.content = form.content.data
        entry.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Journal entry updated successfully!', 'success')
        return redirect(url_for('view_journal_entry', entry_id=entry.id))
    elif request.method == 'GET':
        form.title.data = entry.title
        form.content.data = entry.content
    
    return render_template('edit_journal_entry.html', form=form, entry=entry)


@app.route('/journal/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_journal_entry(entry_id):
    entry = JournalEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        flash('You can only delete your own journal entries.', 'error')
        return redirect(url_for('journal'))
    
    db.session.delete(entry)
    db.session.commit()
    flash('Journal entry deleted successfully!', 'success')
    return redirect(url_for('journal'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)


