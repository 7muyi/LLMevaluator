from evaluator import app
from .user import user
from .prompt import prompt
from .question import question
from .llms import llms


# register apps
app.register_blueprint(user, url_prefix="/user")
app.register_blueprint(prompt, url_prefix="/prompt")
app.register_blueprint(question, url_prefix="/question")
app.register_blueprint(llms, url_prefix="/llms")