from extensions import app, db
from datetime import datetime
from flask_Login import UserMixin
from extensions import login_manager


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String, unique=True)
    password = db.Column(db.String)
    followers = db.relationship('Follower', foreign_keys='Follower.followed_id', backref='followed', lazy='dynamic')
    followed = db.relationship('Follower', foreign_keys='Follower.follower_id', backref='follower', lazy='dynamic')

    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None

    def follow(self, user):
        if not self.is_following(user):
            follow = Follower(follower_id=self.id, followed_id=user.id)
            db.session.add(follow)

    def unfollow(self, user):
        if self.is_following(user):
            Follower.query.filter_by(follower_id=self.id, followed_id=user.id).delete()
    

    def __str__(self):
        return f"{self.user_name}"
    

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)
          





    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String)
    file_path = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    upvote_count = db.Column(db.Integer, default=0)
    downvote_count = db.Column(db.Integer, default=0)
    user = db.relationship('User', backref=db.backref('posts', lazy=True, cascade="all, delete-orphan"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    comments = db.relationship('Comment', backref='post', lazy=True)

   
    
           
    def __str__(self):
        return f"{self.text}"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String)
    user_from_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user_to_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user_from = db.relationship('User', foreign_keys=[user_from_id], backref='sent_messages')
    user_to = db.relationship('User', foreign_keys=[user_to_id], backref='received_messages')


class Follower(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    text = db.Column(db.String, nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    user = db.relationship('User', backref='comments') 
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)



 
class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    vote_type = db.Column(db.String)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)



if __name__ == "__main__": 
    with app.app_context():
        db.create_all()