"""Customer reponse models"""


from typing import Optional

from pydantic import BaseModel


class SuccessResponse(BaseModel):
    """Used for sending a simple 200 success"""

    detail: Optional[str]
