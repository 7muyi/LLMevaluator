import os
from datetime import datetime
import time

from flask import Blueprint, redirect, request, render_template, send_file, url_for, jsonify
import pandas as pd

from ..models import Prompt, User
from evaluator import db, app


prompt = Blueprint("prompt", __name__)

@prompt.route("/list",methods=["GET"])
def prompt_list():
    u_id = request.args.get("u_id")
    user = User.query.get(u_id)
    prompts = Prompt.query.filter_by(u_id=u_id).all()
    prompt_list = []
    for prompt in prompts:
        prompt_list.append({
            "p_id": prompt.p_id,
            "name": prompt.p_name,
            "num of row": prompt.p_num_row,
            "creation time": prompt.p_create_time.strftime("%I:%M %p %b %d"),
        })
    user = {
        "u_id": user.u_id,
        "u_name": user.u_name,
        "u_pic_path": user.u_pic_path,
    }
    return render_template("prompt.html", prompts=prompt_list, user=user)

@prompt.route("/download", methods=["GET"])
def download():
    file_path = request.args.get("filename")
    filename = os.path.basename(file_path)
    return send_file(os.path.join(app.config["STATIC_FOLDER"], file_path), as_attachment=True, download_name=filename)

@prompt.route("/upload", methods=["POST"])
def upload():
    u_id = request.form["u_id"]
    filename = request.form["filename"]
    file = request.files.get("file")
    
    unique_file_name = f"{u_id}_{str(int(time.time()))}.csv"
    file_path = os.path.join(app.config["RUN_DIR"], app.config["PROMPT_FOLDER"], unique_file_name)
    file.save(file_path)
    
    # Download successfully
    if os.path.exists(file_path):
        # *:Try different encoding types.
        encodings = ["utf-8", "gbk", "iso-8859-1"]
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, nrows=10000, encoding=encoding)
            except UnicodeDecodeError:
                continue
        
        row_count = df.shape[0]  # Get the number of data records.
        del df  # *:Release memory.
        
        new_prompt = Prompt(
            p_name=filename,
            p_file_path=unique_file_name,
            p_num_row=row_count,
            u_id=u_id,
        )
        db.session.add(new_prompt)
        db.session.commit()
    
    # *:Ajax is an asynchronous request. Redirect needs to be handled in JavaScript. Here, provide the redirected URL.
    return jsonify(redirect_url=url_for(endpoint="prompt.prompt_list", u_id=u_id))

@prompt.route("/delete", methods=["POST"])
def delete():
    p_id = request.form["p_id"]
    u_id = request.form["u_id"]
    prompt = Prompt.query.get(p_id)

    if prompt:
        file_path = os.path.join(app.config["RUN_DIR"], app.config["PROMPT_FOLDER"], prompt.p_file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            db.session.delete(prompt)
            db.session.commit()
    return redirect(url_for("prompt.prompt_list", u_id=u_id))

@prompt.route("/edit", methods=["POST"])
def edit():
    p_id = request.form["p_id"]
    u_id = request.form["u_id"]
    p_name = request.form["p_name"]
    prompt = Prompt.query.get(p_id)
    if prompt:
        prompt.p_name = p_name
        db.session.commit()
    return redirect(url_for("prompt.prompt_list", u_id=u_id))