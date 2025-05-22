SERVICE_TITLE=Gene Ontology (GO) Term Mapper
SERVICE_NAME=gene-ontology-term-mapper

IVCAP_SERVICE_FILE=service.json

PROJECT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PORT=8077
SERVICE_URL=http://localhost:${PORT}

include Makefile.common

run:
	env VERSION=$(VERSION) \
		poetry run python ${PROJECT_DIR}/service.py --port ${PORT}

TEST_REQUEST=tests/two_bp.json
test-local:
	curl -X POST \
		-H "content-type: application/json" \
		-H "timeout: 60" \
		--data @${TEST_REQUEST} \
		http://localhost:${PORT} | jq

test-job: IVCAP_API=https://develop.ivcap.net
test-job:
	TOKEN=$(shell ivcap context get access-token --refresh-token); \
	curl \
	-X POST \
	-H "content-type: application/json" \
	-H "Timeout: 20" \
	-H "Authorization: Bearer $$TOKEN" \
	--data "{\"number\": 997}" \
	${IVCAP_API}/1/services2/${SERVICE_ID}/jobs?with-result-content=true | jq

test-job-minikube:
	@$(MAKE) IVCAP_API=http://ivcap.minikube test-job

test-job-ivcap:
	@$(MAKE) IVCAP_API=https://develop.ivcap.net test-job

install:
	pip install -r requirements.txt

docker-run: #docker-build
	docker run -it \
		-p ${PORT}:${PORT} \
		--platform=linux/${TARGET_ARCH} \
		--rm \
		${DOCKER_NAME}_${TARGET_ARCH} --port ${PORT}

docker-debug: #docker-build
	docker run -it \
		-p 8888:8080 \
		--user ${DOCKER_USER} \
		--platform=linux/${TARGET_ARCH} \
		--entrypoint bash \
		${DOCKER_NAME}_${TARGET_ARCH}


.PHONY: run
