# from crypt import methods
from Tools.scripts.make_ctype import method
from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fe5d9c78d488adcde2b4565fca1d4c86fba8c375245e0adcd7c0793e6bfd7fb2'




# CREATE DATABASE


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)

# CREATE TABLE IN DB


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(1000))


with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods= ["POST", "GET"])
def register():
    if request.method == "POST":
        new_user = User(
            email = request.form.get("email"),
            password = generate_password_hash(request.form.get("password"), method= "pbkdf2:sha256", salt_length=8),
            name = request.form.get("name"),
        )
        db.session.add(new_user)
        db.session.commit()
        return render_template("secrets.html", name = request.form.get("name"))
    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        input = db.session.execute(db.select(User).where(User.email == request.form.get("email")))
        input_email = input.scalar()
        if input_email and check_password_hash(input_email.password, request.form.get("password")):
            login_user(input_email)
            flash("Logged in successfully!", "success")
        else:
            flash("Invalid email or password. Please try again.", "danger")
    return render_template("login.html")


@app.route('/secrets')
def secrets():
    return render_template("secrets.html")


@app.route('/logout')
def logout():
    pass


@app.route('/download')
def download():
    return send_from_directory('static', 'files/cheat_sheet.pdf', as_attachment = True)


if __name__ == "__main__":
    app.run(debug=True)
