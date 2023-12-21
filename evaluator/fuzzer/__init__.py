from evaluator import app
from .fuzze_test import fuzzer


# register apps
app.register_blueprint(fuzzer, url_prefix="/fuzzer")