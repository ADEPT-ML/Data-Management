from fastapi import FastAPI, Query, HTTPException
from src import importer, schema
import dataclasses
import requests
import pandas
import json
import numpy as np


data = dict()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if dataclasses.is_dataclass(o):
            return dataclasses.asdict(o)
        if isinstance(o, pandas.DataFrame):
            return o.to_json()
        return super().default(o)

def main():
    global data
    files = importer.fetch_files("data")
    data = importer.parse_files(files)
    importer.add_temperature_data(data, "data")
    json_data = requests.post("http://preprocessing/clean", json={"payload": json.dumps(data, cls=JSONEncoder)}).json()
    json_data = requests.post("http://preprocessing/interpolate", json={"payload": json_data}).json()
    json_data = requests.post("http://feature-engineering/diff", json={"payload": json_data}).json()
    json_data = requests.post("http://preprocessing/interpolate", json={"payload": json_data}).json()
    data = importer.json_to_buildings(json.loads(json_data))


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
    description="Returns all buildings available through the building repository.\
        The response includes the buildings names.",
    response_description="List of building names.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "buildings": [
                            "EF 40",
                            "EF 40a"
                        ]
                    }
                }
            },
        }
    },
    tags=["Buildings and Sensors"]
)
def read_buildings():
    try:
        return {"buildings": [b.name for k, b in data.items()]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


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
                        "sensors": [
                            {
                                "type": "Temperatur",
                                "desc": "Wetterstation",
                                "unit": "°C"
                            },
                            {
                                "type": "Wärme Diff",
                                "desc": "Wärmeenergie Tarif 1",
                                "unit": "kWh / 15 min"
                            },
                            {
                                "type": "Wärme.5 Diff",
                                "desc": "Wärmeenergie Tarif 1",
                                "unit": "kWh / 15 min"
                            },
                            {
                                "type": "Elektrizität.1 Diff",
                                "desc": "WV+ Arbeit tariflos",
                                "unit": "kWh / 15 min"
                            },
                            {
                                "type": "Elektrizität.2 Diff",
                                "desc": "WV+ Arbeit Tarif 1",
                                "unit": "kWh / 15 min"
                            }
                        ]
                    }
                }
            },
        },
        404: {
            "description": "Building not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Building not found"}
                }
            },
        },
    },
    tags=["Buildings and Sensors"]
)
def read_building_sensors(building: str):
    try:
        if building not in data:
            raise HTTPException(status_code=404, detail="Building not found")
        return {"sensors": [{"type": s.type, "desc": s.desc, "unit": s.unit} for s in data[building].sensors]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get(
    "/buildings/{building}/slice",
    name="Building Slice",
    summary="Returns a slice of the dataframe for the specified sensors and start & stop times",
    description="Returns a slice of the dataframe for the specified sensors and start & stop times.\
        The response will include a dict of the specified sensors in the specified time slice.",
    response_description="Dict of sensors in time slice.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "payload": {
                            "Electricity.1 Diff": {
                                "2020-07-31T20:00:00": 1.4,
                                "2020-07-31T20:15:00": 1.4,
                                "2020-07-31T20:30:00": 1.3
                            },
                            "Electricity.3 Diff": {
                                "2020-07-31T20:00:00": 1.5,
                                "2020-07-31T20:15:00": 1.6,
                                "2020-07-31T20:30:00": 1.7
                            }
                        }
                    }
                }
            },
        },
        404: {
            "description": "Building not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Building not found"}
                }
            },
        }
    },
    tags=["Buildings and Sensors"]
)
def get_building_data_slice(building: str, start: str, stop: str, sensors: list = Query(None)):
    try:
        if building not in data:
            raise HTTPException(status_code=404, detail="Building not found")
        timestamp_start = np.datetime64(start)
        timestamp_stop = np.datetime64(stop)
        df = data[building].dataframe
        if timestamp_start > df.index[-1] or timestamp_stop < df.index[0]:
            raise HTTPException(status_code=404, detail="Invalid time span")
        if any([s not in [e.type for e in data[building].sensors] for s in sensors]):
            raise HTTPException(status_code=404, detail="Invalid sensor selection")
        df = df.loc[(timestamp_start <= df.index) & (df.index <= timestamp_stop), sensors]
        return {"payload": df.to_dict()}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get(
    "/buildings/{building}/sensors/{sensor}",
    name="Sensor Data",
    summary="Returns the dataframe of a specified sensor",
    description="Returns the dataframe of the specified building and sensor.",
    response_description="Dataframe of the sensor.",
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "sensor": [
                            12.4,
                            12.1,
                            11.8,
                            11.5,
                            11.2
                        ]
                    }
                }
            },
        },
        404: {
            "description": "Building or Sensor not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Building or Sensor not found"}
                }
            },
        }
    },
    tags=["Buildings and Sensors"]
)
def read_building_sensor(building: str, sensor: str):
    try:
        if building not in data:
            raise HTTPException(status_code=404, detail="Building not found")
        if sensor not in [e.type for e in data[building].sensors]:
            raise HTTPException(status_code=404, detail="Sensor not found")
        return {"sensor": [e for e in data[building].dataframe[sensor]]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")

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
                        "timestamps": [
                            "2020-03-14T15:00:00",
                            "2020-03-14T15:15:00",
                            "2020-03-14T15:30:00",
                            "2020-03-14T15:45:00",
                            "2020-03-14T16:00:00",
                            "2020-03-14T16:15:00"
                        ]
                    }
                }
            },
        },
        404: {
            "description": "Building not found.",
            "content": {
                "application/json": {
                    "example": {"detail": "Building not found"}
                }
            },
        },
    },
    tags=["Buildings and Sensors"]
)
def read_building_timestamps(building: str):
    try:
        if building not in data:
            raise HTTPException(status_code=404, detail="Building not found")
        return {"timestamps": [e for e in data[building].dataframe.index]}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Internal Server Error")


schema.custom_openapi(app)

@app.get("/")
async def root():
    url_list = [{"path": route.path, "name": route.name}
                for route in app.routes]
    return url_list