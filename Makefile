POETRY ?= poetry
SOURCE_DIRS ?= src

.PHONY: install-poetry
install-poetry:
	@curl -sSL https://install.python-poetry.org | python3 -

.PHONY: config-poetry
configure-poetry:
	@$(POETRY) config virtualenvs.in-project true
	@$(POETRY) config virtualenvs.create = true

.PHONY: install-deps
install-deps:
	@$(POETRY) install -vv

.PHONY: install
install: install-poetry config-poetry install-deps

.PHONY: lint-black
lint-black:
	@$(POETRY) run black $(SOURCE_DIRS)

.PHONY: lint-isort
lint-isort:
	@$(POETRY) run isort $(SOURCE_DIRS)

.PHONY: lint-flake8
lint-flake8:
	@$(POETRY) run pflake8 $(SOURCE_DIRS)

.PHONY: lint-mypy
lint-mypy:
	@$(POETRY) run mypy $(SOURCE_DIRS)

.PHONY: lint
lint: lint-black lint-isort lint-flake8 lint-mypy