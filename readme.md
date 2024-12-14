# EFA Departures Application

This application provides real-time departure information for Vaihingen Bahnhof using the EFA (Elektronische Fahrplanauskunft) API. It is built with Flask for the backend and vanilla JavaScript for the frontend.

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
    cd efa-departures
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1. Run the Flask application:
    ```bash
    python webserver.py
    ```

2. Open your web browser and navigate to `http://127.0.0.1:5000` to view the departure information.

## Project Structure

- `webserver.py`: The main Flask application file.
- `efa.py`: Contains the EFA class for interacting with the EFA API.
- `templates/index.html`: The HTML template for displaying departure information.
- `static/styles/style.css`: The CSS file for styling the HTML template.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any changes.

## Acknowledgements

- [Flask](https://flask.palletsprojects.com/)
- [aiohttp](https://docs.aiohttp.org/)
- [EFA API](https://www.efa.de/)
