"""Shared type aliases matching the Louie server models."""

from typing import Literal

ShareMode = Literal["Public", "Private", "Organization"]
UserAgent = Literal["API", "Louie"]
