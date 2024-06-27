from extensions import app, db
from models import User  


new_user = [User(user_name="john_doe", password="securepassword")]


with app.app_context():
    db.session.add(new_user)
    db.session.commit()


with app.app_context():
    user = User.query.filter_by(user_name="john_doe").first()
    print(user)