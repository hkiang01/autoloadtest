import os

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/ping")
def ping():
    return {}


class Item(BaseModel):
    item_id: int
    q: str = None
    r: str = None


@app.post("/items/{item_id}", response_model=Item)
def read_item(item_id: int, q: str = None, r: str = None):
    return Item(**{"item_id": item_id, "q": q, "r": r})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=os.environ["PORT"])
