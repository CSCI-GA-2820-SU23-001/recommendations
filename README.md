# NYU DevOps Project Template

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)

This is a skeleton you can use to start your projects

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## REST APIs
|Method     |  Endpoint               |  Description                        |
|-------    |  ---------------------  |  ---------------------------------  |
|POST       |  /recommendations       |  Creates a new recommendation       |
|GET        |  /recommendations       |  Lists all recommendations          |
|GET        |  /recommendations/{id}  |  Retrieves a recommendation  |
|PUT        |  /recommendations/{id}  |  Updates a recommendation           |
|DELETE     |  /recommendations/{id}  |  Deletes a recommendation           |

### POST /recommendations


##### Request Body
```json
{
   "user_id": 1,
   "product_id": 2,
   "recommendation_type": "UPSELL",
   "bought_in_last_30_days": True
}
```

##### Headers
- Content-Type: application/json

##### Response
- Status: 201 Created
```json
{
    "id": 1,
    "user_id": 1,
    "product_id": 2,
    "recommendation_type": "UPSELL",
    "create_date": 2023-07-04,
    "update_date": 2023-07-04,
    "bought_in_last_30_days": True
}
```
- Status: 400 Bad Request
```json
{
    "status": 400,
    "error": "Bad Request",
    "message": "No Data Provided"
}
```
```json
{
    "status": 400,
    "error": "Bad Request",
    "message": "Invalid Data Type"
}
```



## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
