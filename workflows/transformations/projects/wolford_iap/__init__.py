import sys
import os
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(sys.path[0]))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.projects.settings_wolford_iap.project")

from workflows.generic.database_utils import db_connect

# Database source engine (raw data from wolford)
engine_source = db_connect(connection_name='retailisation')
Session_source = sessionmaker(bind=engine_source)

engine_target = db_connect()
Session_target = sessionmaker(bind=engine_target)
