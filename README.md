# CongressRSS

CongressRSS is a web application that fetches and displays RSS feeds related to Congress or legislative activities. The application is divided into two main parts: the back-end, which is responsible for fetching and storing the RSS data, and the front-end, which displays the fetched data to the user.

## Technologies Used

- Python: The back-end code is written in Python.
- HTML, CSS, JavaScript: The front-end code is written in these languages.
- Docker: Docker is used for containerization.
- FastAPI: FastAPI is used for API routing.
- SQLAlchemy: SQLAlchemy is used for database operations.
- APScheduler: APScheduler is used for scheduling tasks.
- Feedparser: Feedparser is used for parsing RSS feeds.

## Directory Structure

- `back-end`: This directory contains the back-end code.
  - `app`: This directory contains the main application code.
    - `api.py`: This file contains API-related code.
    - `database.py`: This file contains database-related code.
    - `main.py`: This file contains the main application logic.
    - `rss_fetcher.py`: This file contains code for fetching RSS feeds.
- `static-site`: This directory contains the front-end code.
  - `fetchRSS.js`: This file contains the JavaScript code for fetching and displaying the RSS data.
  - `index.html`: This is the main HTML file for the website.
  - `style.css`: This file contains the CSS styles for the website.

## Running the Application

### Back-end

The back-end is a FastAPI application that fetches RSS data and stores it in a SQLite database. It exposes an API that the front-end can use to fetch the stored data.

To run the back-end, you need to have Python and Docker installed on your machine.

1. Navigate to the `back-end` directory.
2. Build the Docker image by running the command `docker build -t congressrss .`.
3. Run the Docker container by running the command `docker run -p 8080:8080 congressrss`.

The back-end will now be running at `http://localhost:8080`.

### Front-end

The front-end is a simple static website that fetches data from the back-end and displays it to the user.

To run the front-end, you just need to open the `index.html` file in your web browser.

## API Endpoints

The back-end exposes the following API endpoints:

- `GET /items/`: Fetches all items. You can limit the number of items by passing a `limit` query parameter.
- `GET /items/{source}`: Fetches items from a specific source. You can limit the number of items by passing a `limit` query parameter.

The valid sources that can be fetched are:
- `'white-house-legislation'`: Fetches signed legislation from the White House.
- `'white-house-presidential-actions'`: Fetches presidential actions from the White House.
- `'house-rules-committee'`: Fetches data from the House Rules Committee.
- `'senateppg-twitter'`: Fetches data from the Senate Periodical Press Gallery.
- `'housedailypress-twitter'`: Fetches data from the House Daily Press Gallery.

For example, to fetch items from the House Rules Committee, you would use the endpoint `GET /items/house-rules-committee`.

## Contributing

All contributions are welcome, especially if you have found a useful feed to pull from! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
