import csv
import json
import os
import threading
from typing import Dict

import pandas as pd
from flask import (Blueprint, config, jsonify, redirect, render_template,
                   request, send_file, url_for)

from evaluator import app, db

from ..models import LLM, Prompt, Question, Test, User
from .fuzzer.fuzzer import Fuzzer
from .fuzzer.llms.llm import LLMFromAPI, OpenAILLM
from .fuzzer.mutator import (CrossOver, Embed, Expand, Generate,
                             MutateRandomSinglePolicy, Rephrase, Shorten)
from .fuzzer.selection import (MCTSExploreSelectPolicy, RandomSelectPolicy,
                               RoundRobinSelectPolicy)
from .fuzzer.utils.predict import LLMPredictor

test = Blueprint("test", __name__)

@test.route("/test_list", methods=["GET"])
def test_list():
    u_id = request.args.get("u_id")
    user = User.query.get(u_id)
    test_brief_desc = ["name", "prompt", "question", "LLM", "creation time"]
    test_list = []
    for test in user.tests:
        test_list.append({
            "t_id": test.t_id,
            "name": test.t_name,
            "creation time": test.t_create_time.strftime("%I:%M %p %b %d"),
            "status": test.t_status,
            "prompt": test.prompt.p_name,
            "question": test.question.q_name,
            "LLM": test.llm.l_name,
        })
    user = {
        "u_id": user.u_id,
        "u_name": user.u_name,
        "u_pic_path": user.u_pic_path,
    }
    return render_template("test.html", tests=test_list, test_brief_desc=test_brief_desc, user=user)

