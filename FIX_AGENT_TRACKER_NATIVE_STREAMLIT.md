# Agent Tracker Native Streamlit Fix

## Problem
The agent execution tracker was displaying raw HTML such as `<div style=...>` instead of rendered cards.

## Root cause
The previous tracker used a large multiline HTML string inside `st.markdown(..., unsafe_allow_html=True)`. Because of indentation/Markdown handling, Streamlit rendered the HTML as text/code instead of cards.

## Fix
Replaced the raw HTML tracker with native Streamlit components:

- `st.progress()` for the execution progress bar
- `st.columns()` for wrapped cards, three per row on wide screens
- `st.info()`, `st.warning()`, and `st.success()` for Waiting, Running, and Complete states

## Updated file
- `frontend/dashboard.py`

## Expected result
The tracker now renders as clean Streamlit status cards and will not run off the page or display raw HTML.
