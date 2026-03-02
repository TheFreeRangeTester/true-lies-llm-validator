.PHONY: install test quick-test

install:
	pip install -e ".[dev]"

test:
	python -m pytest tests/ -v --tb=short

# Run tests + generate HTML report (for verifying reporter changes)
quick-test:
	python scripts/quick_test.py
