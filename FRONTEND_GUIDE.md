# Гайд для фронта

> Если ты — другой Клод, которому сказали "напиши фронт к этому", прочитай это до конца. Я уже потратил много токенов чтобы тебе было проще.

## TL;DR

- **Один URL для всего:** `http://localhost:8001` (gateway). Не ходи напрямую в `:8000`, `:9090`, `:8080`, `:8888`, `:9100` — они есть, но фронт должен ходить только в gateway.
- **Swagger UI:** `http://localhost:8001/docs` — там все REST-ручки с body/response, можно тыкать «Try it out» прямо из браузера.
- **OpenAPI JSON:** `http://localhost:8001/openapi.json` — оттуда можно сгенерить TS-типы (`openapi-typescript` или `orval`).
- **WebSocket для лайв-анализа приседа:** `ws://localhost:8001/cv/ws/squat`. **В Swagger UI его нет** (FastAPI не включает ws в openapi). Описание протокола ниже.
- **Auth:** OAuth2 password flow, JWT в `Authorization: Bearer <token>`.

## Поднять стек

```bash
docker compose up --build -d
```

Один раз. `setup_db` и `setup_qdrant` запускаются как init-контейнеры, всё накатывают, выходят, остальное стартует через `depends_on: service_completed_successfully`. Идемпотентно — перезапуски не дублируют данные.

Готовность: `docker compose ps` должен показать всё `Up`. Retriever тяжёлый на cold start (4 RAG-пайплайна с моделями загружаются — на CPU это 1-3 минуты).

## Запросы — что работает

| Метод | Путь | Auth | Что |
|---|---|---|---|
| POST | `/signup/` | — | `{name, email, password}` → создать юзера |
| POST | `/token` | — | OAuth2 form: `username=<email>&password=<pass>` → `{access_token, token_type}` |
| GET | `/user/` | Bearer | вернуть текущего юзера |
| GET | `/exercise/` | — | список упражнений (id, title, tags, hrefs) |
| GET | `/exercise/{id}` | — | + description (длинная строка из minio) |
| GET | `/measurements/` | Bearer | замеры юзера |
| POST | `/measurements/create` | Bearer | `{type, value: int, date: str}` — **value пока int**, не float |
| POST | `/measurements/update` | Bearer | массивом перетереть |
| GET | `/training/planned` | Bearer | список запланированных тренировок |
| GET | `/training/planned/{id}` | Bearer | одна |
| POST | `/training/planned/create` | Bearer | см. shape ниже |
| POST | `/training/planned/update/{id}` | Bearer | |
| POST | `/training/planned/delete/{id}` | Bearer | |
| GET | `/training/user_performed` | Bearer | то что юзер реально выполнил |
| POST | `/training/user_performed/create` | Bearer | + дата `{date: "YYYY-MM-DD", training: ...}` |
| POST | `/cv/analyze` | — | multipart `video=@file.mp4` → анализ приседа из готового файла |
| GET | `/cv/health` | — | проверка модели |
| POST | `/llm/v1/chat/completions` | — | OpenAI-совместимый, проксит в Yandex |
| POST | `/search/exercise/` | — | RAG поиск по упражнениям |
| POST | `/agent/exercise` | — | LLM-ответ про конкретное упражнение |
| POST | `/agent/tell_about` | — | свободный диалог с агентом |
| POST | `/agent/prepare_trainning` | — | построить план тренировки через LLM |

## Auth flow (нужно для всех Bearer-ручек)

```ts
// 1. signup (один раз)
await fetch("http://localhost:8001/signup/", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ name: "Иван", email: "i@v.ru", password: "secret" }),
});

// 2. login → получить токен
const form = new URLSearchParams({ username: "i@v.ru", password: "secret" });
const tokenResp = await fetch("http://localhost:8001/token", {
  method: "POST",
  body: form,  // НЕ JSON. OAuth2 password flow требует form-urlencoded.
});
const { access_token } = await tokenResp.json();
localStorage.setItem("token", access_token);

// 3. потом во все запросы:
const headers = { Authorization: `Bearer ${access_token}` };
```

Токен живёт N минут (по умолчанию из config). При 401 — редиректь на login.

## Формы (Pydantic-схемы — что слать)

### Тренировка (`/training/planned/create`)

