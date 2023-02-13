.PHONY: dev
dev:
	USER=`id -u` docker compose up app

.PHONY: stage
stage:
	USER=1000 sudo docker-compose up --force-recreate -d

.PHONY: prod
app:
	USER=1000 sudo docker-compose up --force-recreate -d

.PHONY: install
install:
	python -m pip install -r requirements.txt

.PHONY: update
update-reqs:
	python -m pip install -U -r requirements.in
	python -m pip freeze > requirements.txt

.PHONY: docker
docker:
	docker build -t apiad/matcom-dashboard:latest .

.PHONY: shell
shell:
	USER=`id -u` docker compose run app bash

.PHONY: root
root:
	USER=0 docker compose run app bash

.PHONY: update
update:
	USER=0 docker compose run app make update-reqs
	make docker

.PHONY: sync
sync:
	git add data/*.yaml
	git commit -m "Update data" || echo "Nothing to commit"
	git pull --no-edit && make app
	git push
