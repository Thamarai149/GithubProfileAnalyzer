# Backend

Backend is a modern Python console application that uses the GitHub REST API to inspect a user’s public profile, summarize repository activity, and export a polished report.

## Features

- Welcome banner and interactive menu
- Analyze a GitHub username
- Compare two GitHub users
- Display profile metadata and repository insights
- Show top repositories by stars
- Render language usage with ASCII progress bars
- Export reports to TXT and JSON
- Gracefully handle invalid usernames and network issues
- New web backend API and frontend dashboard

## Requirements

- Python 3.9+
- Internet access for GitHub API requests

## Setup

1. Clone or open the project folder.
2. Create and activate a virtual environment:
   - Windows:
     - `python -m venv .venv`
     - `.venv\Scripts\activate`
3. Install dependencies:
   - `pip install -r requirements.txt`
4. Run the application:
   - `python main.py`

## Project Structure

- `main.py` - application entry point
- `backend/` - modular source package
  - `app.py` - main application flow
  - `api.py` - GitHub API client
  - `analyzer.py` - data processing and metrics
  - `ui.py` - Rich terminal interface
  - `exporter.py` - TXT/JSON export helpers
  - `models.py` - data models

## Notes

This project uses the public GitHub API and does not require authentication for basic profile and repository analysis.
