import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from agent.agent_backend.prompts.system_prompts import (
    user_inquire_system_prompt,
    create_training_prompt,
    exercise_prompt,
    MEMORY_RULES,
)


# ─── MEMORY_RULES: the shared preamble that drives user-RAG behaviour ────────

def test_memory_rules_mentions_both_tools():
    assert "user_rag_download" in MEMORY_RULES
    assert "user_rag_upload" in MEMORY_RULES


def test_memory_rules_demands_explicit_recall():
    # Memory has to be VISIBLE to the user.
    assert "Помню" in MEMORY_RULES


def test_memory_rules_lists_save_triggers():
    for trigger in ["травмы", "цели", "опыт", "оборудование", "предпочтения"]:
        assert trigger in MEMORY_RULES


# ─── Every scenario prompt must inherit memory rules ────────────────────────

def test_user_inquire_prompt_contains_memory_rules():
    assert MEMORY_RULES in user_inquire_system_prompt


def test_create_training_prompt_contains_memory_rules():
    assert MEMORY_RULES in create_training_prompt


def test_exercise_prompt_contains_memory_rules():
    assert MEMORY_RULES in exercise_prompt


# ─── Original sanity checks (kept) ───────────────────────────────────────────

def test_user_inquire_prompt_is_nonempty():
    assert len(user_inquire_system_prompt) > 100


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


def test_create_training_prompt_demands_memory_lookup():
    # Training-builder must check user memory BEFORE picking exercises.
    assert "user_rag_download" in create_training_prompt


def test_exercise_prompt_has_placeholders():
    assert "{exercise_title}" in exercise_prompt
    assert "{exercise_description}" in exercise_prompt


def test_exercise_prompt_formats_correctly():
    filled = exercise_prompt.format(
        exercise_title="Приседания",
        exercise_description="Базовое упражнение на ноги",
    )
    assert "Приседания" in filled
    assert "Базовое упражнение на ноги" in filled
    assert "{exercise_title}" not in filled


def test_exercise_prompt_mentions_technique():
    assert "техник" in exercise_prompt.lower()


def test_exercise_prompt_demands_memory_lookup():
    assert "user_rag_download" in exercise_prompt
