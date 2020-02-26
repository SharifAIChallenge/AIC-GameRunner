# Installation

## Install Dependencies

You can use ansible playbooks (master.yml) written in: [AIC-GameRunnerManager](https://github.com/SharifAIChallenge/AIC-GameRunnerManager)

Then configure host postgres to be accessible inside docker container network  
(hint: configure postgres to listen 172.17.0.1 also add network ip range to pg_hba.conf)

Finally reconfigure `game_runner/settings.py` in following parts:
1. `DATABASE` to host postgres
2. `DOCKER_REGISTRY_*` to docker registry
3. `MANAGER_IMAGE` to docker registery manager image like `example.com/aic_manager_image`
4. `SITE_URL` to aichallenge site url for report runs

## Start Project
```
docker-compose -f docker-compose.yml up -d --build --remove-orphans
```

Note: development contains psql itself:
```
docker-compose up -d --build --remove-orphans
```

