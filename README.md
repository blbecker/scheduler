# Scheduling App


---
## Running
A development env can be started by running `docker-compose up -d` in the repo root. This will startup the api and database, with the api served on port 3000. Once the stack is started, an interactive terminal can be acquired with `docker compose exec api bash`. This will shell into the api container. From there, `go` and `buffalo` are available for development or testing. 

## Testing
From a terminal in the `api` container, `buffalo test` will refresh the test db and execute the tests. The test harness itself can be run from within Goland using a `docker-compose` target pointed at the `api` container. Running this way won't refresh the database, but that shouldn't always be necessary.
