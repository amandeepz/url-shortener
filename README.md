# URL Shortener Service

## Overview
A backend service that shortens long URLs, handles redirection, and tracks usage analytics.

## Features
- Generate short URLs
- Redirect to original URLs
- Click tracking
- Analytics API

## Tech Stack
- Python
- Flask
- SQLite

## How to Run

1. Install dependencies:
pip install -r requirements.txt

2. Run server:
python app.py

3. Use API:
POST /shorten  
GET /<short_id>  
GET /stats/<short_id>

## Example

Shorten:
POST /shorten  
{ "url": "https://google.com" }

Stats:
GET /stats/<short_id>
