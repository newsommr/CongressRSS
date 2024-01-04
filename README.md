# CongressRSS

CongressRSS is a web application that fetches and displays RSS feeds related to legislative and executive activities. The application is divided into two main parts: the back-end, built in Python with the help of FastAPI,  which is responsible for fetching and storing the RSS data, and the front-end, which displays the fetched data to the user.

## Technologies Used

- The back-end code is written in `Python`.
- The front-end code is written in `HTML, CSS,` and `JavaScript`. It is then deployed to Cloudflare Pages.
- `Docker` is used for containerization and deployment. This allows for easy deployment to Fly.io
- `FastAPI` is used for API routing.
- `Feedparser` is used for parsing various RSS feeds.
- `SQLAlchemy` is used for interacting with the SQLite database.
- `APScheduler` is used for scheduling the operations to keep the database updated in near realtime.
- And much more! Feel free to take a look through the codebase and make suggestions if you wish :)

## Directory Structure

- `back-end`: This directory contains the back-end code.
  - `app`:
    - `api.py`: Contains the various API routes and the logic for responding to requests.
    - `models.py`: Contains the models for the database tables.
    - `database.py`: Initializes the database.
    - `crud.py`: Makes changes to the database on behalf of the rest of the application.
    - `main.py`: Handles starting up the FastAPI routes and scheduling update functions.
    - `rss_fetcher.py`: Contains the logic for making request to the feeds and updating the database if needed.
    - `contact_llm.py`: Not currently used, but will handle requests to a Mixtral-8x7B model for identifying Congressional schedules.
- `static-site`: This directory contains the front-end code.
  - `fetchRSS.js`: The JavaScript code for fetching and displaying the RSS data from the back-end.
  - `index.html`: The main HTML file for the website.
  - `style.css`: The CSS styles for the website.
  - `about.html`: This page describes the projects and what data it can provide to users.
  - `meetingInfo.js`: This file contains the JavaScript code for 

## Running the Application

### Back-end

The back-end is a FastAPI application that fetches RSS data and stores it in a SQLite database. It exposes an API that the front-end can use to fetch the stored data.

To run the back-end, you need to have Python and Docker installed on your machine.

1. Navigate to the `back-end` directory.
2. Build the Docker image by running the command `docker build -t congressrss .`.
3. Run the Docker container by running the command `docker run -p 8080:8080 congressrss`.

The back-end will now be running at `http://localhost:8080`.

### Front-end

The front-end is a HTML/CSS/JavaScript site that fetches data from the back-end and displays it to the user.

To run the front-end, you just need to open the `index.html` file in your web browser.

Due to CORS, the site will not work without updating the list of acceptable origins in `main.py` in the back-end.

### API Endpoints

#### Fetch All RSSItems
- **Endpoint:** `GET /items/`
- **Description:** Fetches all items in the `RSSItem` table.
- **Parameters:**
  - `limit`: Limit the number of items (default is 100).
  - `offset`: Pagination offset (default is 0).
- **Example Request:**
https://congress-rss.fly.dev/items/?limit=3&offset=300
- **Example Response:**
```json
[
  {
    "id": 52,
    "link": "https://www.whitehouse.gov/briefing-room/legislation/2023/11/13/press-release-bills-signed-h-r-366-h-r-1226/",
    "source": "white-house-legislation",
    "pubDate": "2023-11-13T17:17:22",
    "title": "Press Release: Bills Signed: H.R. 366, H.R. 1226",
    "fetched_at": "2023-12-13T07:09:02.860506"
  },
  {
    "id": 31,
    "link": "https://rules.house.gov/video/rules-committee-hearing-5894-and-hr-6363",
    "source": "house-rules-committee",
    "pubDate": "2023-11-13T16:18:00",
    "title": "Rules Committee Hearing 5894 and H.R. 6363",
    "fetched_at": "2023-12-13T07:09:02.751020"
  },
  {
    "id": 32,
    "link": "https://rules.house.gov/bill/118/hr-cr",
    "source": "house-rules-committee",
    "pubDate": "2023-11-11T20:23:00",
    "title": "H.R. 6363 - Further Continuing Appropriations and Extensions Act, 2024",
    "fetched_at": "2023-12-13T07:09:02.753200"
  }
]
```
#### Fetch All RSSItems by Source
- **Endpoint:** `GET /items/{source}`
- **Description:** Fetches all items in the `RSSItem` table from a specific source.
- **Parameters:**
  - `limit`: Limit the number of items (default is 100).
  - `offset`: Pagination offset (default is 0).
