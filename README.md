# Jobinja Job Scraper

A Python web scraper that collects job listings from the Jobinja website and extracts detailed information from each job posting.

## Features

* Scrapes multiple pages of job listings
* Collects basic job information:

  * Company
  * Location
  * Contract type
  * Job posting link
* Visits each job page to extract:

  * Job description
  * Required work experience
  * Salary
  * Gender requirement
  * Military service status
  * Minimum education level
  * Required skills
* Stores the collected data in a Pandas DataFrame
* Handles missing information gracefully by storing `None` for unavailable fields
* Uses custom HTTP headers to mimic a real browser

## Technologies

* Python
* Requests
* BeautifulSoup4
* Pandas


## Collected Fields

| Column          | Description                  |
| --------------- | ---------------------------- |
| links           | URL of the job posting       |
| company         | Company name                 |
| location        | Job location                 |
| contract_type   | Employment type              |
| definition      | Job description              |
| experience      | Required work experience     |
| salary          | Salary information           |
| sex             | Gender requirement           |
| military_status | Military service requirement |
| degree_requir   | Minimum education level      |
| skills          | List of required skills      |

## Notes

* The scraper is designed for educational and research purposes.
* Some job postings may not contain all fields. Missing values are stored as `None`.
* The website structure may change over time, requiring updates to the HTML selectors.

