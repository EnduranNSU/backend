> Gospodi pomiluy

### How to run

```
docker compose up --build
```

Всё. `setup_db` и `setup_qdrant` поднимаются как init-контейнеры, накатывают миграции/упражнения, выходят, остальные сервисы ждут их через `depends_on: service_completed_successfully`. Скрипты идемпотентные — перезапуски ничего не ломают.

### Сервисы и порты
- `gateway`     `:8001` — единая точка входа для фронта (проксит всё ниже)
- `backend`     `:8000` — auth/users/exercises/training/measurements
- `retriever`   `:8888` — RAG по упражнениям
- `agent`       `:8080` — LLM-агент
- `cv_service`  `:9090` — `POST /cv/analyze` (видео приседа → метрики)
- `db`          `:5432`, `minio` `:9000/9001`, `qdrant` `:6333/6334`

### Через gateway (`http://localhost:8001`)
- `/token`, `/signup`, `/user`, `/exercise`, `/training`, `/measurements` → backend
- `/search/exercise`, `/search/user` → retriever (префикс `/search` срезается)
- `/agent/*` → agent
- `/cv/*` → cv_service
