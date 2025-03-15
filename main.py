from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, URLField, IntegerField
from wtforms.validators import DataRequired, URL
from flask_bootstrap import Bootstrap5
# SQL-Alchemy code
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

# Initialize Flask / Bootstrap / SecretKey wtforms
app = Flask(__name__)
app.secret_key = "any-string-you-want-just-keep-it-secret"
bootstrap = Bootstrap5(app)

# Create Form for Share Page
class ShareForm(FlaskForm):
    id = IntegerField("Person ID", validators=[DataRequired()], render_kw={"placeholder": "Spencer[1] or Miracle[2] (Required)"})
    topic = StringField("Topic", validators=[DataRequired()], render_kw={"placeholder": "Enter a topic (e.g. 'Python SQLite')"})
    link = URLField("URL", validators=[URL()], render_kw={"placeholder": "https://www.example.com/"})
    submit = SubmitField(label="Submit")

# Create Database
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///local_database.db"

# Create Extension
db = SQLAlchemy(model_class=Base)
# Call flask app with extension
db.init_app(app)

# Create table
class Data(db.Model):
    record_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    id: Mapped[int] = mapped_column(Integer)
    topic: Mapped[str] = mapped_column(String)
    url: Mapped[str] = mapped_column(String)

# Create table schema 
with app.app_context():
    db.create_all()

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
        id = share_form.id.data
        topic = share_form.topic.data
        url = share_form.link.data
        
        entry = Data(id=id, topic=topic, url=url)
        
        try:
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("go_index_upload"))
        except Exception as e:
            db.session.rollback()
            return f"Error: {e}"
    return render_template("share.html", form=share_form)

@app.route("/learn")
def go_learn():
    entries = Data.query.all()
    return render_template("learn.html", entries=entries)

if __name__ == "__main__":
    app.run(debug=True, port=6969)