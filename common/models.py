from lib2to3.pytree import Base
#from matplotlib.pyplot import cla
from pydantic import BaseModel

class ErrorMessage(BaseModel):
    """Error msg model."""

    details: str