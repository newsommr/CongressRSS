# CongressRSS

CongressRSS is a web application that consolidates U.S. government communicates across the executive, legislative, and judicial branches. The project is divided into two main parts: the back-end, built in Python, which is responsible for fetching and storing the communications, and the front-end, which displays the fetched data to the user.

## Technologies Used

- **Backend**: Written in `Python` using `FastAPI` for API routing and deployed with Docker on [Fly.io](https://fly.io).
- **Frontend**: Built with `HTML`, `CSS`, and `JavaScript`, and deployed to Cloudflare Pages.
- **RSS Parsing**: [`Feedparser`](https://pypi.org/project/feedparser/) is used to handle RSS feed parsing.
- **Database**: `SQLAlchemy` is used for interacting with the SQLite database.
- **Task Scheduling**: `APScheduler` is used to schedule database updates in near real-time.
- **And much more!** Feel free to take a look through the codebase and make suggestions if you wish :)

## Running the Application

The back-end is a FastAPI application that exposes an API that the front-end can use to fetch the stored data.

1. Navigate to the `back-end` directory.
2. Build the Docker image by running the command `docker build -t congressrss .`.
3. Run the Docker container by running the command `docker run -p 8080:8080 congressrss`.

The back-end will now be running at [http://localhost:8080](http://localhost:8080).

## API Endpoints

### Fetch All RSSItems

- **Example Request:** [https://congress-rss.fly.dev/feed?limit=3](https://congress-rss.fly.dev/feed?limit=3)
- **Parameters:**
  - `limit`: Limit the number of items (default is 100).
  - `offset`: Pagination offset (default is 0).
  - `sources`: Filter items by specific sources (optional).
  - `search_term`: Search for items based on the title (optional).
- **Successful Response:**

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

- **Example Response:** [https://congress-rss.fly.dev/feed?search_term=NATO%202025&limit=100&offset=0](https://congress-rss.fly.dev/feed?search_term=NATO%202025&limit=100&offset=0)

- **Failed Response:**

  ```json
  {
    "status": "error",
    "data": null,
    "message": "Items not found"
  }
  ```

### Get Next Meeting Information

- **Example Request:** [https://congress-rss.fly.dev/legislative/session-info](https://congress-rss.fly.dev/legislative/session-info)
- **Example Response:**

```json
{
  "status": "success",
  "data": [
    {
      "chamber": "senate",
      "in_session": 0,
      "next_meeting": "2024-07-02T16:00:00",
      "live_link": "https://www.senate.gov/isvp/stv.html?type=live&comm=stv&filename=stv070224",
      "last_updated": "2024-07-01T03:45:16.391670"
    },
    {
      "chamber": "house",
      "in_session": 0,
      "next_meeting": "2024-07-02T15:00:00",
      "live_link": "https://live.house.gov",
      "last_updated": "2024-07-01T03:45:17.056047"
    }
  ],
  "message": null
}
```

## Contributing

All contributions are welcome, especially if you have found a useful feed to pull from! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.