```json
{
  "weekdays": ["MONDAY", "WEDNESDAY", "FRIDAY"],
  "training": {
    "title": "Ноги",
    "perfomable_exercises": [
      {
        "exercise_id": 1,
        "sets": [
          {"weight": 80, "repetitions": 8, "rest_duration": 120},
          {"weight": 80, "repetitions": 8, "rest_duration": 120},
          {"weight": 85, "repetitions": 6, "rest_duration": 150}
        ]
      }
    ]
  }
}
```

> Опечатка `perfomable_exercises` — это not typo в твоей голове, реально так в API. Не исправляй.

### Performed training (`/training/user_performed/create`)

Тот же `training` объект + `date: "YYYY-MM-DD"`.

### Measurement (`/measurements/create`)

```json
{ "type": "weight", "value": 75, "date": "2026-05-26" }
```

Поле `value` — **int**, не float. Если хочешь дробные веса — `value: 755` и трактовать как 0.1 кг, либо проси бэк поменять модель.

### Agent (`/agent/tell_about`)

```json
{
  "message": "что такое RPE?",
  "chat_id": "session-<uuid>",
  "user_id": 1,
  "user_token": "<JWT>"
}
```

`chat_id` — твой идентификатор сессии чата (стейт LangGraph хранится в памяти агента, при перезапуске агента — теряется). Сделай новый UUID на каждый «новый чат», переиспользуй на продолжении.

### RAG (`/search/exercise/`)

```json
{
  "rag_name": "exercises",
  "query": "как правильно делать тягу",
  "limit": 5,
  "tags": []
}
```

`rag_name` ∈ `exercises`, `ex_hyde`, `ex_cool`, `tag_first`. По умолчанию бери `exercises` (быстрая), `ex_hyde` качественная но дёргает LLM (медленнее, тратит quota).

### CV analyze (`/cv/analyze`)

```ts
const fd = new FormData();
fd.append("video", videoBlob, "squat.mp4");
const r = await fetch("http://localhost:8001/cv/analyze", { method: "POST", body: fd });
const report = await r.json();
// {
//   frames_total, frames_with_pose,
//   reps: [{ start_frame, end_frame, min_knee_angle, max_knee_collapse, deep_enough, knee_collapsed }],
//   avg_min_knee_angle, avg_knee_collapse,
//   knee_collapse_ratio, depth_ratio,
//   verdict: "Засчитано приседов: 3. Глубина в норме. Колени держишь стабильно."
// }
```

## WebSocket: live coaching (приседания)

**URL:** `ws://localhost:8001/cv/ws/squat`

(Или напрямую без gateway: `ws://localhost:9090/cv/ws/squat`.)

### Протокол

**client → server (binary):** JPEG frame, один кадр на `ws.send(buf)`.

**server → client (text JSON):**
```json
{
  "frame": 42,
  "detected": true,
  "knee_angle": 87.3,
  "knee_collapse": 0.012,
  "state": "down",
  "label": "OK",
  "hint": "глубина норм",
  "reps_total": 3,
  "last_rep_ok": true
}
```

| Поле | Что |
|---|---|
| `frame` | номер кадра (от 0) |
| `detected` | поймал ли позу |
| `knee_angle` | угол hip-knee-ankle в градусах. 180 = стоит, <100 = глубокий присед |
| `knee_collapse` | заваливание колена внутрь, нормализованное. >0.04 = плохо |
| `state` | `up` (стоит) / `down` (приседает) |
| `label` | `OK` / `BAD` / `IDLE` — что красить в UI |
| `hint` | человекочитаемая подсказка |
| `reps_total` | счётчик завершённых повторений |
| `last_rep_ok` | bool / null — был ли последний rep чистым |

**client → server (text JSON):** управление
```json
{ "cmd": "reset" }
```
сбрасывает счётчик и стейт (для нового подхода).

### Минимальный фронт-код

