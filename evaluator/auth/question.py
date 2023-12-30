import os
from datetime import datetime
import time

import pandas as pd
from flask import Blueprint, redirect, request, render_template, send_file, url_for, jsonify

from ..models import Question, User
from evaluator import db, app

question = Blueprint("question", __name__)

@question.route("/list",methods=["GET"])
def question_list():
    u_id = request.args.get("u_id")
    user = User.query.get(u_id)
    questions = Question.query.filter_by(u_id=u_id).all()
    question_list = []
    for question in questions:
        question_list.append({
            "q_id": question.q_id,
            "name": question.q_name,
            "num of row": question.q_num_row,
            "creation time": question.q_create_time.strftime("%I:%M %p %b %d"),
        })
    user = {
        "u_id": user.u_id,
        "u_name": user.u_name,
        "u_pic_path": user.u_pic_path,
    }
    return render_template("question.html", questions=question_list, user=user)

@question.route("/download", methods=["GET"])
def download():
    file_path = request.args.get("filename")
    filename = os.path.basename(file_path)
    return send_file(os.path.join(app.config["STATIC_FOLDER"], file_path), as_attachment=True, download_name=filename)

@question.route("/upload", methods=["POST"])
def upload():
    u_id = request.form["u_id"]
    filename = request.form["filename"]
    file = request.files.get("file")
    
    unique_file_name = f"{u_id}_{str(int(time.time()))}.csv"
    file_path = os.path.join(app.config["RUN_DIR"], app.config["QUESTION_FOLDER"], unique_file_name)
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

        new_question = Question(
            q_name=filename,
            q_file_path=unique_file_name,
            q_num_row=row_count,
            u_id=u_id,
        )
        db.session.add(new_question)
        db.session.commit()
    
    # *:Ajax is an asynchronous request. Redirect needs to be handled in JavaScript. Here, provide the redirected URL.
    return jsonify(redirect_url=url_for(endpoint="question.question_list", u_id=u_id))

@question.route("/delete", methods=["POST"])
def delete():
    q_id = request.form["q_id"]
    u_id = request.form["u_id"]
    question = Question.query.get(q_id)
    
    if question:
        file_path = os.path.join(app.config["RUN_DIR"], app.config["QUESTION_FOLDER"], question.q_file_path)
        if os.path.exists(file_path):
            os.remove(file_path)
            db.session.delete(question)
            db.session.commit()
    return redirect(url_for("question.question_list", u_id=u_id))

@question.route("/edit", methods=["POST"])
def edit():
    q_id = request.form["q_id"]
    u_id = request.form["u_id"]
    q_name = request.form["q_name"]
    question = Question.query.get(q_id)
    if question:
        question.q_name = q_name
        db.session.commit()
    return redirect(url_for("question.question_list", u_id=u_id))