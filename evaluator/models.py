from sqlalchemy import Nullable
from evaluator import db


# User table
class User(db.Model):
    __tablename__ = "user"
    
    u_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_name = db.Column(db.String(25), unique=True, nullable=False)
    u_password = db.Column(db.String(30), nullable=False)
    u_email = db.Column(db.String(50), unique=True)
    u_pic_path = db.Column(db.String(50), default="defalut_pic.png")

# LLMs table
class LLM(db.Model):
    __tablename__ = "llm"
    
    l_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    l_name = db.Column(db.String(30), nullable=False)
    l_url = db.Column(db.String(100), nullable=False)
    l_access_token = db.Column(db.String(255))
    l_return_format = db.Column(db.String(200), nullable=False)
    l_create_time = db.Column(db.DateTime, default=db.func.now())
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"))
    
    user = db.relationship("User", backref=db.backref("llms", lazy=True))

# Prompt table
class Prompt(db.Model):
    __tablename__ = "prompt"
    
    p_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_name = db.Column(db.String(30), nullable=False)
    p_file_path = db.Column(db.String(100), unique=True, nullable=False)
    p_create_time = db.Column(db.DateTime, default=db.func.now())
    p_num_row = db.Column(db.Integer)
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"))
    
    user = db.relationship("User", backref=db.backref("prompts", lazy=True))

# Question table
class Question(db.Model):
    __tablename__ = "question"
    
    q_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    q_name = db.Column(db.String(30), nullable=False)
    q_file_path = db.Column(db.String(100), unique=True, nullable=False)
    q_create_time = db.Column(db.DateTime, default=db.func.now())
    q_num_row = db.Column(db.Integer)
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"))
    
    user = db.relationship("User", backref=db.backref("questions", lazy=True))

# Test table
class Test(db.Model):
    __tablename__ = "test"
    
    t_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_name = db.Column(db.String(30), nullable=False)
    t_create_time = db.Column(db.DateTime, default=db.func.now())
    t_status = db.Column(db.Enum("processing", "finish","error"), nullable=False, default="processing")
    t_result_file = db.Column(db.String(64))
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"))
    p_id = db.Column(db.Integer, db.ForeignKey("prompt.p_id"))
    q_id = db.Column(db.Integer, db.ForeignKey("question.q_id"))
    l_id = db.Column(db.Integer, db.ForeignKey("llm.l_id"))
    
    user = db.relationship("User", backref=db.backref("tests", lazy=True))
    prompt = db.relationship("Prompt", backref=db.backref("tests", lazy=True))
    question = db.relationship("Question", backref=db.backref("tests", lazy=True))
    llm = db.relationship("LLM", backref=db.backref("tests", lazy=True))


# Report table
# class Report(db.Model):
#     __tablename__ = "report"
    
#     r_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     r_file_path = db.Column(db.String(100), unique=True, nullable=False)
#     r_create_time = db.Column(db.DateTime, default=db.func.now())
#     # r_attack = db.Column(db.Integer)
#     # r_success = db.Column(db.Integer)
#     t_id = db.Column(db.Integer, db.ForeignKey("test.t_id"))
#     # *:Set to cascade update.
#     test = db.relationship("Test", backref=db.backref("reports", lazy=True, cascade="all, delete-orphan"))