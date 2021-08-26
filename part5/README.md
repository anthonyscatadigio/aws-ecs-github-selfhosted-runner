# Part 5 - Sample Docker Image

Simple docker image to be deployed into ECS for testing ECS github docker build and deployment.
This will be build by the GitHub runner.

## Build Image

```bash
docker build -t sample_nginx .
```

## Run Image

```bash
docker run --rm -d -p 80:80 sample_nginx
```

View the output

```bash
curl localhost:80
```

## Stop container

```bash
docker stop $(docker ps -a -q  --filter ancestor=sample_nginx)
```
