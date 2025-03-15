from flask import Flask
from applications.model import db, User

app = Flask(__name__)

#configuration of the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quiz_master.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "supersecretkey"

#initialization of the database
db.init_app(app)
with app.app_context():
    db.create_all()
    
    # checking if user already exists
    admin_user = User.query.filter_by(username="admin@abc.com").first()
    if not admin_user: # if user doesn't exist, create one
        # Create an inbuilt admin user
        admin = User(
            username="admin@abc.com",
            email="admin@abc.com",
            password="admin",
            fullname="Admin User"
        )
        db.session.add(admin)
        db.session.commit()

#import routes after app is created
from applications.routes import init_routes

init_routes(app) # used to register the routes


# creation of the database tables
with app.app_context():
    db.create_all()
    
if __name__ == '__main__':
    app.run(debug=True, port='8000')