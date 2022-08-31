.ONESHELL:

VERSION := $(shell sed 's/^__version__ = "\(.*\)"/\1/' ./dalle_runtime/version.py)
DOCKER_IMAGE := axsaucedo/mlserver:dalle_runtime-${VERSION}
PACKAGE_NAME := dalle_runtime

install-dev-deps:
	asdf plugin-add poetry https://github.com/asdf-community/asdf-poetry.git


conda-env-remove:
	conda env remove -y -n ${PACKAGE_NAME} \
		|| echo "Please change env with 'conda activate'"


conda-env-create:
	conda create -y --name ${PACKAGE_NAME} \
		python=3.8 || echo "Env already exists"

conda-env-create-dev:
	conda create -y --name ${PACKAGE_NAME}_dev \
		python=3.8 || echo "Env already exists"

conda-env-remove-dev:
	conda env remove -y -n ${PACKAGE_NAME}_dev \
		|| echo "Please change env with 'conda activate'"

## Install Python Dependencies
install:
	poetry install -vv --no-dev

## Install Python Dev Dependencies
install-dev:
	poetry install -vv

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete

fmt:
	black .

## Lint using flake8
lint:
	black --check .
	mypy .
	flake8 .

local-download-resources:
	git clone https://huggingface.co/dalle-mini/vqgan_imagenet_f16_16384 dalle_runtime/min-dalle/pretrained/vqgan
	wandb artifact get --root=./dalle_runtime/min-dalle/pretrained/dalle_bart_mini dalle-mini/dalle-mini/mini-1:v0

local-test-request:
	curl http://localhost:8080/v2/models/test-model/infer \
		-H "Content-Type: application/json" \
		-d '{"inputs":[{"name":"test_input","shape":[3],"datatype":"INT32","data":[1,2,3]}]}'

local-start:
	mlserver start docs/examples/.

local-stop:
	killall mlserver

docker-build:
	docker build . -t ${DOCKER_IMAGE}

docker-push:
	docker push ${DOCKER_IMAGE}

docker-run:
	docker run --rm -d -p 8080:8080 -it --name dalle_runtime --rm ${DOCKER_IMAGE}

###########################################################################################
# Security
##########################################################################################

security-all: security-local-dependencies security-local-dependencies-old security-local-code security-docker

security-local-dependencies-old:
	poetry export --without-hashes -f requirements.txt | piprot --latest --outdated -

security-local-dependencies:
	poetry export --without-hashes -f requirements.txt | safety check --full-report --stdin

security-local-code:
	bandit .

security-docker:
	trivy image --severity HIGH ${DOCKER_IMAGE}

