from sqlmodel import Session, select
import typer
from app.db.database import engine
from app.models.role import Role
from app.models.permission import Permission
from app.models.user import User
from app.models.data_source import DataSource
from app.models.kibana_source import KibanaSource
from app.models.grafana_source import GrafanaSource
from app.models.role_has_permissions import RoleHasPermissions
from app.core.hashing import hash_password

app = typer.Typer()

def seed_db():
    with Session(engine) as session:

        # Seed permissions
        permissions = [
            {"name": "create_user"},
            {"name": "read_user"},
            {"name": "update_user"},
            {"name": "delete_user"},
            {"name": "read_role"},
            {"name": "create_role"},
            {"name": "delete_role"},
            {"name": "rename_role"},
            {"name": "assign_permissions"},
            {"name": "remove_permissions"},
            {"name": "read_permission"},
            {"name": "create_data_source"},
            {"name": "read_data_source"},
            {"name": "update_data_source"},
            {"name": "delete_data_source"},
            {"name": "create_kibana_source"},
            {"name": "read_kibana_source"},
            {"name": "update_kibana_source"},
            {"name": "delete_kibana_source"},
            {"name": "create_grafana_source"},
            {"name": "read_grafana_source"},
            {"name": "update_grafana_source"},
            {"name": "delete_grafana_source"},
        ]

        for perm_data in permissions:
            existing_perm = session.exec(
                select(Permission).where(Permission.name == perm_data["name"])
            ).first()
            if not existing_perm:
                new_perm = Permission(**perm_data)
                session.add(new_perm)

        session.commit()

        # Fetch permissions for role assignment
        perm = {}
        perm_list = list(session.exec(select(Permission)).all())
        for p in perm_list:
            perm[f"{p.name}"] = session.exec(
                select(Permission).where(Permission.name == p.name)
                ).first()


        # Seed roles
        roles = [
            {
                "name": "admin",
                "permissions": [perm[p["name"]] for p in permissions],
            },
            {
                "name": "editor",
                "permissions": [],
            },
        ]

        for role_data in roles:
            existing_role = session.exec(
                select(Role).where(Role.name == role_data["name"])
            ).first()
            if existing_role:
                # Add missing permissions to existing roles
                for permission in role_data["permissions"]:
                    if permission not in existing_role.permissions:
                        existing_role.permissions.append(permission)
            else:
                # Create new role if it doesn't exist
                new_role = Role(name=role_data["name"], permissions=role_data["permissions"])
                session.add(new_role)

        session.commit()

        # Fetch admin role for user assignment
        admin_role = session.exec(select(Role).where(Role.name == "admin")).first()

        # Seed admin user
        admin_email = "admin@example.com"
        existing_user = session.exec(select(User).where(User.email == admin_email)).first()
        if not existing_user:
            admin_user = User(
                name="Admin",
                email=admin_email,
                password=hash_password("adminpassword"),
                status="active",
                role=admin_role,
            )
            session.add(admin_user)

        session.commit()

@app.command()
def seed():
    """
    Seed the database with initial data.
    """
    seed_db()
    typer.echo("Database seeded successfully.")

if __name__ == "__main__":
    app()
