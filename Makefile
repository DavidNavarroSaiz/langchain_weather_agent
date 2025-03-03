install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv tests/

format:	
	black *.py tests/*.py

lint:
	pylint --disable=R,C --fail-under=7 *.py

container-lint:
	docker run --rm -i hadolint/hadolint < Dockerfile

checkgpu:
	echo "Checking GPU for PyTorch"
	python utils/verify_pytorch.py
	echo "Checking GPU for Tensorflow"
	python utils/verify_tf.py

refactor: format lint

all: install lint test format 