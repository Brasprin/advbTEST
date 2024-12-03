class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:12345@127.0.0.1:3308/steamGames"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
    'node1': 'mysql+pymysql://root:12345@127.0.0.1:3308/steamGames'  
    }
