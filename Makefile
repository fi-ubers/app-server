SRC = config/doxygen
DOXYGEN_CONFIG = doxygen_config
DOXYGEN_DOCS =  ${CURDIR}/docs
DOC_FOLDER = documentation

DOCKER_NAME = app-server-img
DOCKER_CONTAINER_NAME = app-server
DOCKER_FLAGS = --name ${DOCKER_CONTAINER_NAME} -p 27017:27017 -p 5000:8000

GUNICORN_BIND = 8000


run: logs/mylog.log
	@echo "Make sure mongod service is running (sudo service mongod start)"
	@export GUNICORN_BIND=${GUNICORN_BIND}
	gunicorn --config config/gunicorn.conf --log-config config/logging.conf src.main.wsgi


# Create directory for log files if it does not exists
logs/mylog.log:
	@mkdir logs -p
	@touch mylog.log

document:
	rm -f -r ${CURDIR}/docs/documentation
	mkdir -p docs/documentation
	doxygen $(SRC)/$(DOXYGEN_CONFIG)

test:
	py.test --cov-report html --cov=src.main src/test/ --verbose


docker_build:
	docker build -t ${DOCKER_NAME} .

docker_run:
	docker run -d ${DOCKER_FLAGS} ${DOCKER_NAME} 

docker_stop:
	docker stop ${DOCKER_CONTAINER_NAME}
	docker container rm ${DOCKER_CONTAINER_NAME}

clean:
	cd src
	find . -name "*.pyc" -delete


.PHONY: document, run, clean, test
	

