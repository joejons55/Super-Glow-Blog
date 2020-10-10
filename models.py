from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
import os
from flask_fontawesome import FontAwesome

app = Flask(__name__)

ENV = 'prod'
if ENV == 'dev':
      app.debug = True
      app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///flasql'
else:
      app.debug = False
      app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://xbhpsrrwtmoglp:8563e26d79dd14521a37a916b2904114d4caa4bd64bfb639bfdb38b920fb22a7@ec2-54-161-58-21.compute-1.amazonaws.com:5432/d8i0oe6qil0tt6'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True


db = SQLAlchemy(app)
fa = FontAwesome(app)

def connect_db(app):
  # Connect to database
  db.app = app
  db.init_app(app)


# create login functionality and login_required pages
login = LoginManager(app)
login.login_view = "login"

connect_db(app)
app.config['SECRET_KEY'] = "1234567890qwertyuiop"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

db.create_all()

class Author(db.Model, UserMixin):
  __tablename__ = "author"
  id = db.Column(db.Integer, primary_key = True, autoincrement = True)
  username = db.Column(db.String(20), index=True, unique=True)
  password = db.Column(db.String(128))
  users = db.relationship("User", backref="author", cascade="all, delete-orphan")

  def set_password(self, password):
        self.password = generate_password_hash(password)

  def check_password(self, password):
      return check_password_hash(self.password, password)

  @login.user_loader
  def load_user(author):
      return Author.query.get(int(author))

  def __repr__(self):
      return f"<Author {self.username}, {self.password}>"

class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key = True, autoincrement = True)
  first_name = db.Column(db.String(20))
  last_name = db.Column(db.String(30))
  author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable = False)
  posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")

  @property
  def get_full_name(self):
    # Display full name 
    return f"{self.first_name} {self.last_name}" 

  def __repr__(self):
      return f"<User {self.first_name} {self.last_name} {self.author_id}>"


class Post(db.Model):
  __tablename__ = "posts"
  id = db.Column(db.Integer, primary_key = True, autoincrement = True)
  title = db.Column(db.String(20), nullable = False)
  content = db.Column(db.String(200),nullable = False)
  createdAt = db.Column(db.DateTime, nullable = False, default=datetime.datetime.now)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'),nullable = False)
  tags = db.relationship('Tag', secondary="posts_tags", backref="post")

  def __repr__(self):
    # Show info about Post
    return f"<Post {self.title} {self.content}>"

  
  @property
  def simple_post_time(self):
    # Post Friendly Formatted Date
    return self.createdAt.strftime("%a %b %d  %Y, %I:%M %p")

  
class Tag(db.Model):
  __tablename__ = 'tags'
  id = db.Column(db.Integer, primary_key = True, autoincrement = True)
  name = db.Column(db.String(15), nullable = False, unique = True)
  posts = db.relationship('Post', secondary="posts_tags", backref="tag")

  def __repr__(self):
    # Show info about Post
    return f"<Tag {self.name}>"

class PostTag(db.Model):
  __tablename__ = 'posts_tags'
  post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), primary_key = True)
  tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), primary_key = True)

