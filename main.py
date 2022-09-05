from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src import importer

from typing import Union

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}

