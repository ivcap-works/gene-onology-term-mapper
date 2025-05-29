SERVICE_TITLE=Gene Ontology (GO) Term Mapper
SERVICE_NAME=gene-ontology-term-mapper

IVCAP_SERVICE_FILE=service.json

PROJECT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PORT=8077
SERVICE_URL=http://localhost:${PORT}

#include Makefile.common

run:
	poetry ivcap run -- --port ${PORT}

TEST_REQUEST=two_bp.json
test-local:
	curl -X POST \
		-H "content-type: application/json" \
		-H "timeout: 60" \
		--data @${TEST_REQUEST} \
		http://localhost:${PORT}

SERVICE_ID=$(shell poetry ivcap --silent get-service-id)
test-job: IVCAP_API=https://develop.ivcap.net
test-job:
	TOKEN=$(shell ivcap context get access-token --refresh-token); \
	curl \
	-X POST \
	-H "content-type: application/json" \
	-H "Timeout: 20" \
	-H "Authorization: Bearer $$TOKEN" \
	--data @${TEST_REQUEST} \
	${IVCAP_API}/1/services2/${SERVICE_ID}/jobs?with-result-content=true | jq

JOB_ID=6a75971d-5467-4fd4-bfae-cbf23efd41a5
ivcap-result:
	curl \
		-H "Authorization: Bearer $(shell ivcap context get access-token --refresh-token)" \
		-H "Timeout: ${TIMEOUT}" \
		${IVCAP_API}/1/services2/${SERVICE_ID}/jobs/${JOB_ID}?with-result-content=false | jq

test-job-minikube:
	@$(MAKE) IVCAP_API=http://ivcap.minikube test-job

test-job-ivcap:
	@$(MAKE) IVCAP_API=https://develop.ivcap.net test-job

docker-build:
	poetry ivcap docker-build

docker-run:
	poetry ivcap docker-run -- --port ${PORT}

docker-debug: #docker-build
	docker run -it \
		-p 8888:8080 \
		--user ${DOCKER_USER} \
		--platform=linux/${TARGET_ARCH} \
		--entrypoint bash \
		${DOCKER_NAME}_${TARGET_ARCH}


.PHONY: run
