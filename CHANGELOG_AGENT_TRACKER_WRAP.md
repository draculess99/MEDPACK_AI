# Agent Tracker UI Wrap Fix

This patch improves the MedPack AI committee execution display.

## Problem fixed

The agent status lights were displayed in one long horizontal row with `white-space: nowrap`, which could run off the right side of the page on normal screens.

## What changed

- Replaced the one-line agent light bar with a responsive `Agent Execution Tracker`.
- Agent statuses now render as wrapped cards in a CSS grid.
- Added a progress bar showing how many agents have completed.
- Added a current-agent label.
- Added a small step-by-step delay so the agent execution is visible without feeling stuck.

## Updated file

- `frontend/dashboard.py`

## Expected result

When you click `Run MedPack Committee Decision`, the agent execution panel should stay inside the page width and wrap cleanly across rows instead of overflowing off-screen.
