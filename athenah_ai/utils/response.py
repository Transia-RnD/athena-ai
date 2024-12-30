#!/usr/bin/env python
# coding: utf-8


def remove_code_fences(value: str) -> int:
    value = value.replace(" ", "").strip()
    return value.replace("```json", "").replace("```", "")
