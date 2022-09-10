import json
import math
import os
from dataclasses import dataclass
import pandas as pd
import numpy as np
import datetime
import time

import xlrd


@dataclass
class Building:
    @dataclass
    class Sensor:
        type: str
        desc: str
        unit: str

    name: str
    sensors: list[Sensor]
    dataframe: pd.DataFrame


def json_to_buildings(data: dict) -> dict:
    buildings = dict()
    for k, b in data.items():
        sensors = [Building.Sensor(s["type"], s["desc"], s["unit"]) for s in b["sensors"]]
        buildings[k] = Building(k, sensors, pd.DataFrame(json.loads(b["dataframe"])))
    return buildings


def fetch_files(directory: str) -> list[str]:
    output_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            basename = os.path.basename(file)
            file_name, file_ext = basename.rsplit(".", 1)
            if file_ext == "xls":
                output_files.append(os.path.join(root, file))
    return output_files


def parse_files(files: list[str]) -> dict[str, Building]:
    output_data = dict()
    start_time = time.time()
    for index, file in enumerate(files):
        file_name = os.path.basename(file).rsplit(".")[0]
        try:
            data = dict()
            wb = xlrd.open_workbook(file, logfile=open(os.devnull, 'w'))
            raw_data = pd.read_excel(wb, engine='xlrd')
            raw_data_keys = raw_data.keys()
            sensors = list()
            for i, key in enumerate(raw_data_keys):
                if i == 0:
                    sensors.append(Building.Sensor("Datetime", "Datetime", "Datetime"))
                else:
                    sensors.append(Building.Sensor(str(key), str(raw_data[key][3]), str(raw_data[key][4])))
                data[sensors[i].type] = raw_data[key][5:][::-1]
            data_types = {sensors[i].type: np.datetime64 if i == 0 else np.float for i in range(len(data))}
            df = pd.DataFrame(data=data).astype(dtype=data_types, copy=True, errors='raise')
            remove_summer_time(df)
            df.set_index("Datetime", inplace=True)
            # df.sort_index(ascending=True, inplace=True)
            output_data[file_name] = Building(file_name, sensors[1:], df)
        except ValueError:
            print("Error reading: " + str(file_name))
        est_time = (len(files) - (index + 1)) * (time.time() - start_time) / (index + 1)
        print(f"[{index + 1} / {len(files)}] IMPORT - Estimated remaining time: {awesome_time(math.floor(est_time))}", flush=True)
    return output_data


def awesome_time(seconds: int) -> str:
    return f"{int((seconds / 3600) % 60)}h {int((seconds / 60) % 60)}min {int(seconds % 60)}s"


def remove_summer_time(df: pd.DataFrame) -> None:
    timestamps = [np.datetime64(e) if e == e else e for e in df["Datetime"]]
    start_time = timestamps[0]
    start_year = start_time.astype(object).year
    summer = get_summer_start(start_year) < start_time <= get_winter_start(start_year)
    time_shift = np.timedelta64(1, 'h')
    for i in range(len(timestamps)):
        if timestamps[i] != timestamps[i]:
            continue
        current_year = timestamps[i].astype(object).year
        if timestamps[i] == get_winter_start(current_year):
            if summer:
                summer = False
                timestamps[i] -= time_shift
        if timestamps[i] == get_summer_start(current_year):
            summer = True
        if summer:
            timestamps[i] -= time_shift
    df["Datetime"] = timestamps


def get_winter_start(year: int) -> np.datetime64:
    last_day_of_october = np.datetime64(str(year) + "-10-31T03:00")
    day_offset = last_day_of_october.astype(datetime.datetime).isoweekday() % 7
    return last_day_of_october - np.timedelta64(day_offset, 'D')


def get_summer_start(year: int) -> np.datetime64:
    last_day_of_october = np.datetime64(str(year) + "-03-31T03:15")
    day_offset = last_day_of_october.astype(datetime.datetime).isoweekday() % 7
    return last_day_of_october - np.timedelta64(day_offset, 'D')


def add_temperature_data(data: dict[str, Building], directory: str) -> None:
    output_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            basename = os.path.basename(file)
            file_name, file_ext = basename.rsplit(".", 1)
            if file_ext == "csv":
                output_files.append(os.path.join(root, file))
    if len(output_files) > 1:
        exit("Too many CSV files!")
    if len(output_files) == 0:
        exit("No temperature CSV file found.")
    raw_data = pd.read_csv(output_files[0])
    raw_data.drop(columns=[k for i, k in enumerate(raw_data.keys()) if i not in [2, 3]], inplace=True)
    keys = raw_data.keys()
    temp_dict = {np.datetime64(raw_data[keys[0]][i]): float(raw_data[keys[1]][i]) for i in
                 range(len(raw_data[keys[0]]))}
    for _, b in data.items():
        b.sensors.append(Building.Sensor("Temperatur", "Wetterstation", "°C"))
        temp_df = pd.DataFrame.from_dict(temp_dict, orient="index", columns=["Temperatur"])
        b.dataframe = b.dataframe.join(temp_df)
