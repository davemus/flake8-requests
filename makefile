dev:
	poetry shell

setup:
	poetry install

release:
	poetry publish --build

test:
	export PYTHONPATH=`pwd`/src
	pytest

clean:
	rm -rf build dist README MANIFEST *.egg-info

distclean: clean
	rm -rf .venv