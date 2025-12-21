from os import listdir
from pydantic import BaseModel

class Exercise(BaseModel):
    id: int
    title: str
    description: str
    video_href: str
    tags: list[str]

exercises = []


title_mapping = {
    "barbell_bent-over_row": "Тяга штанги в наклоне",
    "barbell_squat": "Приседания со штангой",
    "bench_press": "Жим лёжа",
    "bulgarian_squats": "Болгарский сплит-присед",
    "deadlift": "Становая тяга",
    "glute_bridge": "Ягодичный мост",
    "hanging_leg_raises": "Подъём ног с наклоном корпуса",
    "lat_pulldown": "Тяга верхнего блока к груди",
    "lungs": "Выпады вперёд / назад",
    "lying_leg_raises": "Подъём ног лёжа",
    "machine_row": "Горизонтальная тяга в блоке",
    "one-arm_dumpbell_row": "Тяга гантели одной рукой",
    "plank": "Планка",
    "pull_ups": "Подтягивания",
    "romanian_deadlift": "Румынская становая тяга",
    "russian_twists": "Русские скручивания",
    "side_plank": "Боковая планка",
}

tags = [
    "core", "back", "arms", "chest", "legs",
    "shoulders", "glutes", "hamstrings", "quadriceps",
    "lower_back", "upper_back",
    "machine", "free-weight", "bodyweight",
    "pull", "push", "hinge", "squat", "lunge",
    "stability"
]

exercise_tags = {
    "barbell_bent-over_row": [
        "back", "upper_back", "arms", "free-weight", "pull"
    ],
    "barbell_squat": [
        "legs", "quadriceps", "glutes", "core", "free-weight", "squat"
    ],
    "bench_press": [
        "chest", "arms", "shoulders", "free-weight", "push"
    ],
    "bulgarian_squats": [
        "legs", "quadriceps", "glutes", "core", "free-weight", "lunge"
    ],
    "deadlift": [
        "legs", "glutes", "hamstrings", "lower_back", "core", "free-weight", "hinge"
    ],
    "glute_bridge": [
        "glutes", "hamstrings", "core", "free-weight", "hinge"
    ],
    "hanging_leg_raises": [
        "core", "bodyweight", "pull"
    ],
    "lat_pulldown": [
        "back", "upper_back", "arms", "machine", "pull"
    ],
    "lungs": [
        "legs", "quadriceps", "glutes", "core", "free-weight", "lunge"
    ],
    "lying_leg_raises": [
        "core", "bodyweight"
    ],
    "machine_row": [
        "back", "upper_back", "arms", "machine", "pull"
    ],
    "one-arm_dumpbell_row": [
        "back", "upper_back", "arms", "free-weight", "pull"
    ],
    "plank": [
        "core", "stability", "bodyweight"
    ],
    "pull_ups": [
        "back", "upper_back", "arms", "bodyweight", "pull"
    ],
    "romanian_deadlift": [
        "legs", "glutes", "hamstrings", "lower_back", "core", "free-weight", "hinge"
    ],
    "russian_twists": [
        "core", "bodyweight"
    ],
    "side_plank": [
        "core", "stability", "bodyweight"
    ],
}


counter = 0
for file in listdir("./texts"):
    if file.startswith("_"):
        continue
    with open(f"./texts/{file}", "r", encoding="utf-8") as f:
        exercises.append(Exercise(
            id=counter,
            title=title_mapping[file.split(".")[0]],
            description=f.read(),
            video_href="",
            tags=exercise_tags[file.split(".")[0]]
        ))

    counter += 1

import json

exercises = [ex.model_dump_json() for ex in exercises]

with open("./exercises.json", "w", encoding="utf-8") as f:
    json.dump(exercises, f, ensure_ascii=False)
    