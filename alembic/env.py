
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.core.config import settings  # Import your Settings

# Ensure all your models are registered with Base's metadata
from app.db.base import Base

# Import all models here to register them with Base.metadata for migration file
from app.models.data_source import DataSource
from app.models.grafana_source import GrafanaSource
from app.models.kibana_source import KibanaSource
from app.models.permission import Permission
from app.models.role_has_permissions import RoleHasPermissions
from app.models.role import Role
from app.models.user import User


# this is the Alembic Config object, which provides access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Retrieve the database URL from your settings
def get_database_url() -> str:
    return settings.SQLALCHEMY_DATABASE_URI

def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    This configures the context with just a URL and not an Engine.
    """
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Optional: Detect changes in column types
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """
    Run migrations in 'online' mode.
    This creates an Engine and associates a connection with the context.
    """
    connectable = engine_from_config(
        {
            'sqlalchemy.url': get_database_url(),
            'sqlalchemy.echo': 'true',  # Enable SQL echoing
        },
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,  # Optional: Detect changes in column types
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
