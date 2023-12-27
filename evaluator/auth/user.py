import os
import time

from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory

from ..models import User
from evaluator import db, app


user = Blueprint("user",__name__)

@user.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        
        # Query user based on username.
        user = User.query.filter_by(u_name=username).first()
        
        if user is None or user.u_password != password:
            return render_template("login.html", res=False)
        else:
            return redirect(url_for("user.profile", id=user.u_id))
    
    return render_template("login.html")

@user.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        
        res = {}
        if not all([username, password1, password2]):
            res["code"] = 1
            res["message"] = "Username or password is empty."
        elif password1 != password2:
            res["code"] = 2
            res["message"] = "The passwords entered twice are inconsistent."
        else:
            user = User.query.filter_by(u_name=username).first()
            # The username has been registered
            if user is not None:
                res["code"] = 3
                res["message"] = "Username has been registered."
            else:
                res["code"] = 0
                res["message"] = "Success."
                
                # Create a new user
                new_user = User(u_name=username, u_password=password1)
                db.session.add(new_user)
                db.session.commit()
                return redirect(url_for("user.login"))
        
        # Failed to create user
        return render_template("register.html", res=res)
    
    return render_template("register.html")


@user.route("/uploads", methods=["GET"])
def uploads_file():
    filename = request.args.get("filename")
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

@user.route("/profile", methods=["GET","POST"])
def profile():
    if request.method == "POST":
        u_id = request.form["id"]
        u_name = request.form["username"]
        u_email = request.form["email"]
        old_password = request.form.get("old_password", None)
        new_password = request.form.get("new_password", None)
        
        user = User.query.filter_by(u_id=u_id).first()
        
        user_info = {
            "id": user.u_id,
            "username": user.u_name,
            "email": user.u_email,
            "pic_path": user.u_pic_path,
        }
        
        is_error = False
        
        res = {
            "code": 0,
            "message": "SUCCESS",
        }
        
        is_error = []
        if u_name != user.u_name:
            if User.query.filter_by(u_name=u_name).first():  # The password is non-empty and has not been used.
                is_error.append(True)
                res["code"] = 1
                res["message"] = "The username has been used."
            else:
                is_error.append(False)
                user.u_name = u_name
        
        if u_email != user.u_email:
            if User.query.filter_by(u_email=u_email).first():  # The username is non-empty and has not been used.
                is_error.append(True)
                res["code"] = 2
                res["message"] = "The email has been used."
            else:
                is_error.append(False)
                user.u_email = u_email
        
        if new_password:
            if old_password != user.u_password:
                is_error.append(True)
                res["code"] = 3
                res["message"] = "Old password error."
            elif (
                len(new_password) >= 15  # Password must contain at least 15 characters
                or (  # Or at least 8 characters including a number and a lowercase letter.
                    len(new_password) >= 8
                    and any(c.isdigit() for c in new_password)
                    and any(c.islower() for c in new_password)
                    )):
                is_error.append(False)
                user.u_password = new_password
            else:
                is_error.append(True)
                res["code"] = 4
                res["message"] = "Password do not complie with the specifications."
        
        # Update will not proceed if any of the above conditions is not met.
        if not any(is_error):
            db.session.commit()
            user_info["username"] = user.u_name
            user_info["email"] = user.u_email
        else:
            db.session.rollback()
        return render_template("your_profile.html", user=user_info, res=res)
    
    u_id = request.args.get("id")
    user = User.query.filter_by(u_id=u_id).first()
    user = {
        "id": user.u_id,
        "username": user.u_name,
        "email": user.u_email,
        "pic_path": user.u_pic_path,
    }
    return render_template("your_profile.html", user=user)

@user.route("/profile/img", methods=["POST"])
def upload_img():
    img = request.files.get("image")
    suffix = img.filename.split(".")[-1]
    upload_dir = os.path.join(f"evaluator", app.config["UPLOAD_FOLDER"])
    base_dir = os.path.join(upload_dir, "profile_pics")
    img_path = os.path.join(base_dir, f"{str(int(time.time()))}.{suffix}")
    img.save(img_path)
    
    u_id = request.form["id"]
    if os.path.exists(img_path):
        user = User.query.filter_by(u_id=u_id).first()
        
        # Extract the file extension of an image.
        new_img_path = os.path.join(base_dir, f"{user.u_id}.{suffix}")
        
        # If it is the default path (u_pic_path is default), rename the image with the u_id.
        if user.u_pic_path != "profile_pics/icon_black.png":
            os.remove(os.path.join(upload_dir, user.u_pic_path))
        
        os.rename(img_path, new_img_path)
        user.u_pic_path = os.path.join("profile_pics/", f"{user.u_id}.{suffix}")
        db.session.commit()
    return user.u_pic_path