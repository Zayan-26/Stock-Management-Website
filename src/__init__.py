from flask import Flask
import sqlite3
from .auth import login_manager, load_user


def create_app():
  app = Flask(__name__)
  app.config['SECRET_KEY'] = 'ASsgolis235g'

  from .views import views
  from .auth import auth

  app.register_blueprint(views, url_prefix='/')
  app.register_blueprint(auth, url_prefix='/')


  login_manager.login_view = 'auth.login'
  login_manager.init_app(app)


  return app
