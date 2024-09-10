lint: # Check for any code writing error
	pylint client/

venv: # Activate the virtual environment (creates a new one if no environment has been created before)
	pipenv shell

install_requirements: # Install project requirements
	pip install -r requirements.txt

help: # Print help on Makefile
	@findstr '^[^.#]\+:\s\+.*#' Makefile | \
	sed "s/\(.\+\):\s*\(.*\) #\s*\(.*\)/`printf "\033[93m"`\1`printf "\033[0m"`	\3 [\2]/" | \
	expand -t20