"""
Centralized model routing.

Instead of each agent hardcoding its own model name, every agent imports its
model from here. This makes swapping models a single-line edit instead of
hunting through every agent file - useful for the live review where they may
ask you to change routing logic in real time.

--- Routing reasoning (also goes in README) ---

Image Analyser (13 calls, one per photo): FLASH_LITE
  High call volume, task is close to structured classification/description -
  doesn't need the strongest reasoning. Flash-Lite is cheaper with a much
  higher free-tier daily quota, which matters a lot at this call volume.

Intent Parser (1 call): FLASH_LITE (dev) / would use FLASH in production
  Simple, low-ambiguity extraction task from a short prompt.

Storyboard Writer (1 call): FLASH_LITE (dev) / would use FLASH in production
  Most creatively demanding node - image selection, narrative flow, style
  guide adherence. Would get the strongest available model in production.

Script Generator (1-N calls, N = retry count): FLASH_LITE (dev) / FLASH in prod
  Code generation benefits from a stronger model, and cost compounds across
  retries, so this matters more at scale.

NOTE: Gemini's free tier currently caps gemini-2.5-flash at 20 requests/day
per project - too low for iterating on a 5-agent pipeline. All nodes are set
to FLASH_LITE below to keep development unblocked. The table still reflects
intended production reasoning; switching creative nodes back to FLASH is a
one-line edit once billing is enabled.
"""

FLASH_LITE = "gemini-2.5-flash-lite"
FLASH = "gemini-2.5-flash"

MODEL_ROUTING = {
    "image_analyser": FLASH_LITE,
    "intent_parser": FLASH_LITE,
    "storyboard_writer": FLASH_LITE,
    "script_generator": FLASH_LITE,
    "compiler_fixer": FLASH_LITE,
}