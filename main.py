from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src import importer

data = dict()


def main():
    global data
    files = importer.fetch_files("data")
    data = importer.parse_files(files)
    importer.add_temperature_data(data, "data")


main()

app = FastAPI()
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/buildings")
def read_buildings():
    return {"buildings": [b.name for k, b in data.items()]}
