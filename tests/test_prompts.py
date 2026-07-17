"""Tests that the prompt states its rules and renders the profile."""

from app import prompts


def test_render_profile_includes_the_key_facts(profile):
    text = prompts.render_profile(profile)
    assert "18" in text
    assert "low" in text
    assert "vegetarian" in text.lower()
    assert "ironman" in text.lower()


def test_system_prompt_states_its_boundaries():
    text = prompts.SYSTEM_PROMPT
    lowered = text.lower()
    assert "never diagnose" in lowered
    assert "search_research" in text
    assert "search_products" in text


def test_system_instruction_combines_prompt_and_profile(profile):
    text = prompts.system_instruction(profile)
    assert prompts.SYSTEM_PROMPT in text
    assert prompts.render_profile(profile) in text
