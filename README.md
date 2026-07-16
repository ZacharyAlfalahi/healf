# Healf wellness assistant

A command-line assistant that answers a customer's health question using a small
research library and product catalogue, tailored to their profile. It helps with
wellness and product choices; it never diagnoses, prescribes, or interprets
results the way a clinician would.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then add your GEMINI_API_KEY
```

## Run

```bash
python -m app.cli
```

## What works so far

- Streaming chat from the command line.
- A research corpus and product catalogue with similarity and field search.
