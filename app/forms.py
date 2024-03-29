from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, TextAreaField
from wtforms.validators import Required, Length


class LoginForm(Form):
	openid = TextField('openid', validators=[Required()])
	remember_me = BooleanField('remember_me', default=False)


class EditForm(Form):
	nickname = TextField('nickname', validators=[Required()])
	about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

	def __init__(self, original_nickname, *args, **kwargs):
	    Form.__init__(self, *args, **kwargs)
	    self.original_nickname = original_nickname

	def validate(self):
	    if not Form.validate(self):
	        return False
	    if self.nickname.data == self.original_nickname:
	        return True
	    if self.nickname.data != User.make_valid_nickname(self.nickname.data):
	    	self.nickname.errors.append(gettext('This nickname has invalid characters.'))
	    	return False
	    user = User.query.filter_by(nickname=self.nickname.data).first()
	    if user != None:
	        self.nickname.errors.append('This nickname is already in use. Choose another')
	        return False
	    return True


class PostForm(Form):
	post = TextAreaField('post', validators=[Required()])


class SearchForm(Form):
	search = TextField('search', validators=[Required()])