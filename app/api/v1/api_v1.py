# app/api/v1/api_v1.py

from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    roles,
    permissions,
    data_sources,
    kibana_sources,
    grafana_sources,
    role_has_permissions,
    logout
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(logout.router, prefix="/logout", tags=["logout"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(permissions.router, prefix="/permissions", tags=["permissions"])
api_router.include_router(roles.router, prefix="/roles", tags=["roles"])
api_router.include_router(role_has_permissions.router, prefix="/role-has-permissions", tags=["role_has_permissions"])
api_router.include_router(data_sources.router, prefix="/data-sources", tags=["data_sources"])
api_router.include_router(grafana_sources.router, prefix="/grafana-sources", tags=["grafana_sources"])
api_router.include_router(kibana_sources.router, prefix="/kibana-sources", tags=["kibana_sources"])