```tsx
import { useEffect, useRef, useState } from "react";

export function SquatCoach() {
  const videoRef = useRef<HTMLVideoElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const [reps, setReps] = useState(0);
  const [label, setLabel] = useState<"OK" | "BAD" | "IDLE">("IDLE");
  const [hint, setHint] = useState("");

  useEffect(() => {
    let cancelled = false;
    let interval: number | undefined;

    (async () => {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480 },
      });
      if (cancelled) return;
      videoRef.current!.srcObject = stream;
      await videoRef.current!.play();

      const ws = new WebSocket("ws://localhost:8001/cv/ws/squat");
      ws.binaryType = "arraybuffer";
      wsRef.current = ws;

      ws.onmessage = (e) => {
        const r = JSON.parse(e.data);
        if (r.error) return;
        setReps(r.reps_total ?? 0);
        setLabel(r.label ?? "IDLE");
        setHint(r.hint ?? "");
      };

      ws.onopen = () => {
        const canvas = document.createElement("canvas");
        const ctx = canvas.getContext("2d")!;
        interval = window.setInterval(() => {
          if (ws.readyState !== WebSocket.OPEN) return;
          const v = videoRef.current!;
          canvas.width = v.videoWidth;
          canvas.height = v.videoHeight;
          ctx.drawImage(v, 0, 0);
          canvas.toBlob(
            (b) => b && b.arrayBuffer().then((buf) => ws.send(buf)),
            "image/jpeg",
            0.7
          );
        }, 100); // 10 FPS — достаточно
      };
    })();

    return () => {
      cancelled = true;
      if (interval) clearInterval(interval);
      wsRef.current?.close();
    };
  }, []);

  const reset = () => wsRef.current?.send(JSON.stringify({ cmd: "reset" }));

  const color = label === "OK" ? "lime" : label === "BAD" ? "red" : "gray";
  return (
    <div>
      <video ref={videoRef} style={{ border: `4px solid ${color}` }} />
      <h2>Повторов: {reps}</h2>
      <p>{hint}</p>
      <button onClick={reset}>Новый подход</button>
    </div>
  );
}
```

### Важно

- **JPEG quality 0.5–0.7** хватает, не шли 0.9 — это в 3 раза больше байт без выигрыша по точности позы.
- **10 FPS** — оптимум. 30 FPS не даёт точнее, только грузит CPU на бэке.
- **640x480** — нормальный размер. Больше — сильнее CPU, не точнее.
- WS **stateful per connection**: открыл — пошёл подход, закрыл — счётчик сбросится. Для пауз используй `{cmd: "reset"}` без переподключения.
- Бэк сейчас умеет **только squat**. Если в URL подставить `/cv/ws/curl` — вернёт `{error, supported}` и закроет. Когда добавлю новые упражнения — список в `cv_service/src/cv_service/routers/ws.py:_SUPPORTED_EXERCISES`.

## Что есть в проекте сейчас (для контекста)

```
backend_cv/
├── docker-compose.yml           # один up поднимает всё
├── .env                         # YANDEX_API_KEY, LLM_PROVIDER
├── backend/                     # FastAPI: auth, users, exercises, training, measurements (Postgres + minio)
├── retriever/ (rag/)            # FastAPI: RAG по упражнениям (Qdrant + sentence-transformers)
├── agent/                       # FastAPI + langgraph: LLM-агент с тулзами
├── llm/                         # Тонкий OpenAI-совместимый прокси → Yandex/OpenAI/Ollama (LLM_PROVIDER env)
├── cv_service/                  # FastAPI: pose detection (mediapipe) + live WS
├── gateway/                     # FastAPI: проксит всё на :8001, агрегирует openapi для /docs
└── experiments/                 # ноутбуки + тестовые видео приседаний
```

## Генерация типов

```bash
npx openapi-typescript http://localhost:8001/openapi.json -o src/api/types.ts
```

Дальше любой клиент: orval, openapi-fetch, ts-rest, что хочешь.

## CORS

Сейчас CORS-middleware **не настроен**. Если фронт на `:5173` (vite), а бэк на `:8001`, в браузере получишь CORS ошибку. Поправь в `gateway/src/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

Это первое что надо сделать перед началом фронта.

## Известные подводные камни

1. **`MeasurementBase.value: int`** — нельзя слать `75.5`. Либо int, либо проси бэк поменять.
2. **`weekdays`** — список строк, формат не валидируется. Договорись с собой: `MONDAY`/`TUESDAY`/.../`SUNDAY`.
3. **`agent.chat_id`** — стейт в RAM агента, при `docker compose restart agent` теряется. Не критично для MVP.
4. **Yandex LLM** — chat работает, embedding не нужен (sentence-transformers локально). Если ключ протухнет — 401 на `/agent/*` и `/search/*` (с HyDE).
5. **WebSocket не в Swagger** — это норма для FastAPI. Документация здесь, в гайде.
6. **CV cold start** — первый `/cv/analyze` или первый WS-кадр греет mediapipe-граф, ~3 сек. Второй уже быстро.
