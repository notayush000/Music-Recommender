from flask import render_template, url_for, request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, current_user, login_required

from musicf import app, db
from musicf.models import User
from musicf.api import Spotify

import validators
import secrets
import os


def validate_email_username(email: str, username: str) -> list:
    userExists = User.query.filter_by(username=username).first()
    if userExists:
        return [False, "Username already in use", "danger"]
    emailExists = User.query.filter_by(email=email).first()
    if emailExists:
        return [False, "Email already in use", "danger"]
    return [True]


def check_if_corrupt(email: str, username: str, password: str) -> list:
    if len(username) < 3:
        return [False, "Username too short", "danger"]
    if not validators.email(email):
        return [False, "Invalid email address", "danger"]
    if len(password) < 4:
        return [False, "Password length must be 4 or more", "danger"]
    return [True]
    

def check_update_details(email: str = None, username: str = None) -> list:
    if username:
        userEx = User.query.filter_by(username=username).first()
        if not userEx and username != current_user.username:
            return [True]
        else:
            return [False, "Username entered is same / already in use", "danger"]
    if email:
        emailEx = User.query.filter_by(email=email).first()
        if not emailEx and email != current_user.email:
            return [True]
        else:
            return [False, "Email entered is same / already in use", "danger"]
    return [True]


def save_picture(picture_data) -> str:
    random_hex = secrets.token_hex(8)
    _, p_ext = os.path.splitext(picture_data.filename)
    new_filename = random_hex + p_ext
    picture_path = os.path.join(app.root_path, "static/profile_pics", new_filename)
    picture_data.save(picture_path)
    return new_filename
    
spotify = Spotify()


@app.route("/", methods=['GET', 'POST'])
def landing():
    if current_user.is_authenticated:
        return redirect(url_for("home")) 
    return render_template("landing.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        remember = request.form.get("userRemember")
        username = request.form.get("userEmailUsername")
        password = request.form.get("userPassword")
        
        user = User.query.filter_by(username=username).first()
        if not user:
            user = User.query.filter_by(email=username).first()
            if not user:
                flash("Login Unsuccessful. Please check email and password", "danger")
                return redirect(url_for("login"))
        if not check_password_hash(user.password, password):
            flash("Login Unsuccessful. Please check email and password", "danger")
            return redirect(url_for("login"))

        login_user(user, remember=True if remember is not None else False)
        flash("Logged in!!!", "success")
        next_page = request.args.get("next")
        return redirect(next_page) if next_page else redirect(url_for("home"))
    
    return render_template("login.html")


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    
    if request.method == "POST":
        username = request.form.get("userUsername")
        email = request.form.get("userEmail")
        password = request.form.get("userPassword")
        passwordRepeat = request.form.get("userRepeatPassword")
        
        validationOne = validate_email_username(email, username)
        validationTwo = check_if_corrupt(email, username, password)
        
        if password != passwordRepeat:
            flash("Password's doesn't match!", "danger")
        elif not validationOne[0]:
            flash(validationOne[1], validationOne[2])
        elif not validationTwo[0]:
            flash(validationTwo[1], validationTwo[2])
        else:
            user = User(username=username,
                        email=email,
                        password=generate_password_hash(password, method="sha256")) 
            db.session.add(user)
            db.session.commit()
            flash(f"User created with username {username}, login to continue!", "success")
            return redirect(url_for("login"))
        return redirect(url_for("register"))
        
    return render_template("register.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "success")
    return redirect(url_for("landing"))


@app.route("/home")
@login_required
def home():
    if not spotify.is_authenticated():
        return redirect(spotify.get_oauth2_url())

    if spotify.is_token_expired():
        auth_code: None = request.args.get("code")
        if auth_code:
            spotify.get_or_refresh_access_token("GET", auth_code)
        else:
            spotify.get_or_refresh_access_token("refresh")
            
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_pic)
    return render_template("home.html", user=current_user, img=image_file)

@app.route("/settings")
@login_required
def settings():
    return render_template("settings.html")

@app.route("/profile", methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == "POST":
        img_data = request.files.get("profile")
        new_username = request.form.get("username")
        new_email = request.form.get("email")
        
        if img_data:
            img_name = save_picture(img_data)
            current_user.profile_pic = img_name
            db.session.commit()
            flash("Your account has been updated!", "success")
        
        if new_username:
            validation = check_update_details(username=new_username)
            if not validation[0]:
                flash(validation[1], validation[2])
            else:
                current_user.username = new_username
                db.session.commit()
                flash("Your account has been updated!", "success") if not img_data else None
                
        if new_email:
            validation = check_update_details(email=new_email)
            if not validation[0]:
                flash(validation[1], validation[2])
            else:
                current_user.email = new_email
                db.session.commit()
                flash("Your account has been updated!", "success") if not img_data and new_username else None
                
        return redirect(url_for('profile'))
        
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_pic)
    return render_template("account.html", 
                           user=current_user, 
                           img=image_file,
                           date_time=current_user.date_created)
    
@app.route("/play") 
@login_required
def play_music():
    if spotify.is_token_expired():
        auth_code = request.args.get("code")
        if auth_code:
            spotify.get_or_refresh_access_token("GET", auth_code)
        else:
            try:
                spotify.get_or_refresh_access_token("refresh")
            except:
                return redirect(spotify.get_oauth2_url())
     
    data = {
        "name": spotify.player_details['current']['name'],
        "artists": spotify.player_details['current']['artists'],
        "img": spotify.player_details['current']['img'],
        "uri": spotify.player_details['current']['uri'],
        "duration": spotify.player_details['current']['duration']
    }
    image_file = url_for('static', filename='profile_pics/' + current_user.profile_pic)
    return render_template("play.html", 
                           user=current_user, 
                           img=image_file,
                           data=data)