@test.route("/delete", methods=["POST"])
def delete():
    u_id = request.form["u_id"]
    t_id = request.form["t_id"]
    test = Test.query.get(t_id)
    
    if test:
        result_path = os.path.join(app.config["RUN_DIR"], app.config["REPORT_JSON_FOLDER"], test.t_result_file)
        if test.t_status == "finish":
            with open(result_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                file_path = data.get("file_path")
            if os.path.exists(os.path.join(app.config["RUN_DIR"], file_path)):
                os.remove(file_path)
        os.remove(result_path)
        db.session.delete(test)
        db.session.commit()
    return redirect(url_for("test.test_list", u_id=u_id))

@test.route("/detect", methods=["POST"])
def detect():
    u_id = request.form["u_id"]
    t_name = request.form["t_name"]
    l_id = request.form["llm"]
    p_id = request.form["prompt"]
    q_id = request.form["question"]
    select_strategy = request.form["selection_strategy"]
    stop_condition = request.form["stop_condition"]
    num = request.form["num"]
    
    new_test = Test(
        t_name=t_name,
        t_status="processing",
        u_id=u_id,
        p_id=p_id,
        q_id=q_id,
        l_id=l_id,
    )
    
    db.session.add(new_test)
    db.session.commit()
    
    prompt_path = Prompt.query.get(p_id).p_file_path
    question_path = Question.query.get(q_id).q_file_path
    llm = LLM.query.get(l_id)
    thread = threading.Thread(target=fuzzing, kwargs={
        "t_id": new_test.t_id,
        "seed_path": os.path.join(app.config["RUN_DIR"], app.config["PROMPT_FOLDER"], prompt_path),
        "question_path": os.path.join(app.config["RUN_DIR"], app.config["QUESTION_FOLDER"], question_path),
        "number": int(num),
        "tar_model": {
                "name": llm.l_name,
                "url": llm.l_url,
                "return_format": llm.l_return_format,
                "access_token": llm.l_access_token,
            },
        "select_policy": select_strategy,
        "stop_condition": stop_condition,
        "mut_model_name": "gpt-4",
    })
    thread.start()
    
    return redirect(url_for("test.test_list", u_id=u_id))

def fuzzing(t_id, seed_path, question_path, number,
            tar_model, select_policy, stop_condition,
            mut_model_name: str = "gpt-3.5-turbo"):
    if tar_model["name"] == "gpt-3.5-turbo":
        tar_model = OpenAILLM(tar_model["name"], "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")
    else:
        tar_model = LLMFromAPI(
            model_name_or_path=tar_model["name"],
            url=tar_model["url"],
            return_format=tar_model["return_format"],
            access_token=tar_model["access_token"]
        )
    
    model = tar_model
    # *: Openai API expired
    # model = OpenAILLM(mut_model_name, "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")
    
    if select_policy == "Random":
        select = RandomSelectPolicy()
    elif select_policy == "Round robin":
        select = RoundRobinSelectPolicy()
    else:
        select = MCTSExploreSelectPolicy(alpha=0.1, beta=0.2)
    
    if stop_condition == "max-vulnerability":
        max_jailbreak = number
        max_iteration = -1
    else:
        max_jailbreak = -1
        max_iteration = number
    
    predictor = LLMPredictor(model)
    
    initial_seed = []
    
    with open(seed_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        # skip title row
        next(reader)
        
        for row in reader:
            initial_seed.append((row[2], row[1]))
    question_list = []
    
    with open(question_path, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        # skip title row
        next(reader)
        
        for row in reader:
            question_list.append(row[1])
    
    results_file = os.path.join(app.config["RUN_DIR"], app.config["REPORT_CSV_FOLDER"], f"{t_id}.csv")
    results_config = os.path.join(app.config["RUN_DIR"], app.config["REPORT_JSON_FOLDER"], f"{t_id}.json")
    fuzzer = Fuzzer(
        questions=question_list,
        target=tar_model,
        predictor=predictor,
        initial_seed=initial_seed,
        mutate_policy=MutateRandomSinglePolicy(
            [Generate(), Shorten(), Expand(), Rephrase(), CrossOver()],
            model
        ),
        select_policy=select,
        max_jailbreak=max_jailbreak,
        max_iteration=max_iteration,
        result_file=results_file,
        generate_in_batch=False,
    )
    with app.app_context():
        test = Test.query.get(t_id)
        res = {"file_path": os.path.join(app.config["REPORT_CSV_FOLDER"], f"{t_id}.csv")}
        try:
            fuzzer.run()
        except Exception as e:
            test.t_status = "error"
            res["status"] = "error"
            res["error"] = str(e)
        else:
            test.t_status = "finish"
            res["status"] = "success"
        generate_report(results_config, res)
        test.t_result_file = f"{t_id}.json"
        db.session.commit()

@test.route("/report", methods=["GET"])
def report():
    t_id = request.args.get("t_id")
    test = Test.query.get(t_id)
    result_path = os.path.join(app.config["RUN_DIR"], app.config["REPORT_JSON_FOLDER"], test.t_result_file)
    with open(result_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("status") == "error":
        res = {"error": data.get("error")}
    else:  # success
        res = {
            "num_vulnerability": data.get("num_rows"),
            "example": data.get("example")
        }
    return jsonify(res)

@test.route("/download", methods=["GET"])
def download():
    t_id = request.args.get("t_id")
    test = Test.query.get(t_id)
    result_file = os.path.join(app.config["RUN_DIR"], app.config["REPORT_JSON_FOLDER"], test.t_result_file)
    with open(result_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return send_file(data["file_path"], as_attachment=True)

def generate_report(config_path: str, config: Dict[str, str]) -> int:
    """analyze the contents of the file with path file_path.
    
    If the status in config is `success`, the file's line number and other information are analyzed,
    and the final file configuration information is stored in the file with path config_path
    
    Args:
        config_path (str): path of the file storing the result.
        config (str): basic status information of the file.
    
    Return:
        (int): 1 means the file is valid, 0 means the file is invalid.
    """
    file_path = os.path.join(app.config["RUN_DIR"], config["file_path"])
    if config["status"] == "success":
        data = pd.read_csv(file_path)
        num_rows = data.shape[0]
        config["num_rows"] = num_rows,
        config["example"] = {
            "prompt": data.iloc[0, 1],
            "response": data.iloc[0, 2]
        }
        del data  # Free memory
    else:
        os.remove(file_path)
        del config["file_path"]
    
    with open(config_path, "w", newline="", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)