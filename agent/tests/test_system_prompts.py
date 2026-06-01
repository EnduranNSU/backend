import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from agent.agent_backend.prompts.system_prompts import (
    user_inquire_system_prompt,
    create_training_prompt,
    exercise_prompt,
)


def test_user_inquire_prompt_is_nonempty():
    assert len(user_inquire_system_prompt) > 100


def test_user_inquire_prompt_mentions_rag():
    assert "RAG" in user_inquire_system_prompt


def test_user_inquire_prompt_covers_key_topics():
    for topic in ["цель", "уровень", "ограничения", "оборудование"]:
        assert topic in user_inquire_system_prompt


def test_create_training_prompt_mentions_catalog():
    assert "get_exercise_catalog" in create_training_prompt


def test_create_training_prompt_contains_json_marker():
    assert "<TRAINING_JSON>" in create_training_prompt
    assert "</TRAINING_JSON>" in create_training_prompt


def test_create_training_prompt_json_has_required_fields():
    for field in ["title", "perfomable_exercises", "exercise_id", "sets", "weight", "repetitions", "rest_duration"]:
        assert field in create_training_prompt


def test_exercise_prompt_has_placeholders():
    assert "{exercise_title}" in exercise_prompt
    assert "{exercise_description}" in exercise_prompt


def test_exercise_prompt_formats_correctly():
    filled = exercise_prompt.format(
        exercise_title="Приседания",
        exercise_description="Базовое упражнение на ноги"
    )
    assert "Приседания" in filled
    assert "Базовое упражнение на ноги" in filled
    assert "{exercise_title}" not in filled


def test_exercise_prompt_mentions_technique():
    assert "техник" in exercise_prompt.lower()
