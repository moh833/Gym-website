import secrets
import os
from functools import wraps
from flask import render_template, url_for, flash, redirect, request, abort, session
from gym import app, db, bcrypt, mail
from gym.models import User, Employee
from gym.forms import (RegistrationForm, LoginForm, UserAccountForm,
 						EmployeeAccountForm, RequestResetForm, ResetPasswordForm,
						 AddEmpForm, SearchUserForm, ManageUserForm)
from flask_login import login_user, current_user, logout_user, login_required

from flask_mail import Message

import datetime

# def check_employee(func):
# 	@wraps(func)
# 	def wrapper(*args, **kwargs):
# 		if session['ROLE'] == 'employee':
# 		# if Employee.query.filter_by(email=current_user.email).first():
# 			return func(*args, **kwargs)
# 		return redirect(url_for('login'))
# 	return wrapper

# def check_user(func):
# 	@wraps(func)
# 	def wrapper(*args, **kwargs):
# 		if session['ROLE'] == 'user':
# 		# if User.query.filter_by(email=current_user.email).first():
# 			return func(*args, **kwargs)
# 		return redirect(url_for('login'))
# 	return wrapper


def required_roles(*roles):
	def wrapper(func):
		@wraps(func)
		def wrapped(*args, **kwargs):
			if session['ROLE'] in roles:
				return func(*args, **kwargs)
			flash('You don\'t have permission to access this page!', 'danger')
			return redirect(url_for('home'))
		return wrapped
	return wrapper


# @app.context_processor
# def isemployee():
# 	if current_user.is_authenticated:
# 		if Employee.query.filter_by(email=current_user.email).first():
# 			return dict(is_emp=True)
# 	return dict(is_emp=False)
	# return dict(is_emp=isinstance(current_user, Employee))

# @app.context_processor
# def employee_role():
# 	if current_user.is_authenticated:
# 		if current_user.role:
# 			return dict(emp_role=current_user.role)
# 	return dict(emp_role=False)

@app.context_processor
def isuser():
	if current_user.is_authenticated:
		if User.query.filter_by(email=current_user.email).first():
			return dict(is_user=True)
	return dict(is_user=False)
	# return dict(is_user=isinstance(current_user, User))


def get_coaches():
	try:
		employees = Employee.query.filter_by(role='coach').all()
		return [('', 'Coach')] + [(str(emp.id), emp) for emp in employees]
	except:
		return [('', 'Coach')]


@app.route('/')
@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/about/')
def about():
	return render_template('about.html', title='About')

@app.route('/register/', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		# ask if the user is already logged in
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(fname=form.fname.data, lname=form.lname.data, email=form.email.data.lower(),
					 phone=form.phone.data, gender=form.gender.data,
					  password=hashed_password)
		db.session.add(user)
		db.session.commit()
		# flash('Your account has been created! You are now able to login', 'success')
		# return redirect(url_for('login'))
		flash(f'Welcome, {user.fname}', 'success')
		login_user(user)
		session['ROLE'] = 'user'
		# next_page = request.args.get('next')
		# return redirect(next_page) if next_page else redirect(url_for('home'))
		return redirect(url_for('home'))
	return render_template('register.html', title='Register', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		employee = Employee.query.filter_by(email=form.email.data.lower()).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			session['ROLE'] = 'user'
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		elif employee and bcrypt.check_password_hash(employee.password, form.password.data):
			login_user(employee, remember=form.remember.data)
			session['ROLE'] = current_user.role
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Invalid credentials. Try Again.', 'danger')
	return render_template('login.html', title='Login', form=form)

@app.route('/logout')
@login_required
def logout():
	logout_user()
	session.pop('ROLE', None)
	return redirect(url_for('home'))


@app.route('/user_account', methods=['GET', 'POST'])
@login_required
@required_roles('user')
# @check_user
def user_account():
	form = UserAccountForm()
	days_left = 0
	if form.validate_on_submit():
		current_user.fname = form.fname.data
		current_user.lname = form.lname.data
		current_user.email = form.email.data.lower()
		current_user.phone = form.phone.data
		if form.birth_year.data:
			current_user.birth_year = int(form.birth_year.data)
		if form.rate.data:
			current_user.rate = int(form.rate.data)
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('user_account'))
	elif request.method == 'GET':
		if current_user.rate:
			form.rate.default = current_user.rate
		if current_user.birth_year:
			form.birth_year.default = current_user.birth_year
		form.process()
		if current_user.sup_start:
			form.sup_start.data = current_user.sup_start
		if current_user.sup_end:
			form.sup_end.data = current_user.sup_end

			days_left = abs(( current_user.sup_end.date() - datetime.datetime.now().date()).days)
			if days_left <= 0:
				days_left = 0
				flash('Your subscription has expired!', 'danger')
		if current_user.coach:
			form.coach.data = current_user.coach
		if current_user.months:
			form.months.data = current_user.months
		if current_user.payment:
			form.payment.data = current_user.payment
		form.fname.data = current_user.fname
		form.lname.data = current_user.lname
		form.email.data = current_user.email
		form.phone.data = current_user.phone
		form.change.data = current_user.change
		form.discount.data = current_user.discount
		form.points.data = current_user.points

		# initiate with the current data in the form
	return render_template('user_account.html', title='Account', form=form, days_left=days_left)




@app.route('/employee_account', methods=['GET', 'POST'])
@login_required
@required_roles('receptionist', 'coach', 'admin')
# @check_employee
def employee_account():
	form = EmployeeAccountForm()
	if form.validate_on_submit():
		current_user.fname = form.fname.data
		current_user.lname = form.lname.data
		current_user.email = form.email.data.lower()
		current_user.phone = form.phone.data
		if current_user.role != 'admin':
			current_user.salary = form.salary.data
			current_user.incentive = form.incentive.data
		# change the data in the database for this user
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('employee_account'))
	elif request.method == 'GET':
		form.fname.data = current_user.fname
		form.lname.data = current_user.lname
		form.email.data = current_user.email
		form.phone.data = current_user.phone
		if current_user.role != 'admin':
			form.salary.data = current_user.salary
			form.incentive.data = current_user.incentive
		# initiate with the current data in the form
	return render_template('employee_account.html', title='Account', form=form)




