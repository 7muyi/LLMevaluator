from evaluator import db


# User table
class User(db.Model):
    __tablename__ = "user"
    
    u_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    u_name = db.Column(db.String(25), unique=True, nullable=False)
    u_password = db.Column(db.String(30), nullable=False)

# LLMs table
class LLMs(db.Model):
    __tablename__ = "llms"
    
    l_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    l_name = db.Column(db.String(30), nullable=False)
    l_url = db.Column(db.String(100), nullable=False)
    l_return_format = db.Column(db.String(200), nullable=False)
    l_create_time = db.Column(db.DateTime, default=db.func.now())

# Prompt table
class Prompt(db.Model):
    __tablename__ = "prompt"
    
    p_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    p_name = db.Column(db.String(30), nullable=False)
    p_file_path = db.Column(db.String(100), unique=True, nullable=False)
    p_create_time = db.Column(db.DateTime, default=db.func.now())
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"))
    
    user = db.relationship("User", backref=db.backref("prompts", lazy=True))

# Question table
class Question(db.Model):
    __tablename__ = "question"
    
    q_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    q_name = db.Column(db.String(30), nullable=False)
    q_file_path = db.Column(db.String(100), unique=True, nullable=False)
    q_create_time = db.Column(db.DateTime, default=db.func.now())
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"))
    
    user = db.relationship("User", backref=db.backref("questions", lazy=True))

# Test table
class Test(db.Model):
    __tablename__ = "test"
    
    t_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    t_name = db.Column(db.String(30), nullable=False)
    t_create_time = db.Column(db.DateTime, default=db.func.now())
    t_status = db.Column(db.Enum("processing", "finish"), nullable=False, default="processing")
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"))
    p_id = db.Column(db.Integer, db.ForeignKey("prompt.p_id"))
    q_id = db.Column(db.Integer, db.ForeignKey("question.q_id"))
    l_id = db.Column(db.Integer, db.ForeignKey("llms.l_id"))
    
    user = db.relationship("User", backref=db.backref("tests", lazy=True))
    prompt = db.relationship("Prompt", backref=db.backref("tests", lazy=True))
    question = db.relationship("Question", backref=db.backref("tests", lazy=True))
    llms = db.relationship("LLMs", backref=db.backref("tests", lazy=True))


# Report table
class Report(db.Model):
    __tablename__ = "report"
    
    r_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    r_name = db.Column(db.String(30), nullable=False)
    r_file_path = db.Column(db.String(100), unique=True, nullable=False)
    r_create_time = db.Column(db.DateTime, default=db.func.now())
    u_id = db.Column(db.Integer, db.ForeignKey("user.u_id"))
    
    user = db.relationship("User", backref=db.backref("reports", lazy=True))