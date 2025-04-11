from pydantic import BaseModel
from typing import List


class AssignPermissionsRequest(BaseModel):
    permission_ids: List[int]
