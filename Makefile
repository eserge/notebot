POETRY ?= poetry

.PHONY: install-poetry
install-poetry:
	@curl -sSL https://install.python-poetry.org | python3 -

.PHONY: config-poetry
configure-poetry:
	@$(POETRY) config virtualenvs.in-project true
	@$(POETRY) config virtualenvs.create = true

.PHONY: install-deps
install-deps:
	@$(POETRY) install --no-dev -vv

.PHONY: install
install: install-poetry config-poetry install-deps

.PHONY: server
server:
	@$(POETRY) run uvicorn app:app --host $(APP_HOST)