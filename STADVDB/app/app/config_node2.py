class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345@127.0.0.1:3309/steamGames"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
    'node2': 'mysql+pymysql://root:12345@127.0.0.1:3309/steamGames'  
    }
