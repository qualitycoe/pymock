# pymock

[![PyPI - Version](https://img.shields.io/pypi/v/pymock.svg)](https://pypi.org/project/pymock)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pymock.svg)](https://pypi.org/project/pymock)

-----

  # pymock

  **pymock** is a lightweight mock server built using **Flask**. It allows you to configure endpoints, request rules, and dynamic responses all via YAML files. This makes it easy to prototype or test API behaviors without writing additional code.

  ## Table of Contents

  1. [Features](#features)
  2. [Requirements](#requirements)
  3. [Installation](#installation)
  4. [Configuration](#configuration)
     - [Config File](#config-file)
     - [Environment Variable Overrides](#environment-variable-overrides)
     - [Endpoints Definition](#endpoints-definition)
  5. [Usage](#usage)
     - [Running the Server](#running-the-server)
     - [Example Usage](#example-usage)
  6. [Rules Engine](#rules-engine)
     - [Targets](#targets)
     - [Operators](#operators)
  7. [Templates](#templates)
  8. [Caching](#caching)
  9. [Contributing](#contributing)
  10. [License](#license)

  ---

  ## 1. Features

  - **Rule-based request matching**: Configure rules that inspect request body, headers, params, method, and more.
  - **Powerful condition logic**: Use JSON Path, regex matching, schema validation, array checks, etc.
  - **Flexible response**: Return either a Jinja2-rendered template or JSON data.
  - **Easy configuration**: Store all behavior in YAML files (including environment-based overrides).
  - **Multiple endpoint directories**: Scan multiple folders for YAML endpoint definitions.
  - **Dynamic path parameters**: Routes can contain `<variable>` parts accessible to your rules.

  ---

  ## 2. Requirements

  - **Python 3.7+**
  - **Flask**
  - **PyYAML**
  - **jsonschema** (for JSON schema validation)
  - **jsonpath-ng** (for JSON path extraction)

  > These dependencies can be installed automatically via `requirements.txt` or manually.

  ---

  ## 3. Installation

  1. **Clone** this repository (or copy the code into your own project):
      ```bash
      git clone https://github.com/<username>/pymock.git
      cd pymock
      ```
  2. **Create and activate** a virtual environment (recommended):
      ```bash
      python -m venv venv
      source venv/bin/activate   # Linux/macOS
      # or venv\Scripts\activate # Windows
      ```
  3. **Install dependencies**:
      ```bash
      pip install -r requirements.txt
      ```

  ---

  ## 4. Configuration

  ### 4.1 Config File

  The main configuration is controlled by `config.yaml` at the root (or specify the path in the code). Here is an example:

  ```yaml
  server:
    host: "127.0.0.1"
    port: 5000

  # Define one or more directories containing endpoint definitions
  endpoints_path:
    - "endpoints/"
    - "custom_endpoints/"
  ```

  - **server**:
    - `host`: IP address or hostname to bind to (default: `"127.0.0.1"`).
    - `port`: Port number to run on (default: `5000`).
  - **endpoints_path**: One or more directory paths (strings) where the server will recursively scan for YAML files defining endpoints.

  ### 4.2 Environment Variable Overrides

  You can override specific settings in `config.yaml` by providing environment variables:

  | Environment Variable                     | YAML Key                   | Description                                                 |
  |-----------------------------------------|----------------------------|-------------------------------------------------------------|
  | `PYMOCK__SERVER__HOST`                  | `server.host`             | Overrides the host address                                 |
  | `PYMOCK__SERVER__PORT`                  | `server.port`             | Overrides the port number                                  |
  | `PYMOCK__SERVER__ENDPOINTS_PATH`        | `endpoints_path`          | Comma-separated list of directory paths for endpoints      |

  **Examples**:
  ```bash
  export PYMOCK__SERVER__HOST="0.0.0.0"
  export PYMOCK__SERVER__PORT="8080"
  export PYMOCK__SERVER__ENDPOINTS_PATH="my_endpoints,custom_endpoints"
  ```

  > Environment variables take first priority if set, otherwise the server falls back to the YAML config values.

  ### 4.3 Endpoints Definition

  In the directories listed under `endpoints_path`, you can define multiple **endpoint YAML files**. Each file may contain one or more endpoints, for example:

  ```yaml
  # endpoints/get_user.yaml

  - path: "/users/<user_id>"
    method: "GET"
    rules:
      - conditions:
          - target: "route_params"
            property: "user_id"
            operator: "equals"
            value: "123"
        response:
          status: 200
          data:
            message: "User 123 found!"
      - conditions:
          - target: "route_params"
            property: "user_id"
            operator: "equals"
            value: "456"
        response:
          status: 200
          data:
            message: "User 456 found!"
  ```

  **Key fields** in each endpoint definition:

  - `path`: The route path (supports Flask-style path parameters like `<user_id>`).
  - `method`: HTTP method (e.g. GET, POST, PUT, etc.).
  - `rules`: A list of rule objects. Each rule has:
    - `conditions`: An array of conditions that must all be satisfied for the rule to match.
    - `response`: What to return if the rule matches (`status`, `data`, optional `template`).

  > If an endpoint also specifies `template: "my_template.html"`, then the server will render the Jinja2 template with the `data` variables passed in.

  ---

  ## 5. Usage

  ### 5.1 Running the Server

  1. **Ensure** you have a valid `config.yaml` in the root folder (or set up environment variables).
  2. **Run** `app.py`:

      ```bash
      python app.py
      ```

     The server will bind to the configured host and port, logging requests and rule evaluations.

  ### 5.2 Example Usage

  **Local Testing**:

  ```bash
  curl http://127.0.0.1:5000/users/123
  # => { "message": "User 123 found!" }

  curl http://127.0.0.1:5000/users/456
  # => { "message": "User 456 found!" }

  curl http://127.0.0.1:5000/users/999
  # => 404 { "error": "No matching rule found" }
  ```

  ---

  ## 6. Rules Engine

  The rules engine checks **conditions** under an endpoint in order. Each rule has an array of conditions. All conditions in a rule must be met (logical AND) for that rule to match. The first matching rule returns its response.

  ### 6.1 Targets

  Each condition specifies a **target**, which tells the engine **where to look**:

  | Target           | Meaning                                                           |
  |------------------|-------------------------------------------------------------------|
  | `body`           | JSON body of the request                                         |
  | `params`         | Query parameters (i.e., `request.args`)                           |
  | `headers`        | HTTP request headers                                             |
  | `cookies`        | Cookies sent by the client                                       |
  | `method`         | The HTTP method (GET, POST, etc.)                                |
  | `path`           | The URL path (e.g., `/users/123`)                                |
  | `route_params`   | Values captured from dynamic routes (e.g., `<user_id>`)          |
  | `number`         | Special handling if you expect numeric data in query/body (stub) |
  | `global_variable`| Custom logic to retrieve a global variable (not fully implemented)|
  | `data_bucket`    | Custom logic to retrieve data from an external bucket or DB (stub)|

  ### 6.2 Operators

  Each condition also uses an **operator** for comparison. Supported operators include:

  - `equals`
  - `regex`
  - `regex (case-insensitive)`
  - `null`
  - `empty array`
  - `array includes`
  - `valid JSON schema`

  For example:

  ```yaml
  - target: "headers"
    property: "X-Api-Key"
    operator: "equals"
    value: "secret"
  ```

  **Invert Matching**
  You can optionally include `"invert": true` in a condition to negate the match result (e.g., "not equals").

  ---

  ## 7. Templates

  If an endpoint rule specifies a `template`, the system will render that template using Jinja2, passing `data` as template variables.

  1. **Folder**: Templates are searched in the `templates/` directory (configurable in `FileSystemLoader`).
  2. **Usage**:
     ```yaml
     - path: "/about"
       method: "GET"
       template: "about.html"
       rules:
         - conditions: []  # or some conditions
           response:
             status: 200
             data:
               title: "About Us"
               description: "This is a simple static page."
     ```

  In `about.html`, you can reference `{{ title }}` and `{{ description }}`.

  ---

  ## 8. Caching

  This mock server uses a simple **in-memory cache** (`CACHE`) keyed by `<path>-<query_string>`. Once a request is matched, subsequent identical requests will return the same response data from the cache. This is helpful for repeated calls to the same route/query.

  **Note**: The cache is purely in-memory and **not** thread-safe for heavy production usage. If you need advanced caching or concurrency, consider an external store (e.g., Redis).

  ---

  ## 9. Contributing

  1. Fork or clone the repo.
  2. Create a feature branch.
  3. Submit a pull request describing your changes.

  Suggestions and contributions are always welcome!

  ---

  ## 10. License

  This project is licensed under the [MIT License](LICENSE). Feel free to modify and adapt it to your needs.

  ---

  **Questions or feedback?** Open an issue or create a discussion on the repository. Enjoy your mock server!
