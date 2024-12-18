# Infoscreen Application

This application provides real-time departure information for public transport stations using the EFA (Elektronische Fahrplanauskunft) API. It is built with Flask for the backend and vanilla JavaScript for the frontend.

## Features

- Fetches real-time departure data from the EFA API.
- Displays departure information including line, direction, departure time, countdown, and delay.
- Updates departure information every 2 minutes.

## Requirements

- Python 3.7+
- Flask
- aiohttp

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/efa-departures.git
    cd efa-departures/services/web
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv .venv
    venv\Scripts\activate  # `venv/bin/activate` on Linux
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Change the URL for the EFA interface of your public transport operator and station of your choice in `web/project/__init__.py`.

2. Run the Flask application:

    a. Passing the app as an argument
    ```bash
    flask --app infoscreen run --debug # identical to `python -m flask --app infoscreen run --debug`
    ```
    b. Using environment variable
    ```bash
    $Env:FLASK_APP = "infoscreen" # `export FLASK_APP=project/__init__.py` on Linux
    python manage.py run
    ```

3. Open your web browser and navigate to `http://localhost:5000` to view the departure information.

## Docker

Start server:

 ```bash
docker-compose build
docker-compose up -d 
```

Rebuild
```bash
docker-compose up -d --build
```

Stop containers:
```bash
docker-compose down -v
```

## Project Structure

- `web/EFS_API/__init__.py`: Contains the EFA class for interacting with the EFA API.
- `web/project/__init__.py`: The main Flask application file.
- `web/project/templates/index.html`: The HTML template for displaying departure information.
- `web/project/static/styles/style.css`: The CSS file for styling the HTML template.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [aiohttp](https://docs.aiohttp.org/)
- [EFA API](https://www.efa.de/)
- EFA class based on https://finalrewind.org/interblag/entry/efa-json-api/
