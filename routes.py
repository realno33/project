from extensions import app
from flask import  render_template,  redirect, url_for, request, flash, send_from_directory, abort, jsonify
from sqlalchemy import or_
from forms import RegisterForm, LoginForm, PostForm, CommentForm, ReplyForm,  SearchForm
from players import players
from models import User, Post, Comment, Vote, Follower
#from data import new_user
from extensions import db
from flask_Login import logout_user, login_user, current_user, login_required
import os
from werkzeug.utils import secure_filename
from operator import add
from datetime import datetime, timedelta
from random import shuffle


@app.route("/")
def home():
    return render_template("index.html", players=players)



@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(user_name=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect("/home")
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        exists = User.query.filter(User.user_name==form.username.data).first()
        if exists and exists.password == form.password.data:
            login_user(exists)
            return redirect("/home")
    return render_template("login.html", form=form)



@app.route("/logout")
def logout():
    logout_user()
    return redirect("/")



@app.route('/post', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        file = form.file.data
        if file:
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(f"static/{file_path}")
        else:
            file_path = None

        new_post = Post(
            text=form.text.data,
            file_path=file_path,
            user_id=current_user.id,
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Post created successfully', 'success')
        return redirect(url_for('index'))
    
    return render_template('post.html', form=form)

@app.route('/home')
@login_required
def index():
    form = SearchForm()
    yesterday = datetime.now() - timedelta(days=1)


    recent_entries = db.session.query(Post).filter(Post.created_at >= yesterday).all()

    shuffle(recent_entries)

    return render_template('home.html', posts=recent_entries, form=form)










@app.route('/following')
@login_required
def friend():
    form = SearchForm()
    yesterday = datetime.now() - timedelta(days=1)


    recent_entries_followeds = db.session.query(Post).filter(Post.created_at >= yesterday) \
        .join(Follower,  Follower.followed_id == Post.user_id).filter(current_user.id == Follower.follower_id).all()
    
    recent_entries_not_followeds = db.session.query(Post).filter(Post.created_at >= yesterday) \
        .outerjoin(Follower,  Follower.followed_id == Post.user_id).filter(or_(current_user.id != Follower.follower_id, Follower.follower_id == None)).all()

    
    shuffle(recent_entries_followeds)

    shuffle(recent_entries_not_followeds)


    recent_entries = recent_entries_followeds
    # recent_entries.extend(recent_entries_not_followeds)
    
    
    return render_template('following.html', posts=recent_entries, form=form)

@app.route('/post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def post_detail(post_id):
    yesterday = datetime.now() - timedelta(days=1)
    post = Post.query.get_or_404(post_id)
    if post.created_at < yesterday:
        return abort(404)
    form = CommentForm()
    reply_form = ReplyForm()
    
    if form.validate_on_submit() and 'comment' in request.form:
        new_comment = Comment(text=form.text.data, user_id=current_user.id, post_id=post_id)
        db.session.add(new_comment)
        db.session.commit()
        flash('Comment added successfully!', 'success')
        return redirect(url_for('post_detail', post_id=post_id))

    if reply_form.validate_on_submit() and 'reply' in request.form:
        parent_id = int(request.form['parent_id'])
        new_reply = Comment(text=reply_form.text.data, user_id=current_user.id, post_id=post_id, parent_id=parent_id)
        db.session.add(new_reply)
        db.session.commit()
        flash('Reply added successfully!', 'success')
        return redirect(url_for('post_detail', post_id=post_id))

    comments = Comment.query.filter_by(post_id=post_id, parent_id=None).all()
    return render_template('post_detail.html', post=post, form=form, comments=comments, reply_form=reply_form)



@app.route('/upvote/<int:post_id>', methods=['POST'])
@login_required
def upvote(post_id):
    post = Post.query.get_or_404(post_id)
    existing_vote = Vote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_vote:
        return redirect(url_for('index'))
    
    new_vote = Vote(user_id=current_user.id, post_id=post_id, vote_type='upvote')
    post.upvote_count += 1

    db.session.add(new_vote)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/downvote/<int:post_id>', methods=['POST'])
@login_required
def downvote(post_id):
    post = Post.query.get_or_404(post_id)
    if post.downvote_count is None:
        post.downvote_count = 0
    existing_vote = Vote.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_vote:
        return redirect(url_for('index'))
    
    new_vote = Vote(user_id=current_user.id, post_id=post_id, vote_type='downvote')
    post.downvote_count += 1

    db.session.add(new_vote)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    if user == current_user:
        return redirect(url_for('main.profile', username=username))
    current_user.follow(user)
    db.session.commit()
    return redirect(url_for('profile', username=username, ))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    if user == current_user:
        return redirect(url_for('main.profile', username=username))
    current_user.unfollow(user)
    db.session.commit()
    return redirect(url_for('profile', username=username))





@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    form = SearchForm()
    users = []
    print("aleqds")
    #if form.validate_on_submit():
    query = form.query.data
    if not query:
        users = []
    else:        
        users = User.query.filter(User.user_name.ilike(f'%{query}%')).all()
    print(f"Search query: {query}")  
    print(f"Found users: {users}")  
    return render_template('search.html', form=form, users=users)


@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(user_name=username).first_or_404()
    is_following = current_user.is_following(user)

    yesterday = datetime.now() - timedelta(days=1)
    
    
    recent_entries = db.session.query(Post).filter(Post.created_at >= yesterday).filter(Post.user == user).all()


    
    return render_template('profile.html', user=user, posts=recent_entries, is_following=is_following)


