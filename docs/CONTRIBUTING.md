# Contributing

AEPL is a teaching lab. Contributions are welcome — especially ones that make a concept clearer for the next reader.

## Quick start

```bash
git clone https://github.com/vinothhacks/agentic-edge-platform-lab.git
cd agentic-edge-platform-lab
python -m venv .venv && source .venv/bin/activate
pip install -e .
pip install ruff pytest httpx
```

## Loop

```bash
ruff check apps/ tests/
pytest tests/unit/ -q
docker compose up -d --build
```

CI runs the first two on every push.

## Code style

- Python 3.11+, type hints required on public functions.
- `ruff` is law — run it before pushing.
- Public functions get docstrings; private helpers don't need them.
- New behaviour ⇒ new test. PRs without tests get bounced.

## License

By contributing you agree your contribution is under the project's [MIT license](../LICENSE).
