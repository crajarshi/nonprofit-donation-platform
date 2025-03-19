# Import all the models, so that Base has them before being
# imported by Alembic
from app.database.base_class import Base  # noqa
from app.models.user import User  # noqa
from app.models.npo import NPO  # noqa
from app.models.donation import Donation  # noqa
from app.models.campaign import Campaign  # noqa
from app.models.token import Token  # noqa 