@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
@required_roles('receptionist', 'admin')
def search_user():
	form = SearchUserForm()
	if form.validate_on_submit():
		if form.search_by.data == 'id':
			user = User.query.filter_by(id=int(form.search.data)).first()
		elif form.search_by.data == 'phone':
			user = User.query.filter_by(phone=form.search.data).first()
		elif form.search_by.data == 'email':
			user = User.query.filter_by(email=form.search.data).first()
		if user:
			flash(f'{user}', 'success')
			return redirect(url_for('manage_user', id=user.id))
		else:
			flash('That user doesn\'t exist', 'danger')
	return render_template('search_user.html', title='Search for User', form=form)



@app.route('/manage_users/<id>', methods=['GET', 'POST'])
@login_required
@required_roles('receptionist', 'admin')
def manage_user(id):
	form = ManageUserForm()
	user = User.query.filter_by(id=int(id)).first()
	if not user:
		return redirect(url_for('search_user'))
	days_left = 0
	if form.validate_on_submit():
		p = app.config['FEES_MONTH'] * int(form.months.data)
		if user.discount:
			p -= float(user.discount)
		if user.change:
			p -= float(user.change)
		user.payment = form.payment.data
		user.change = form.payment.data - p
		user.discount = 0
		left_days = 0
		if user.sup_start:
			left_days = abs(( user.sup_end.date() - datetime.datetime.now().date()).days)
			if left_days <= 0:
				left_days = 0
		user.sup_start = form.sup_start.data
		user.sup_end = form.sup_start.data + datetime.timedelta(days=(30 * int(form.months.data))) + datetime.timedelta(days=int(left_days))
		user.months = form.months.data
		if form.coach.data:
			user.employee_id = int(form.coach.data)
		user.points += app.config['POINT_MONTH'] * int(form.months.data)
		db.session.commit()
		flash('User\'s subscription has been updated', 'success')
		return redirect(url_for('manage_user', id=id))
	elif request.method == 'GET':
		form.coach.choices = get_coaches()
		if user.coach:
			form.coach.default = user.coach.id
		form.process()
		if user.sup_start:
			form.sup_start_view.data = user.sup_start
			days_left = abs(( user.sup_end.date() - datetime.datetime.now().date()).days)
			if days_left <= 0:
				days_left = 0
				flash('User\'s subscription has expired!', 'danger')
		if user.sup_end:
			form.sup_end_view.data = user.sup_end
		if user.coach:
			form.coach_view.data = user.coach
		form.id.data = user.id
		form.fname.data = user.fname
		form.lname.data = user.lname
		form.email.data = user.email
		form.phone.data = user.phone
		form.change.data = user.change
		form.discount.data = user.discount
		form.points.data = user.points
	return render_template('manage_user.html', title='Manage User', form=form, days_left=days_left, user=user)




@app.route('/show_trainers')
@login_required
@required_roles('coach')
def show_trainers():
	if current_user.students:
		rates = [int(s.rate) for s in current_user.students if s.rate]
		rates = [ x for x in rates if x!=0 ]
		rate = (sum(rates) / len(rates)) if rates else 0
		return render_template('show_trainers.html', title='Current trainers'
		, students=current_user.students, rate=rate, num_of_students=len(current_user.students))
	flash('You don\'t have any trainers yet', 'success')
	return redirect(url_for('home'))




@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
@required_roles('admin')
def add_emp():
	form = AddEmpForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		emp = Employee(fname=form.fname.data, lname=form.lname.data, email=form.email.data.lower(),
					 phone=form.phone.data,role=form.role.data , password=hashed_password)
		if form.salary.data:
			emp.salary = float(form.salary.data)
		if form.incentive.data:
			emp.incentive = float(form.incentive.data)
		db.session.add(emp)
		db.session.commit()
		flash('A new Employee has been added successfully', 'success')
		return redirect(url_for('home'))
	return render_template('add_employee.html', title='Add Employee', form=form)





#-------------------------------------------------

# 'noreply@demo.com'
def send_reset_email(user):
	token = user.get_reset_token()
	msg = Message('Password Reset Request',
				sender=app.config['MAIL_USERNAME'],
				recipients=[user.email])
	msg.body = f'''To reset your password, visit the following link or copy it to your browser:
{url_for('reset_token', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
	mail.send(msg)


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data.lower()).first()
		emp = Employee.query.filter_by(email=form.email.data.lower()).first()
		if emp:
			send_reset_email(emp)
		elif user:
			send_reset_email(user)
		flash('An email has been sent with instructions to reset your password.', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)
	


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	emp = Employee.verify_reset_token(token)
	user = User.verify_reset_token(token)
	
	if user is None and emp is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('reset_request'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		if emp:
			emp.password = hashed_password
		elif user:
			user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! You are now able to login', 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)


# --------------------------errors--------------------------------------


@app.errorhandler(404)
def error_404(error):
	return render_template('errors/404.html'), 404


@app.errorhandler(403)
def error_403(error):
	return render_template('errors/403.html'), 403


@app.errorhandler(500)
def error_500(error):
	return render_template('errors/500.html'), 500
