from pydantic import BaseModel

from retriever.generator.collection_handler import CollectionHandler, CollectionEntry
from retriever.scripts.exercises import get_exercises

class Exercise(BaseModel):
    id: int
    title: str
    description: str
    video_href: str
    tags: list[str]


exercises_list = get_exercises()


ch = CollectionHandler("exercises")
for exercise in exercises_list:
    description = exercise.description.split("\n\n\n")

    technique = description[1]
    muscles = description[2]
    limitations = description[3]
    mistakes = description[4]
    alternatives = description[5]

    entries = [
        CollectionEntry(
            text = technique,
            payload = {
                "text": technique,
                "source": exercise.id,
                "tags": [exercise.title, "technique"]
            }
        ),

        CollectionEntry(
            text = muscles,
            payload = {
                "text": muscles,
                "source": exercise.id,
                "tags": [exercise.title, "muscles"]
            }
        ),

        CollectionEntry(
            text = limitations,
            payload = {
                "text": limitations,
                "source": exercise.id,
                "tags": [exercise.title, "limitations"]
            }
        ),

        CollectionEntry(
            text = mistakes,
            payload = {
                "text": mistakes,
                "source": exercise.id,
                "tags": [exercise.title, "mistakes"]
            }
        ),

        CollectionEntry(
            text = alternatives,
            payload = {
                "text": alternatives,
                "source": exercise.id,
                "tags": [exercise.title, "alternatives"]
            }
        ),
    ]

    ch.write_data(entries)
