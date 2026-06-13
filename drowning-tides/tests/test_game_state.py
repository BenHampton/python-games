from drowning_tides.core.game_state import HELM, ON_FOOT, GameState


def test_default_mode_is_helm():
    gs = GameState()
    assert gs.is_helm()
    assert not gs.is_on_foot()


def test_toggle_flips_helm_and_foot():
    gs = GameState()
    assert gs.toggle_helm_foot() == ON_FOOT
    assert gs.is_on_foot()
    assert gs.toggle_helm_foot() == HELM
    assert gs.is_helm()


def test_explicit_transitions():
    gs = GameState()
    gs.to_on_foot()
    assert gs.mode == ON_FOOT
    gs.to_menu()
    assert gs.is_menu()
    gs.to_helm()
    assert gs.is_helm()
