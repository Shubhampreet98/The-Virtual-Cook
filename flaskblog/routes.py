import os
import secrets, itertools
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, jsonify
from flaskblog import app, db, bcrypt, mysql
from flaskblog.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, PostForm1, PostForm2
from flaskblog.models import User, Post, Dishes
from flask_login import login_user, current_user, logout_user, login_required





@app.route('/')
@app.route('/home')
def home():
	posts = Post.query.all()
	return render_template('home.html', posts=posts)

@app.route('/about')	
def about():
    return render_template('about.html')
	
@app.route('/register', methods=['GET','POST'])
def register():
	if current_user. is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash(f'Account is created, Now you can login','success')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)
	
@app.route('/login', methods=['GET','POST'])
def login():
	if current_user. is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data)
			next_page = request.args.get("next")
			return redirect(next_page) if next_page else redirect(url_for('home'))
		else:
			flash('Login Unsuccesful. Please check email and password', 'danger')

	return render_template('login.html', title='login', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profilepics', picture_fn)

	output_size = (125,125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)
	i.save(picture_path)

	return picture_fn

@app.route('/account', methods=['GET','POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
		current_user.username = form.username.data
		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == "GET":
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename= 'profilepics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route('/post/new', methods=['GET','POST'])
@login_required
def new_post():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(title=form.title.data, content=form.content.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', form=form)


@app.route('/dishes', methods=['GET','POST'])
@login_required
def dishes():
	form = PostForm1()
	if form.validate_on_submit():
		dish = Dishes.query.filter_by(dishname=form.search.data).first()
		flash(dish, 'success')	
	return render_template('dishes.html', title='Dishes', form=form)

@app.route('/dishes2', methods=['GET','POST'])
@login_required
def dishes2():
	form = PostForm2()
	data1= ''
	data2= ''
	data3= ''
	data4= ''
	t = ''
	image_file1=''
	image_file2= []
	if form.validate_on_submit():
		if request.method == 'POST':
			dish = form.search.data	
					
			cur = mysql.connection.cursor()
			query1= f"SELECT name1,Ingredients,Time,Steps FROM reciepes WHERE name1 LIKE '%{dish}%' OR Ingredients LIKE '%{dish}%' ORDER BY rating DESC"
			
			cur.execute(query1)
			
			data = cur.fetchone()

			t = cur.fetchall()


			data1 = data[0]
			data2 = data[1]
			data3 = data[2]
			data4 = data[3]
			
			mysql.connection.commit()
			cur.close()
			image_file1 = url_for('static', filename= 'dishes/' + data1 + '.jpg' )

			for i in t:
				image = url_for('static', filename= 'dishes/' + i[0] + '.jpg' )
				image_file2.append(image)
			
			flash("Results Found",'success')	

			
	return render_template('dishes2.html', title='Dishes2', y = zip(t, image_file2),image_file1=image_file1, image_file2=image_file2, form=form, data1=data1, data2=data2, data3=data3, data4=data4, t=t)






@app.route("/livesearch",methods=["POST","GET"])
def livesearch():
    searchbox = request.form.get("text")
    cursor = mysql.connection.cursor()
    query = "SELECT name1 FROM reciepes WHERE name1 LIKE '{}%' ORDER BY name1".format(searchbox)
    cursor.execute(query)
    result = cursor.fetchall()
	
    return jsonify(result)


@app.route('/saved', methods=['GET','POST'])
@login_required
def saved():
	form = PostForm2()
	return render_template('saved.html', title='Dishes', form=form)
	