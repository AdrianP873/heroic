.PHONY: app_test pipeline_test

py_install:
		python -m pip install --upgrade pip
		pip install flake8 pytest
		if [ -f requirements.txt ]; then pip install -r requirements.txt; fi

py_lint:
		echo "linting source"

py_test:
		echo "testing source"
		pytest