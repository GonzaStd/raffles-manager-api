from sqlalchemy import create_engine
from config.database import setup_mysql
if setup_mysql():
    sys_engine = create_engine("mysql+pymysql://raffles-manager:raffles@localhost")