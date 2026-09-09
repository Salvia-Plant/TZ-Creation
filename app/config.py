import os

class AppConfig:
 DB_USER = os.getenv("DB_USER", "postgres")
 DB_PASSWORD = os.getenv("DB_PASSWORD", "")  # засекретили пароль, он в дотенв, который в гитигноре
 #DB_SERVER = 'ksue-db.service.consul:5432'
 DB_SERVER = os.getenv("DB_SERVER", "127.0.0.1:5432")
 DB_NAME = os.getenv("DB_NAME", "flask_db")
 MAX_CONTENT_LENGTH = 50 * 1000 * 1000
 #PARSER_ADDRESS = 'panda-back.service.consul:8765'
 PARSER_ADDRESS = '192.168.74.68:8765'
 SQLALCHEMY_TRACK_MODIFICATIONS = False
 DAFD_ADDRESS = "192.168.74.63:9005"
 ATTESTATION_ADDRESS = "192.168.74.71:9037"
 TEMPLATE_ID = 'asd8hyH9-56gd-87gy-a5dv-56747gdhcn8h'

 @property
 def SQLALCHEMY_DATABASE_URI(self):
   return  'postgresql+psycopg2://{user}:{password}@{address}/{db}'.format(
      user=self.DB_USER, password=self.DB_PASSWORD, address=self.DB_SERVER, db=self.DB_NAME)