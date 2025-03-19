# PyMock

[![PyPI - Version](https://img.shields.io/pypi/v/pymock.svg)](https://pypi.org/project/pymock)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pymock.svg)](https://pypi.org/project/pymock)
![PyMock](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Build](https://img.shields.io/github/actions/workflow/status/qualitycoe/pymock/ci.yml)

-----

## 📖 Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [Running via CLI](#running-via-cli)
  - [Defining Endpoints](#defining-endpoints)
  - [Scenarios \& Rule Logic](#scenarios--rule-logic)
  - [Jinja2 Templates](#jinja2-templates)
- [Configuration](#configuration)
  - [Environment Variable Overrides](#environment-variable-overrides)
- [Advanced Usage](#advanced-usage)
  - [Caching](#caching)
  - [Docker Support](#docker-support)
- [Usage Examples](#usage-examples)
  - [Mocking an API](#mocking-an-api)
  - [Conditional Responses with Rules](#conditional-responses-with-rules)
- [License](#license)
- [Contact](#contact)

---

## 🚀 Introduction

**PyMock** is a **versatile Flask-based mock server** that lets you define endpoints, behavior, and conditional responses with minimal effort. It’s designed to help you:

1. **Stand up quick mock APIs** for prototyping or testing.
2. **Validate incoming requests** with rule-based logic.
3. **Dynamically generate responses**, including template rendering via Jinja2.

Under the hood, PyMock uses **RuleEngineX** to evaluate incoming requests. However, **PyMock** is fully self-contained: you don’t need prior RuleEngineX knowledge to define your endpoints and rules. Everything is configured through **YAML** files.

---

## 🔥 Features

✔ **Easy Endpoint Definition**: Write YAML files to define routes and HTTP methods.
✔ **Rule-Based Matching**: Condition your responses on request data (headers, query params, body, etc.).
✔ **Jinja2 Templating**: Render custom text, HTML, or JSON with dynamic data.
✔ **Caching**: Speed up repeated responses with in-memory caching.
✔ **Docker Support**: Simple Dockerfile provided for containerizing your mock server.
✔ **Configurable**: Set server host, port, and endpoint directories in a single YAML or via environment variables.
✔ **Lightweight & Extensible**: Built on Flask and easily extended or integrated into broader testing pipelines.

---

## 📦 Installation

### From Source or Git

```bash
git clone https://github.com/qualitycoe/pymock.git
cd pymock
pip install .
```

Or in your own `requirements.txt`:

```
pymock @ git+https://github.com/qualitycoe/pymock.git@main#egg=pymock
```

> *(PyPI publishing is planned. If available, simply `pip install pymock`.)*

### Development with Hatch

If you wish to develop or contribute:

```bash
# 1) Ensure Hatch is installed: pip install hatch
# 2) Create a local environment and install dev dependencies
hatch env create
# 3) Run tests
hatch run test
```

---

## 🚀 Quick Start

### 1️⃣ Running via CLI

1. **Create** a YAML configuration file (e.g. `config.yaml`) specifying the server settings and one or more directories for endpoints.
2. **Launch** the server using the CLI:

   ```bash
   pymock config.yaml
   ```

   By default, it starts on `127.0.0.1:5000` (unless otherwise configured).

### 2️⃣ Defining Endpoints

Inside each directory listed under `endpoints_path` in your `config.yaml`, you can place multiple `.yaml` files. **Each file** may define one or more endpoints. For example:

```yaml
# endpoints/users.yaml
path: "/users"
method: "GET"
scenarios:
  - scenario_name: "Fetch Admin Users"
    rules_data:
      - target: "query_params"
        prop: "admin"
        op: "EQUALS"
        value: "true"
    response:
      status: 200
      data:
        message: "Admin users retrieved."
        admin_users:
          - id: 1
          - id: 2
```

- **`path`**: The route path (e.g., `/users`).
- **`method`**: The HTTP method (e.g., `GET`, `POST`).
- **`scenarios`**: A list of scenario objects, each containing:
  - **`scenario_name`**: A readable name or identifier.
  - **`rules_data`**: Conditions for matching this scenario. *(More below.)*
  - **`response`**: What to return when the scenario matches. May include `status`, `data`, `headers`, or a `template`.

> **Note**: If multiple scenarios match, **PyMock** returns the first matching scenario’s response.

### 3️⃣ Scenarios & Rule Logic

Each scenario’s `rules_data` is a **list of rules** that all must be satisfied for that scenario to match. A **rule** is defined by four main fields:

- **`target`**: The part of the request you’re matching (e.g. `"body"`, `"headers"`, `"query_params"`, `"path"`, `"method"`).
- **`prop`**: The property (or JSONPath) within that target. Examples:
  - **Dot-notation**: `"user.name"`
  - **JSONPath**: `"$.users[*].id"`
  - Or `""` (empty) if you want the entire target.
- **`op`**: The operator (e.g. `EQUALS`, `REGEX`, `ARRAY_INCLUDES`).
- **`value`**: The value you want to compare against (could be a string, integer, regex pattern, etc.).

Some commonly used operators:

| Operator                    | Description                                             |
|-----------------------------|---------------------------------------------------------|
| `EQUALS`                    | Checks if two values are strictly the same             |
| `REGEX`                     | Case-sensitive regex match                              |
| `REGEX_CASE_INSENSITIVE`    | Case-insensitive regex match                           |
| `NULL`                      | Checks if the value is `None`                          |
| `EMPTY_ARRAY`               | Checks if the value is an empty list                   |
| `ARRAY_INCLUDES`            | Checks if a list contains a specific element           |
| `VALID_JSON_SCHEMA`         | Validates data against a JSON Schema definition        |

### 4️⃣ Jinja2 Templates

You can **render Jinja2 templates** if your scenario’s response includes a `template` key:

```yaml
path: "/hello"
method: "GET"
scenarios:
  - scenario_name: "Greeting"
    rules_data: []
    response:
      status: 200
      template: "greeting.html"
      data:
        name: "{{ request.args.get('name', 'Guest') }}"
```

In the `greeting.html` file (placed in a `templates` directory):

```html
<html>
  <body>
    <h1>Hello, {{ name }}!</h1>
  </body>
</html>
```

When a request hits `/hello?name=Alice`, PyMock will merge the `data` dictionary into the Jinja2 template context, rendering `"Hello, Alice!"`.

---

## Configuration

A basic `config.yaml` might look like:

```yaml
server:
  host: "127.0.0.1"
  port: 5000

endpoints_path:
  - "endpoints/"
  - "custom_endpoints/"
```

- **`server.host`**: IP or hostname where Flask listens.
- **`server.port`**: Port number.
- **`endpoints_path`**: List of directories containing `.yaml` endpoint definitions.

### Environment Variable Overrides

PyMock also supports environment variables to override certain config fields:

| Environment Variable              | Overwrites                |
|----------------------------------|---------------------------|
| `PYMOCK__SERVER__HOST`           | `server.host`             |
| `PYMOCK__SERVER__PORT`           | `server.port`             |
| `PYMOCK__SERVER__ENDPOINTS_PATH` | `endpoints_path` (comma-separated) |

Example:

```bash
export PYMOCK__SERVER__HOST="0.0.0.0"
export PYMOCK__SERVER__PORT="8080"
pymock config.yaml
```

Now it starts on `0.0.0.0:8080`.

---

## Advanced Usage

### Caching

PyMock includes **Flask-Caching**. By default, each scenario’s response is cached for 60 seconds based on request path + query parameters. This can be configured in `cache.py` or overridden by customizing the Flask config.

### Docker Support

Build and run PyMock in Docker:

```bash
# 1) Build the image (from the Dockerfile)
docker build -t pymock .
# 2) Run the container
docker run --rm -p 5000:5000 pymock
```

To customize or mount a different `config.yaml`, you can do:

```bash
docker run -d -p 5000:5000 \
  -v $(pwd)/my_config.yaml:/app/config.yaml \
  --name pymock_server \
  pymock
```

---

## Usage Examples

### Mocking an API

Suppose you need a quick mock for an external service:

1. In `endpoints/service.yaml`:

    ```yaml
    path: "/api/v1/data"
    method: "GET"
    scenarios:
      - scenario_name: "All Data"
        rules_data: []
        response:
          status: 200
          data:
            items:
              - id: 1
                name: "Sample 1"
              - id: 2
                name: "Sample 2"
    ```

2. Start PyMock:
    ```bash
    pymock config.yaml
    ```

3. Send a request:
    ```bash
    curl http://127.0.0.1:5000/api/v1/data
    # => returns the JSON in the scenario's 'data' field
    ```

### Conditional Responses with Rules

If you want to return a **different** response based on a query parameter:

```yaml
path: "/api/v1/items"
method: "GET"
scenarios:
  - scenario_name: "Has Query Param"
    rules_data:
      - target: "query_params"
        prop: "type"
        op: "EQUALS"
        value: "special"
    response:
      status: 200
      data:
        message: "Found special items!"

  - scenario_name: "Default"
    rules_data: []
    response:
      status: 404
      data:
        error: "Not found"
```

- If `?type=special`, we get `message: Found special items!`
- Otherwise, we get a `404` response with `"Not found"`.

---

## 📖 License

PyMock is distributed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.

---

## 📬 Contact

- **Issues & Questions**: Open a GitHub issue at [PyMock Issues](https://github.com/qualitycoe/pymock/issues).
- **Email**: For direct inquiries, contact `qualitycoe@outlook.com`.
