all:
	docker build -t tars-discord .

run:
	docker run --env-file=.env tars-discord &> log.txt&