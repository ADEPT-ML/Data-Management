# Data-Management 🗃️

The service is responsible for managing all building data available to ADEPT.

## Requirements

+ Python >3.10
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

Copyright © ADEPT ML, TU Dortmund 2022