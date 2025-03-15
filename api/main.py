from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, IntegerField
from wtforms.validators import DataRequired, URL
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String
import os

# Initialize Flask / Bootstrap
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "any-string-you-want-just-keep-it-secret"
bootstrap = Bootstrap5(app)

# Fix DATABASE_URL for Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database Model Setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Data(db.Model):
    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer)  # Renamed to avoid SQLAlchemy conflicts
    topic: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)

# Ensure database tables exist
with app.app_context():
    db.create_all()

# Flask Form for Submission
class ShareForm(FlaskForm):
    user_id = IntegerField("Person ID", validators=[DataRequired()], render_kw={"placeholder": "Spencer[1] or Miracle[2] (Required)"})
    topic = StringField("Topic", validators=[DataRequired()], render_kw={"placeholder": "Enter a topic (e.g. 'Python SQLite')"})
    link = URLField("URL", validators=[URL()], render_kw={"placeholder": "https://www.example.com/"})
    submit = SubmitField(label="Submit")

# Routes
@app.route("/")
def go_index():
    return render_template("index.html")

@app.route("/index_upload")
def go_index_upload():
    return render_template("index_upload.html")

@app.route("/share", methods=["GET", "POST"])
def go_share():
    share_form = ShareForm()
    if share_form.validate_on_submit():
        user_id = share_form.user_id.data
        topic = share_form.topic.data
        url = share_form.link.data
        
        entry = Data(user_id=user_id, topic=topic, url=url)
        
        try:
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("go_index_upload"))
        except Exception as e:
            db.session.rollback()
            return render_template("error.html", error_message=str(e))  # Displays error safely
    return render_template("share.html", form=share_form)

@app.route("/learn")
def go_learn():
    entries = Data.query.all()
    return render_template("learn.html", entries=entries)

# Production Server for Vercel
if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
