> Gospodi pomiluy

### How to run
```
cd backend && pdm install && cd ..
docker compose up --build
cd backend && pdm run migrate && pdm run exercises
```

После этого все должно завестись. Любой последующий запуск должен осуществляться только
```
docker compose up
````

