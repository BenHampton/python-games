"""Top-level control-mode state machine.

Tracks what the player is currently controlling so input handling, the active camera,
and which entity updates can all be routed through one place. Today it only
distinguishes driving the boat (`HELM`) from walking on foot (`ON_FOOT`); `MENU` is
reserved for future docked/town UI. This generalizes the ad-hoc `console.active`
input gating.
"""

HELM = "helm"
ON_FOOT = "on_foot"
MENU = "menu"


class GameState:
    def __init__(self, mode=HELM):
        self.mode = mode

    def is_helm(self):
        return self.mode == HELM

    def is_on_foot(self):
        return self.mode == ON_FOOT

    def is_menu(self):
        return self.mode == MENU

    def to_helm(self):
        self.mode = HELM

    def to_on_foot(self):
        self.mode = ON_FOOT

    def to_menu(self):
        self.mode = MENU

    def toggle_helm_foot(self):
        """Switch between driving and walking; returns the new mode."""
        self.mode = ON_FOOT if self.mode == HELM else HELM
        return self.mode
