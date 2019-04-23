from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from datetime import datetime
from gym import db, login_manager, app, admin
from flask_login import UserMixin, current_user
from flask import session
from flask_admin.contrib.sqla import ModelView
from flask_admin import BaseView, expose

from flask import url_for, flash, redirect



@login_manager.user_loader
def load_user(user_id):
	if session['ROLE'] == 'user':
		return User.query.get(int(user_id))
	# elif session['ROLE'] == 'employee':
	else:
		return Employee.query.get(int(user_id))


# @login_manager.user_loader
# def load_employee(emp_id):
# 	return Employee.query.get(int(emp_id))


class User(db.Model, UserMixin):
	# UserMixin manages our sessions
	id = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String(50), nullable=False)
	lname = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	phone = db.Column(db.String(15), unique=True)
	gender = db.Column(db.String(10), nullable=False)
	birth_year = db.Column(db.Integer)
	password = db.Column(db.String(60), nullable=False) 
	employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'))

	rate = db.Column(db.Integer)

	sup_start = db.Column(db.DateTime) 
	sup_end = db.Column(db.DateTime) 
	freeze = db.Column(db.Boolean, default=False)
	#datetime.utcnow
	months = db.Column(db.Integer)
	payment = db.Column(db.Float, default=0.0)
	change = db.Column(db.Float, default=0.0)
	discount = db.Column(db.Float, default=0.0)
	points = db.Column(db.Integer, default=0)



	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"Trainer( {self.fname} {self.lname} )"


class Employee(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	fname = db.Column(db.String(30), nullable=False)
	lname = db.Column(db.String(30), nullable=False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	phone = db.Column(db.String(15), unique=True, nullable=False)
	role = db.Column(db.String(20), nullable=False)
	password = db.Column(db.String(60), nullable=False)

	salary = db.Column(db.Float)
	incentive = db.Column(db.Float)
	students = db.relationship('User', backref='coach', lazy=True)


	def get_reset_token(self, expires_sec=1800):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'emp_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			emp_id = s.loads(token)['emp_id']
		except:
			return None
		return Employee.query.get(emp_id)


	def __repr__(self):
		return f"Coach( {self.fname} {self.lname} )"






class UserView(ModelView):

	can_delete = False
	# can_create = False
	# can_edit = False
	can_view_details = True
	column_details_exclude_list = ['password', 'rate', 'freeze']
	column_list = ['id', 'fname', 'lname', 'email', 'phone', 'coach']
	# column_exclude_list = ['password', 'rate']
	column_searchable_list = ['id', 'phone', 'email']
	column_filters = ['gender']


	# column_editable_list = ['points', 'discount', 'change', 'payment', 'months',
	# 'sup_start']
	# form_columns = ('id', 'fname', 'lname')
	form_excluded_columns = ['rate', 'birth_year', 'password', 'freeze']
	can_export = True
	
	
	column_display_pk = True

	form_choices = {
    'gender': [
        ('male', 'Male'),
        ('female', 'Female')
    ]
}

	form_choices = {
    'months': [
        ('1', 'Month'),
        ('2', 'Two Months'),
		('3', 'Three Months')
    ]
}

# disable in creation and editing
	form_widget_args = {
        'fname': {
            'readonly': True
        },
        'lname': {
            'readonly': True
        },
        'email': {
            'readonly': True
        },
        'phone': {
            'readonly': True
        },
        'gender': {
            'readonly': True
        },
    }
	
	page_size = 30

	def is_accessible(self):
		if current_user.is_authenticated and session['ROLE'] in ['admin', 'receptionist']:
			return True

	def inaccessible_callback(self, name, **kwargs):
		flash('You don\'t have permission to access this page!', 'danger')
		return redirect(url_for('home'))




class EmployeeView(ModelView):

	can_delete = False
	can_view_details = True
	column_details_exclude_list = ['password']
	page_size = 30
	# create_modal = True
	# edit_modal = True
	# form_excluded_columns = ['email']
	column_searchable_list = ['id', 'phone', 'email']
	can_export = True
	form_excluded_columns = ['password']

	column_list = ['id', 'fname', 'lname', 'email', 'phone']
	# column_editable_list = ['salary', 'incentive', 'students']

	# form_edit_rules = ('email', 'fname', 'lname')


	# form_args = {
	# 	'fname': {
	# 		'label': 'First Name',
	# 		'validators': [DataRequired()]
	# 	}
	# }

	def is_accessible(self):
		if current_user.is_authenticated and session['ROLE'] in ['admin']:
			return True

	def inaccessible_callback(self, name, **kwargs):
		flash('You don\'t have permission to access this page!', 'danger')
		return redirect(url_for('home'))



admin.add_view(UserView(User, db.session))
admin.add_view(EmployeeView(Employee, db.session))



