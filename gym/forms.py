from gym.models import User, Employee
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, FloatField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.fields.html5 import DateField


from gym import app


choices = { 'gender' : [('', 'Gender'), ('male', 'Male'), ('female', 'Female')],

  			'rate' : [('0', 'Rate'), ('1', '1'), 
  						('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
  			'search_by' : [('id', 'ID'), 
  						('phone', 'Phone'), ('email', 'Email')],
  			'months' : [('', 'Months'), 
  						('1', 'Month'), ('2', '2 Months'), ('3', '3 Months')],
  			'role' : [('', 'Role'), 
  						('receptionist', 'Sales and Receptionist'), ('coach', 'Coach'), ('admin', 'Admin')]
  			}

birth_years = [('', 'Birth Year')] + [(str(x), str(x)) for x in range(2018, 1900, -1)]



class RegistrationForm(FlaskForm):

	# add parameter render_kw={'placeholder': 'Username'}
	fname = StringField('First Name', validators=[DataRequired(), Length(max=50)], render_kw={'autofocus': 'true'})
	lname = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
	phone = StringField('Phone', validators=[DataRequired(), Length(max=15)])
	gender = SelectField('Gender', validators=[DataRequired()], choices = choices.get('gender'))
	password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(max=50), EqualTo('password', message='Password doesn\'t match.')])
	submit = SubmitField('Sign Up')



	def validate_email(self, email):
		user = User.query.filter_by(email=email.data.lower()).first()
		employee = Employee.query.filter_by(email=email.data.lower()).first()
		if user or employee:
			raise ValidationError('That email is taken. Please choose a different one.')

	def validate_phone(self, phone):
		user = User.query.filter_by(phone=phone.data).first()
		employee = Employee.query.filter_by(phone=phone.data).first()
		if user or employee:
			raise ValidationError('That Phone is already registered.')
		try:
			n = int(phone.data)
		except:
			raise ValidationError('Please enter a valid phone Number.')
		# if len(phone.data) != 11 or phone.data[:2] != '01':
			# raise ValidationError('Please enter a valid phone Number.')




class LoginForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)], render_kw={'autofocus': 'true'})
	password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')


class UserAccountForm(FlaskForm):
	fname = StringField('First Name', validators=[DataRequired(), Length(max=50)], render_kw={'autofocus': 'true'})
	lname = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
	phone = StringField('Phone', validators=[DataRequired()])
	birth_year = SelectField('Birth Year', choices = birth_years)
	rate = SelectField('Rate Your Captain', choices = choices.get('rate'))

	sup_start = DateField('Start Date', format='%Y-%m-%d', render_kw={'disabled': 'true'})
	sup_end = DateField('End Date', format='%Y-%m-%d', render_kw={'disabled': 'true'})
	coach = StringField('Coach', render_kw={'disabled': 'true'})
	months = StringField('Months', render_kw={'disabled': 'true'})
	payment = FloatField('Last Payment', render_kw={'disabled': 'true'})
	change = FloatField('Change', render_kw={'disabled': 'true'})
	discount = FloatField('Discount', render_kw={'disabled': 'true'})
	points = IntegerField('Points', render_kw={'disabled': 'true'})

	submit = SubmitField('Update')


	def validate_phone(self, phone):
		if phone.data != current_user.phone:
			user = User.query.filter_by(phone=phone.data).first()
			employee = Employee.query.filter_by(phone=phone.data).first()
			if user or employee:
				raise ValidationError('That Phone is another\'s user, Please choose another.')
			try:
				n = int(phone.data)
			except:
				raise ValidationError('Please enter a valid phone Number.')
			# if len(phone.data) != 11 or phone.data[:2] != '01':
				# raise ValidationError('Please enter a valid phone Number.')

	def validate_email(self, email):
		if email.data.lower() != current_user.email:
			user = User.query.filter_by(email=email.data.lower()).first()
			employee = Employee.query.filter_by(email=email.data.lower()).first()
			if user or employee:
				raise ValidationError('That email is taken. Please choose a different one.')


