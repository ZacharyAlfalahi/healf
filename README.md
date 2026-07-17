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
cp .env.example .env            # then add your GEMINI_API_KEY
```

## Run

```bash
python -m app.cli
```

## Test

```bash
python -m pytest                    # fast offline checks that the app is wired up
HEALF_RUN_LIVE=1 python -m pytest   # also runs the four demo turns against the API
```

## How it's built

Each reply is one pass of a stateless loop. The model is given the system
prompt, the customer profile, and the conversation, and can call two tools:
`search_research` (similarity search over the research corpus using Gemini
embeddings) and `search_products` (exact substring search over the catalogue).
It decides when to search and reasons over the results between calls, then
streams the answer to the terminal. It stays in its lane — declining
medications, interactions, and diagnosis with a signpost — and says when the
library has no evidence rather than guessing. Prices are added by the CLI after
the answer, looked up by id, so they never enter the model's context.

See `REASONING.md` for the design decisions.
