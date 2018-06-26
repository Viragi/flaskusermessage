from flask import Flask, request, url_for, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_modus import Modus
# from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://localhost/user"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'ihaveasecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

modus = Modus(app)
db = SQLAlchemy(app)

# toolbar = DebugToolbarExtension(app)


class User(db.Model):
    __tablename__ = "user_details"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    # studio_id = db.Column(db.Integer, db.ForeignKey('studios.id'))
    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name


MessageTag = db.Table(
    "message_tag", db.Column('id', db.Integer, primary_key=True),
    db.Column('message_id', db.Integer,
              db.ForeignKey('message_details.id', ondelete="cascade")),
    db.Column('tag_id', db.Integer,
              db.ForeignKey("tag_details.id", ondelete="cascade")))


class Message(db.Model):
    __tablename__ = "message_details"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user_details.id'))
    tags = db.relationship(
        "Tag", secondary=MessageTag, backref=db.backref("messages"))

    # studio_id = db.Column(db.Integer, db.ForeignKey('studios.id'))
    def __init__(self, message, user_id):
        self.message = message
        self.user_id = user_id


class Tag(db.Model):
    __tablename__ = "tag_details"

    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.Text)

    def __init__(self, tag_name):
        self.tag_name = tag_name


db.create_all()
# users route


@app.route("/user", methods=["GET"])
def user_list():
    print("got to user list")
    # u = User.query.get(id)
    return render_template(
        "user_index.html", users=User.query.all(), tags=Tag.query.all())


@app.route("/user/add", methods=["GET"])
def user_add_form():
    return render_template("user_add.html")


@app.route("/user", methods=["POST"])
def user_add():
    new_user = User(
        first_name=request.form['first_name'],
        last_name=request.form['last_name'])
    db.session.add(new_user)
    db.session.commit()
    url = url_for("user_list")
    return redirect(url)


@app.route("/user/edit/<int:id>", methods=["GET"])
def user_edit_form(id):
    u = User.query.get(id)

    return render_template(
        "user_edit.html",
        id=u.id,
        first_name=u.first_name,
        last_name=u.last_name,
        messages=u.messages)


@app.route("/user/<int:id>", methods=["PATCH"])
def user_edit(id):
    u = User.query.get(id)
    u.first_name = request.form["first_name"]
    u.last_name = request.form["last_name"]
    db.session.add(u)
    db.session.commit()
    return redirect("/user")


@app.route("/user/delete/<int:id>", methods=["DELETE"])
def user_delete(id):
    u = User.query.get(id)
    db.session.delete(u)
    db.session.commit()
    return redirect("/user")


# message route
@app.route("/user/<int:id>/message", methods=["GET"])
def message_form(id):
    u = User.query.get(id)
    return render_template("message_index.html", id=u.id, tags=Tag.query.all())


@app.route("/user/<int:id>/message/add", methods=["POST"])
def add_message(id):
    u = User.query.get(id)
    new_msg = Message(
        message=request.form["mtext"], user_id=u.id
    )  # but from joel: need to provide both "message" and "user_id" here
    tags_selected_ids = request.form.getlist("tag_input")
    t_list = [Tag.query.get(t) for t in tags_selected_ids]
    new_msg.tags.extend(t_list)
    db.session.add(new_msg)
    db.session.commit()
    return redirect("/user")


@app.route("/user/<int:id>/message/edit", methods=["GET"])
def edit_msg_form(id):
    m = Message.query.get(id)
    selected_tags_ids = [t.id for t in m.tags]
    return render_template(
        "messageedit.html",
        message=m,
        id=m.id,
        tags=Tag.query.all(),
        selected_tags_ids=selected_tags_ids)


@app.route("/user/<int:id>/message/edit", methods=["POST"])
def edit_msg(id):
    m = Message.query.get(id)
    m.message = request.form['mtext']
    selected_tags_id = request.form.getlist("tag_input")
    m.tags = [Tag.query.get(t) for t in selected_tags_id]
    db.session.add(m)
    db.session.commit()
    return redirect("/user")


@app.route("/tag", methods=['GET'])
def tag_form():
    return render_template("tag_form.html", messages=Message.query.all())


@app.route("/tag", methods=['POST'])
def add_tag():
    t = Tag(request.form['tag'])
    t.messages = [
        Message.query.get(mid) for mid in request.form.getlist("message_id")
    ]
    db.session.add(t)
    db.session.commit()
    return redirect("/user")


@app.route("/tag/<int:id>/edit")
def edit_tag_form(id):
    return render_template("tag_edit_form.html", tag=Tag.query.get(id))


@app.route("/tag/<int:id>/edit", methods=['PATCH'])
def edit_Tag(id):
    t = Tag.query.get(id)
    t.tag_name = request.form['tag']
    db.session.add(t)
    db.session.commit()
    return redirect("/user")


@app.route("/tag/<int:id>", methods=['DELETE'])
def del_tag(id):
    db.session.delete(Tag.query.get(id))
    db.session.commit()
    return redirect("/user")
