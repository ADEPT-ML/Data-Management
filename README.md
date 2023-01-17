# Data-Management 🗃️

The service is responsible for managing all building data available to ADEPT.

## Requirements

+ Python ≥ 3.10
+ All packages from requirements.txt

## Development

### Local

Install dependencies from requirements.txt

Start the service:

```sh
uvicorn main:app --reload
```

### Docker

We provide a docker-compose in the root directory of ADEPT to start all services bundled together.

## Adding functionality

ADEPT is designed to work with specific datasets provided by the university. If you want to use it with a different data
format, you must at least change the importer.

### Directory structure

```
\-Explainability
    ├── src                                     # Python source files for base functions
    │   ├── importer.py                         # Functions for data-import
    │   └── [...]
    ├── Dockerfile
    ├── main.py                                 # Main module with all API definitions
    ├── requirements.txt                        # Required python dependencies
    └── [...]
```

### Changing the importer

The three microservices that handle import, pre-processing and feature engineering are all dependent on a specific
dictionary representations of the buildings. The representation is quite generic, but you need to adapt your data to its
format. The objects look something like this:

```
{
    "buildingA": {
        "name": "buildingA", 
        "sensors": [{"type": "Elektrizität", "desc": "P Summe", "unit": "kW"}], 
        "dataframe": {
            "Elektrizität": {
                "1642809600000":1.5355268051,"1642810500000":0.5147979489, [...]
            }
        }
    },
    "buildingB": {
        "name": "buildingB", 
        "sensors": [{"type": "Elektrizität", "desc": "P Summe", "unit": "kW"}], 
        "dataframe": {
            "Elektrizität": {
                "1642809600000":1.5355268051,"1642810500000":0.5147979489, [...]
            }
        }
    },
    [...]
}
```

As a starting point, you will find the code for parsing files in the `parse_files` function
in [importer.py](src/importer.py).

Copyright © ADEPT ML, TU Dortmund 2023