- **Example Request:**
https://congress-rss.fly.dev/items/senateppg-twitter?limit=2
- **Example Response:**
```json
[
  {
    "id": 333,
    "link": "https://twitter.com/SenatePPG/status/1740758987489046694#m",
    "source": "senateppg-twitter",
    "pubDate": "2023-12-29T15:37:39",
    "title": "Senator Murphy (D-CT) presided today and no business was conducted.",
    "fetched_at": "2023-12-29T15:41:37.935018"
  },
  {
    "id": 327,
    "link": "https://twitter.com/SenatePPG/status/1740715555831845261#m",
    "source": "senateppg-twitter",
    "pubDate": "2023-12-29T12:45:04",
    "title": "The Second Session of the 118th Congress will convene on Wednesday, January 3, 2024 at 12 noon for a pro forma session only, with no business conducted.",
    "fetched_at": "2023-12-29T12:53:37.570786"
  }
]
```

The valid sources that can be fetched are:
- `'white-house-legislation'`: Fetches signed legislation from the White House.
- `'white-house-presidential-actions'`: Fetches presidential actions from the White House.
- `'house-rules-committee'`: Fetches data from the House Rules Committee.
- `'senateppg-twitter'`: Fetches data from the Senate Periodical Press Gallery.
- `'housedailypress-twitter'`: Fetches data from the House Daily Press Gallery.
- `'doj-olc-opinions'`: Fetches released opinions from the Office of Legal Counsel in the Department of Justice.
- `'gao-reports'`: Fetches new reports from the Government Accountability Office.

#### Search through all RSSItems
- **Endpoint:** `GET /items/search/{search_term}`
- **Description:** Searches all items in the RSSItem table based on the title attribute.
- **Parameters:**
  - `limit`: Limit the number of items (default is 100).
  - `offset`: Pagination offset (default is 0).
- **Example Request:**
https://congress-rss.fly.dev/items/search/NDAA?limit=3
- **Example Response:**
```json
[
    {
        "title": "Vote update: 2 votes at 5pm today.\n\n1. Motion to waive Paul point of order with respect to the conference report to accompany H.R.2670, the #NDAA \n2. Adoption of the conference report to accompany H.R.2670, the #NDAA",
        "pubDate": "2023-12-13T19:45:30",
        "id": 95,
        "fetched_at": "2023-12-13T19:46:31.957313",
        "source": "senateppg-twitter",
        "link": "https://twitter.com/SenatePPG/status/1735023156622942355#m"
    },
    {
        "title": "The Senate has resumed consideration of the conference report to accompany H.R.2670, the #NDAA, post-cloture.\n\nThere are no votes scheduled. \n\nUnder the regular order, unless an agreement is reached, the 30 hours of post-cloture time expires at  approximately 12:30am ET tonight.",
        "pubDate": "2023-12-13T16:59:17",
        "id": 92,
        "fetched_at": "2023-12-13T17:52:51.920921",
        "source": "senateppg-twitter",
        "link": "https://twitter.com/SenatePPG/status/1734981329433894937#m"
    },
    {
        "title": "The Senate is now voting on the Ernst Motion to Table the Schumer Motion to Recommit (NDAA Conference Report).",
        "pubDate": "2023-12-12T20:12:59",
        "id": 80,
        "fetched_at": "2023-12-13T07:10:51.028224",
        "source": "senateppg-twitter",
        "link": "https://twitter.com/SenatePPG/status/1734667686246834468#m"
    }
]
```
#### Get Next Meeting Information
- **Endpoint:** `GET /info/session/{chamber}`
- **Description:** Gets the next meeting information for the House or Senate based on the specified chamber parameter.
- **Example Request:**
https://congress-rss.fly.dev/info/session/senate
- **Example Response:**
```json
{
  "in_session": 0,
  "next_meeting": "2024-01-02 16:45:00+00:00",
  "live_link": "https://www.senate.gov/isvp/stv.html?type=live&comm=stv&filename=stv010224",
  "last_updated": "2024-01-01T04:22:36.559394"
}
```
## Contributing

All contributions are welcome, especially if you have found a useful feed to pull from! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
