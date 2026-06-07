#!/usr/bin/env python3
"""
Hermes Agent callback integration example.

This shows how to use Gimme's cli_input() as a fallback when
no native GUI is available (headless VPS, SSH session, etc.).

Usage:
    python examples/hermes_callback.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_server import cli_input


def clarify_callback(question, choices=None, fields=None):
    """
    Hermes-style clarify callback with fields support.
    
    Args:
        question: The question text to display
        choices: Up to 4 predefined options (mutually exclusive with fields)
        fields: Up to 8 field definitions for a multi-field form
    
    Returns:
        If choices mode: string (selected choice or user-typed answer)
        If fields mode: dict of {field_name: user_value}
    """
    if fields:
        # Multi-field form mode
        schema = {"title": question, "fields": fields}
        return cli_input(schema)
    elif choices:
        # Simple choice mode (up to 4 options)
        sys.stderr.write(f"\n{question}\n")
        for i, c in enumerate(choices, 1):
            sys.stderr.write(f"  {i}: {c}\n")
        sys.stderr.write(f"Enter 1-{len(choices)} or type answer: ")
        sys.stderr.flush()
        val = sys.stdin.readline().strip()
        if val.isdigit() and 1 <= int(val) <= len(choices):
            return choices[int(val) - 1]
        return val
    else:
        # Open-ended question
        sys.stderr.write(f"\n{question}: ")
        sys.stderr.flush()
        return sys.stdin.readline().strip()


# Example usage
if __name__ == "__main__":
    # Example 1: Simple choice
    print("=== Example 1: Simple Choice ===")
    result = clarify_callback(
        "What's your preferred deployment environment?",
        choices=["staging", "production", "development"]
    )
    print(f"Selected: {result}\n")
    
    # Example 2: Multi-field form
    print("=== Example 2: Multi-Field Form ===")
    result = clarify_callback(
        "Log your workout set",
        fields=[
            {"name": "exercise", "type": "select", "label": "Exercise",
             "options": ["Leg Press", "Calf Extension", "Machine Chest Press"],
             "default": "Leg Press"},
            {"name": "sets", "type": "number", "label": "Sets", "default": 3},
            {"name": "reps", "type": "number", "label": "Reps", "default": 10},
            {"name": "weight", "type": "number", "label": "Weight (lbs)", "default": 225}
        ]
    )
    print(f"Result: {result}")
