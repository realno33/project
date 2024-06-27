from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, PasswordField, FileField,TextAreaField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField, FileAllowed

    # def __str__(self):
        # return f"{self.name}"
    

class RegisterForm(FlaskForm):
    username = StringField(label="username")
    password = PasswordField(label = "password")
    register = SubmitField(label ="register")
    
class LoginForm(FlaskForm):
    username = StringField(label="username")
    password = PasswordField(label = "password")
    login = SubmitField(label ="login")

class PostForm(FlaskForm):
    text = StringField('Text', validators=[DataRequired()])
    file = FileField('File', validators=[FileAllowed(['jpg', 'png', 'pdf', 'docx'], 'Images and documents only!')])
    submit = SubmitField('Post')

class CommentForm(FlaskForm):
    text = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Submit')

class ReplyForm(FlaskForm):
    text = TextAreaField('Text', validators=[DataRequired()])
    submit = SubmitField('Reply')

class SearchForm(FlaskForm):
    query = StringField('Search for Users', validators=[DataRequired()])
    submit = SubmitField('Search')