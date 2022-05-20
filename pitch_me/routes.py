import os
import secrets
from PIL import Image
from flask import render_template, url_for ,flash , redirect, request, abort
from pitch_me import app, db ,bcrypt
from pitch_me.forms import RegForm, LoginForm, UpdateAccountForm, PitchForm
from pitch_me.models import User, Pitch
from flask_login import login_user, current_user, logout_user, login_required



@app.route('/')
@app.route('/home')
def home():
    pitch = Pitch.query.all()
    return render_template('home.html',pitch=pitch)

@app.route('/about')
def about():
    
    return render_template('about.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return render_template(url_for('home'))
    form = RegForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data,email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your Account has been successfully created! You are now able to login','success')
        return redirect(url_for('login')) 
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user =User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
           login_user(user, remember=form.remember.data)
           next_page = request.args.get('next')
           return redirect(next_page)if next_page else redirect(url_for('home'))
        else:
            flash('login Unsuccessful. please check out your email and password')
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _,f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/photos', picture_fn)
    
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)  
    
    return picture_fn 
    

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm() 
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit
        flash('Your Account has been updated',)
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static',filename='photos/' + current_user.image_file )
    return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new",methods=['GET', 'POST'])
@login_required
def new_post():
    form = PitchForm()
    if form.validate_on_submit():
        pitch = Pitch(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(pitch)
        db.session.commit()
        flash('Your Pitch has been created!','success')
        return redirect(url_for('home'))
    return render_template('create_pitch.html',title='New Pitch', form=form ,legend='New Pitch')

@app.route("/pitch/<int:pitch_id>")
def pitch(pitch_id):
    pitch = Pitch.query.get_or_404(pitch_id)
    return render_template('pitch.html' , title=pitch.title, pitch=pitch)

@app.route("/pitch/<int:pitch_id>/update", methods= ['GET', 'POST'])
@login_required
def update_pitch(pitch_id):
    pitch = Pitch.query.get_or_404(pitch_id)
    if pitch.author != current_user:
        abort(403)
    form = PitchForm()
    if form.validate_on_submit():
        pitch.title = form.title.data
        pitch.content = form.content.data
        db.session.commit()
        flash('Your pitch has been updated', 'danger')
        return redirect(url_for('pitch', pitch_id=pitch.id))
    elif request.method == 'GET':  
        form.title.data = pitch.title
        form.content.data = pitch.content
    return render_template('create_pitch.html', title='Update Pitch', form=form, legend='Update Pitch')

@app.route("/pitch/<int:pitch_id>/delete", methods= ['POST'])
@login_required
def delete_pitch(pitch_id):
    pitch = Pitch.query.get_or_404(pitch_id)
    if pitch.author != current_user:
        abort(403)
    db.session.delete(pitch)
    db.session.commit()
    flash('pitch has been deleted', 'success')
    return redirect(url_for('home'))
    
    