# Selenium Educational Project — Job Offer Scraper

This is an **educational** Python project demonstrating how to use **Selenium** to scrape job offers from [JustJoin.it](https://justjoin.it/).  
It is designed for learning purposes and may require adjustments if the target website changes.

---

## Features
- Select **location** and **job title** via command-line arguments
- Automatically scrolls through the dynamically loaded offers
- Collects:
  - Job title
  - Company name
  - Salary information (if available)
  - Location
  - Type of work, Experience level, Employment type, Operating mode
  - Skills with proficiency levels
  - Job description paragraphs
  - Direct job link
- Saves results to `data.json`
- Logs errors to `scraper_errors.log`

---

## Requirements
- **Python** 3.8+
- Google Chrome installed
- ChromeDriver (matching your Chrome version) — Selenium will usually auto-manage this if configured
- The following Python packages:
  ```bash
  pip install selenium selenium-stealth

## Usage
Run the scraper from the command line:
    **python projekt.py --location "Wrocław" --job "CyberSecurity"**
Arguments:
  
  --location → City to search in (must match one of the buttons on the site)
  
  --job → Job keyword to search

## Output
data.json — A JSON file with all scraped offers
scraper_errors.log — Log file with any scraping errors
