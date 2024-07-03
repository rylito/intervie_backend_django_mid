
from decimal import Decimal
from pydantic import BaseModel

# Needed for Python 3.8.19
from typing import List


class InventoryMetaData(BaseModel):
    year: int
    actors: List[str]
    imdb_rating: Decimal
    rotten_tomatoes_rating: int
