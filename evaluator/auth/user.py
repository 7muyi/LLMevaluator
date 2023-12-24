from flask import Blueprint, render_template, request, redirect, url_for

from ..models import User
from evaluator import db


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
            print("true")
            # TODO: Navigate to the admin interface.
            return redirect(url_for())
    
    return render_template("login.html")

@user.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        
        print(username, password1, password2)
        res = {}
        if not all([username, password1, password2]):
            res["code"] = 1
            res["message"] = "Username or password is empty."
        elif password1 != password2:
            res["code"] = 2
            res["message"] = "The passwords entered twice are inconsistent."
        else:
            user = User.query.filter_by(u_name=username).first()
            print(user)
            # The username has been registered
            if user is not None:
                res["code"] = 3
                res["message"] = "Username has been registered."
                print("already")
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