# Feed Monitor

A web app that monitors data feeds between systems, flags bad records, and includes an AI assistant that explains why a feed failed and how to fix it.

**All data in this project is synthetic.** No real people or real organizations' records are used.

## Status

Work in progress.

## Run it locally

1. Copy `.env.example` to `.env` and set a password.
2. Start the database: `docker compose up -d`
3. Create a virtual environment and install packages:
   ```
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
