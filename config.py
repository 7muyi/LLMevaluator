class Config():
    # General configyration
    STATIC_FOLDER = "static/"
    DEBUG = True
    
    # MySQL configuration
    USERNAME = "root"
    PASSWORD = "yangkang"
    HOSTNAME = "127.0.0.1"  # Database and program are on the same server.
    PORT = 3306
    DATABASE = "LLMevaluator"
    
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{}:{}@{}:{}/{}".format(USERNAME, PASSWORD, HOSTNAME, PORT, DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevConfig(Config):
    DEBUG = True
    HOSTNAME = "127.0.0.1"


class ProConfig(Config):
    DEBUG = False
    HOSTNAME = "127.0.0.1"


configs = {
    "development": DevConfig,
    "production": ProConfig,
    "default": Config,
}