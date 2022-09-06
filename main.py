from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src import importer, schema
from fastapi.openapi.utils import get_openapi

data = dict()


def main():
    global data
    # files = importer.fetch_files("data")
    # data = importer.parse_files(files)
    # importer.add_temperature_data(data, "data")


main()

app = FastAPI()
# origins = ["*"]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title="Custom title",
#         version="2.5.0",
#         description="This is a very custom OpenAPI schema",
#         routes=app.routes,
#     )
#     openapi_schema["info"]["x-logo"] = {
#         "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
#     }
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/buildings")
def read_buildings():
    return {"buildings": [b.name for k, b in data.items()]}

@app.get("/buildings/{building}/sensors")
def read_building_sensors(building: str):
    return {"sensors": [{"type": s.type, "desc": s.desc, "unit": s.unit} for s in data[building].sensors]}

@app.get("/buildings/{building}/sensor/{sensor}")
def read_building_sensor(building: str, sensor: str):
    return {"sensor": [e for e in data[building].dataframe[sensor]]}

@app.get("/buildings/{building}/timestamps")
def read_building_timestamps(building: str):
    return {"timestamps": [e for e in data[building].dataframe.index]}


schema.custom_openapi(app)
