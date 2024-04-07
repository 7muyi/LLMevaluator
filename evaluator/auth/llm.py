from datetime import datetime

from flask import (Blueprint, jsonify, redirect, render_template, request,
                   url_for)

from evaluator import db

from ..models import LLM, User

llm = Blueprint("llm", __name__)

@llm.route("/list",methods=["GET"])
def llm_list():
    u_id = request.args.get("u_id")
    user = User.query.get(u_id)
    llm_brief_desc = ["name", "url", "creation time"]
    llm_list = []
    for llm in user.llms:
        llm_list.append({
            "l_id": llm.l_id,
            "name": llm.l_name,
            "url": llm.l_url,
            "access_token": llm.l_access_token,
            "return_format": llm.l_return_format,
            "creation time": llm.l_create_time.strftime("%I:%M %p %b %d"),
        })
    if u_id != 1:
        # *:All users share Admin's files.
        admin = User.query.get(1)
        for llm in admin.llms:
            llm_list.append({
                "l_id": llm.l_id,
                "name": llm.l_name,
                "url": llm.l_url,
                "access_token": llm.l_access_token,
                "return_format": llm.l_return_format,
                "creation time": llm.l_create_time.strftime("%I:%M %p %b %d"),
            })
    user = {
        "u_id": user.u_id,
        "u_name": user.u_name,
        "u_pic_path": user.u_pic_path,
    }
    return render_template("llm.html", llms=llm_list, llm_brief_desc=llm_brief_desc, user=user)

@llm.route("/add_llm", methods=["POST"])
def add_llm():
    u_id = request.form["u_id"]
    l_name = request.form["l_name"]
    l_url = request.form["l_url"]
    l_return_format = request.form["l_return_format"]
    l_access_token = request.form["l_access_token"]

    res = {
        "code": 0,
        "message": "SUCCESS",
        "redirect_url": None,
    }
    if all([l_name, l_url, l_return_format]):
        new_llm = LLM(
            l_name=l_name,
            l_url=l_url,
            l_return_format=l_return_format,
            l_access_token=l_access_token,
            u_id=u_id,
        )
        db.session.add(new_llm)
        db.session.commit()
        res["redirect_url"] = url_for(endpoint="llm.llm_list", u_id=u_id)
    else:
        res["code"] = 1
        res["message"] = "Name, URL, Return format are not allowed to be empty."
    # *:Ajax is an asynchronous request. Redirect needs to be handled in JavaScript. Here, provide the redirected URL.
    return jsonify(res)

@llm.route("/delete", methods=["POST"])
def delete():
    l_id = request.form["l_id"]
    u_id = request.form["u_id"]
    llm = LLM.query.get(l_id)

    if llm:
        db.session.delete(llm)
        db.session.commit()
    return redirect(url_for("llm.llm_list", u_id=u_id))

@llm.route("/edit", methods=["POST"])
def edit():
    l_id = request.form["l_id"]
    u_id = request.form["u_id"]
    l_name = request.form["l_name"]
    l_url = request.form["l_url"]
    l_return_format = request.form["l_return_format"]
    l_access_token = request.form["l_access_token"]

    llm = LLM.query.get(l_id)
    if llm:
        llm.l_name = l_name if l_name else llm.l_name
        llm.l_url = l_url if l_url else llm.l_url
        llm.l_return_format = l_return_format if l_return_format else llm.l_return_format
        llm.l_access_token = l_access_token if l_access_token else llm.l_access_token

        db.session.commit()
    return redirect(url_for("llm.llm_list", u_id=u_id))

@llm.route("/brief_desc_list", methods=["GET"])
def brief_desc_list():
    u_id = request.args.get("u_id")
    user = User.query.get(u_id)
    admin = User.query.get(1)
    llm_list = []
    for llm in admin.llms:
        llm_list.append({
            "l_id": llm.l_id,
            "l_name": llm.l_name,
        })
    for llm in user.llms:
        llm_list.append({
            "l_id": llm.l_id,
            "l_name": llm.l_name,
        })
    return jsonify({"llms": llm_list})