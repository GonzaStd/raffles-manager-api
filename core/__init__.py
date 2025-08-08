from sqlalchemy import create_engine
from core.database import setup_mysql
from core.config_loader import settings

# Remove immediate database setup that hangs during import
# Only create the engine definition, don't execute setup
def get_sys_engine():
    if setup_mysql():
        return create_engine(f"mysql+pymysql://{settings.MARIADB_USERNAME}:{settings.MARIADB_PASSWORD}@{settings.MARIADB_SERVER}")
    return None

# Make sys_engine lazy-loaded
sys_engine = None
