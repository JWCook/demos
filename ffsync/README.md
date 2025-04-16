# Self-hosted Firefox sync

Example of setting up self-hosted Firefox sync ([syncstorage-rs](https://github.com/mozilla-services/syncstorage-rs)) using [syncstorage-rs-docker](https://github.com/dan-r/syncstorage-rs-docker)

# Prerequisites
* [Docker compose](https://docs.docker.com/compose/install/)

# Server setup
```sh
cp example.env .env
docker compose up -d --build
```

# Browser setup
* Set custom sync URI:
   * Option 1: Go to [about:config](about:config) and set `identity.sync.tokenserver.uri` to `http://localhost:8446/1.0/sync/1.5`
   * Option 2 (LibreWolf only): [`librewolf.overrides.cfg`](https://librewolf.net/docs/settings/):
    ```sh
    ln -s $(pwd)/librewolf.overrides.cfg ~/.librewolf/librewolf.overrides.cfg
    ```
* Go to Settings -> Sync -> log in
* Verify sync:
    * Set `services.sync.log.appender.file.logOnSuccess` to `true`
    * Go to [about:sync-log](about:sync-log)