class EmployeeAccountForm(FlaskForm):
	fname = StringField('First Name', validators=[DataRequired(), Length(max=50)], render_kw={'autofocus': 'true'})
	lname = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
	phone = StringField('Phone', validators=[DataRequired()])
	salary = FloatField('Salary', render_kw={'disabled': 'true'})
	incentive = FloatField('Incentive', render_kw={'disabled': 'true'})
	submit = SubmitField('Update')


	def validate_phone(self, phone):
		if phone.data != current_user.phone:
			user = User.query.filter_by(phone=phone.data).first()
			employee = Employee.query.filter_by(phone=phone.data).first()
			if user or employee:
				raise ValidationError('That Phone is another\'s user, Please choose another.')
			try:
				n = int(phone.data)
			except:
				raise ValidationError('Please enter a valid phone Number.')
			# if len(phone.data) != 11 or phone.data[:2] != '01':
				# raise ValidationError('Please enter a valid phone Number.')

	def validate_email(self, email):
		if email.data.lower() != current_user.email:
			user = User.query.filter_by(email=email.data.lower()).first()
			employee = Employee.query.filter_by(email=email.data.lower()).first()
			if user or employee:
				raise ValidationError('That email is taken. Please choose a different one.')



class SearchUserForm(FlaskForm):
	search = StringField('Search', validators=[DataRequired(), Length(max=100)], render_kw={'autofocus': 'true'})
	search_by = SelectField('Serach By', validators=[DataRequired()], choices = choices.get('search_by'))
	submit = SubmitField('Search')


	def validate_search(self, search):
		if self.search_by.data == 'id':
			try:
				int(search.data)
			except:
				raise ValidationError('ID should be a number.')
		elif self.search_by.data == 'phone':
			try:
				int(search.data)
			except:
				raise ValidationError('Please enter a valid phone Number.')
			# if len(search.data) != 11 or search.data[:2] != '01':
				# raise ValidationError('Please enter a valid phone Number.')


class ManageUserForm(FlaskForm):
	id = IntegerField('ID', render_kw={'disabled': 'true'})
	fname = StringField('First Name', render_kw={'disabled': 'true'})
	lname = StringField('Last Name', render_kw={'disabled': 'true'})
	email = StringField('Email', render_kw={'disabled': 'true'})
	phone = StringField('Phone', render_kw={'disabled': 'true'})
	sup_start = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
	sup_start_view = DateField('Start Date', format='%Y-%m-%d', render_kw={'disabled': 'true'})
	sup_end_view = DateField('End Date', format='%Y-%m-%d', render_kw={'disabled': 'true'})

	coach_view = StringField('Coach', render_kw={'disabled': 'true'})

	# choices for coach field added in the route
	coach = SelectField('Coach', validators=[DataRequired()])
	months = SelectField('Months', validators=[DataRequired()], choices=choices.get('months'))
	payment = FloatField('Payment', validators=[DataRequired()])
	change = FloatField('Change', render_kw={'disabled': 'true'})
	discount = FloatField('Discount', render_kw={'disabled': 'true'})
	points = IntegerField('Points', render_kw={'disabled': 'true'})

	submit = SubmitField('Update Subscription')





class AddEmpForm(FlaskForm):
	fname = StringField('First Name', validators=[DataRequired(), Length(max=50)], render_kw={'autofocus': 'true'})
	lname = StringField('Last Name', validators=[DataRequired(), Length(max=50)])
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=100)])
	phone = StringField('Phone', validators=[DataRequired(), Length(max=15)])
	role = SelectField('Role', validators=[DataRequired()], choices = choices.get('role'))
	salary = FloatField('Salary')
	incentive = FloatField('Incentive')
	password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(max=50), EqualTo('password', message='Password doesn\'t match.')])
	submit = SubmitField('Add')


	def validate_email(self, email):
		user = User.query.filter_by(email=email.data.lower()).first()
		employee = Employee.query.filter_by(email=email.data.lower()).first()
		if user or employee:
			raise ValidationError('That email is taken. Please choose a different one.')

	def validate_phone(self, phone):
		user = User.query.filter_by(phone=phone.data).first()
		employee = Employee.query.filter_by(phone=phone.data).first()
		if user or employee:
			raise ValidationError('That Phone is already registered.')
		try:
			n = int(phone.data)
		except:
			raise ValidationError('Please enter a ddd phone Number.')
		# if len(phone.data) != 11 or phone.data[:2] != '01':
			# raise ValidationError('Please enter a valid phone Number.')







#--------------------------------------------------

class RequestResetForm(FlaskForm):
	email = StringField('Email', validators=[DataRequired(), Email(), Length(max=50)], render_kw={'autofocus': 'true'})
	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data.lower()).first()
		employee = Employee.query.filter_by(email=email.data.lower()).first()
		if user is None and employee is None:
			raise ValidationError('There is no account with that email. You must register first.')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired(), Length(max=50)])
	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), Length(max=50), EqualTo('password')])
	submit = SubmitField('Reset Password')
