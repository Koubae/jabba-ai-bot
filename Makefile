.PHONY: run stop logs build flake8 black mypy isort tests unit integration

VENV := .venv

# ============================
#       Local Development
# ============================

run:
	@pipenv shell && python main.py


# --------------------------
# Init
# --------------------------
init-venv: .update-env-file .install-pip-env .install-env .install-deps

.install-pip-env:
	pip install --user pipenv

.install-env:
	pipenv install --python=$(which python)

.install-deps:
	@pipenv shell && pipenv update

.update-env-file:
	@echo 'Updating .env from .env.example 🖋️...'
	# Updating .env
	@cp .env.example .env


# =========================
# 		Code Quality
# =========================
quality-checks: isort black flake8 mypy

flake8:
	@pipenv shell && flake8 --config=.flake8 main.py src/

black:
	@pipenv shell && black --config=pyproject.toml jabba-ai-bot.py src/

mypy:
	@pipenv shell && mypy main.py && mypy src/

isort:
	@pipenv shell &&  isort main.py src/


# =========================
# 		Tests
# =========================
