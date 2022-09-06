from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src import importer, schema

data = dict()


def main():
    global data
    files = importer.fetch_files("data")
    data = importer.parse_files(files)
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


@app.get(
    "/buildings", 
    name="Buildings", 
    summary="Returns a list of buildings",
    description="Returns all buildings avalaible through the building repository.\
        The response includes the buildings names.",
    response_description="List of building names.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "TBD": [
                            "96caaf28-TBD-4a9a-8a3f-TBD",
                            "TBD-TBD-TBD-TBD-5cf4676674f4",
                            "da7d5941-TBD-TBD-b63b-TBD",
                        ]
                    }
                }
            },
        }
    },
    tags=["Buildings and Sensors"]
)
def read_buildings():
    return {"buildings": [b.name for k, b in data.items()]}


@app.get(
    "/buildings/{building}/sensors", 
    name="Building Sensors", 
    summary="Returns a list of sensors of a specified building",
    description="Returns all sensors available for the building specified through the parameter.\
        The response will include a list of the sensors with their type, desc and unit.",
    response_description="List of sensors.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "TBD": [
                            "96caaf28-TBD-4a9a-8a3f-TBD",
                            "TBD-TBD-TBD-TBD-5cf4676674f4",
                            "da7d5941-TBD-TBD-b63b-TBD",
                        ]
                    }
                }
            },
        },
        404: {
            "description": "Building not found.",
            "content": {
                "application/json": {
                    "example": {"message": "Building not found"}
                }
            },
        },
    },
    tags=["Buildings and Sensors"]
)
def read_building_sensors(building: str):
    return {"sensors": [{"type": s.type, "desc": s.desc, "unit": s.unit} for s in data[building].sensors]}

@app.get(
    "/buildings/{building}/sensors/{sensor}", 
    name="Sensor Data", 
    summary="Returns the dataframe of a specified sensor",
    description="Returns the dataframe of the sepcified building and sensor.",
    response_description="Dataframe of the sensor.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "TBD": [
                            "96caaf28-TBD-4a9a-8a3f-TBD",
                            "TBD-TBD-TBD-TBD-5cf4676674f4",
                            "da7d5941-TBD-TBD-b63b-TBD",
                        ]
                    }
                }
            },
        },
        404: {
            "description": "Building or Sensor not found.",
            "content": {
                "application/json": {
                    "example": {"message": "Building or Sensor not found"}
                }
            },
        }
    },
    tags=["Buildings and Sensors"]
)
def read_building_sensor(building: str, sensor: str):
    return {"sensor": [e for e in data[building].dataframe[sensor]]}

@app.get(
    "/buildings/{building}/timestamps", 
    name="Building Timeframe", 
    summary="Returns a dataframe of the data-timeframe of a specified building",
    description="Returns timestamps for the specified building.",
    response_description="Dataframe of the time-data.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "TBD": [
                            "96caaf28-TBD-4a9a-8a3f-TBD",
                            "TBD-TBD-TBD-TBD-5cf4676674f4",
                            "da7d5941-TBD-TBD-b63b-TBD",
                        ]
                    }
                }
            },
        },
        404: {
            "description": "Building not found.",
            "content": {
                "application/json": {
                    "example": {"message": "Building not found"}
                }
            },
        },
    },
    tags=["Buildings and Sensors"]
)
def read_building_timestamps(building: str):
    return {"timestamps": [e for e in data[building].dataframe.index]}


schema.custom_openapi(app)

@app.get("/")
async def root():
    url_list = [{"path": route.path, "name": route.name}
                for route in app.routes]
    return url_list