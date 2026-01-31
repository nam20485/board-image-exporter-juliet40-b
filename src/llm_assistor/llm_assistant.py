"""
llm_assistant.py
-----------------

This module provides a pluggable interface for generating natural
language explanations and fix suggestions for board validation errors
using a local large‑language model (LLM). It includes a simple base
class and a stub implementation backed by ONNX Runtime. In a real
system, the ONNX engine would load an int4/int8 quantized model that
can run efficiently on CPU or hardware accelerators such as Apple's
Core ML (via the ONNX Runtime execution provider). The stub returns
deterministic results for demonstration purposes.

The assistant generates output adhering to a strict JSON schema to
facilitate consumption by the CLI and to enable guardrails. Each
explanation includes a summary of the problem, a likely cause, a list
of fix steps, a candidate patch (list of RFC6902 operations), a
confidence score, and a boolean indicating if human review is
required.
"""

from __future__ import annotations

from typing import Any, Protocol

from validator import ValidationError


class LlmEngine(Protocol):
    """Interface for LLM engines.

    Any engine must implement the `generate_json` method which takes a
    system prompt and a user prompt and returns a Python dictionary.
    """

    def generate_json(
        self, system_prompt: str, user_prompt: str
    ) -> dict[str, Any]: ...  # pragma: no cover


class NoopEngine:
    """A fallback engine that returns an empty response.

    This engine can be used when no LLM is available. It returns an
    empty dictionary which the caller must interpret accordingly.
    """

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        return {}


class OnnxRuntimeEngine:
    """An example ONNX Runtime based engine.

    In a production setting, this class would load a quantized model
    converted to ONNX format and run inference using the best available
    execution provider (CPU, CUDA, or CoreML). This stub implementation
    returns a deterministic explanation for demonstration purposes.
    """

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        try:
            import onnxruntime as ort  # type: ignore

            self.ort = ort
        except ImportError:
            # We cannot import ONNX Runtime in this environment; fall back
            self.ort = None

    def generate_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        """Generate a JSON response for the given prompts.

        Args:
            system_prompt: A string describing assistant behavior.
            user_prompt: The user input containing errors and context.

        Returns:
            A dictionary with explanation, fix steps, and patch suggestions.

        Note:
            This stub does not perform any true inference. It returns
            static messages to illustrate the expected shape of the result.
        """
        # In a real implementation, you would tokenize the prompt and run it
        # through the ONNX model session. Here we simulate a response.
        return {
            "summary": "Validation errors were detected in the board design.",
            "likely_cause": (
                "Some fields contain invalid numeric values or violate design constraints."
            ),
            "fix_steps": [
                "Review each error and ensure numeric fields are positive.",
                "Adjust via hole sizes so they are smaller than their diameters.",
                "Re‑run validation to confirm issues are resolved.",
            ],
            "proposed_patch": [],  # this stub never proposes a patch
            "confidence": 0.5,
            "needs_human_review": True,
        }


def explain_errors(
    errors: list[ValidationError],
    board_info: dict[str, Any] | None = None,
    engine: LlmEngine | None = None,
) -> list[dict[str, Any]]:
    """Generate explanations for a list of validation errors.

    Args:
        errors: A list of ValidationError objects produced by `validator.validate_board`.
        board_info: Optional dictionary with additional board metadata "
        "(unused here but kept for future use).
        engine: An LlmEngine to produce the explanation. If None, defaults to OnnxRuntimeEngine.

    Returns:
        A list of explanation dictionaries corresponding one‑to‑one with the input errors. Each
        explanation conforms to the schema described in the module docstring.
    """
    if engine is None:
        engine = OnnxRuntimeEngine()

    explanations: list[dict[str, Any]] = []
    for err in errors:
        # Construct a specific user prompt for each error
        user_prompt = (
            f"Error code: {err['code']}. Message: {err['message']}. "
            f"Json path: {err['json_path']}. "
            "Provide a concise human explanation, likely cause, fix steps, "
            "and a proposed JSON patch if possible."
        )
        system_prompt = (
            "You are a helpful board design assistant. You receive structured "
            "validation errors and must explain them clearly. Return your response "
            "as JSON with keys summary, likely_cause, fix_steps, proposed_patch, "
            "confidence, and needs_human_review. If you cannot propose a fix, leave "
            "proposed_patch empty."
        )
        response = engine.generate_json(system_prompt, user_prompt)
        # Validate response structure and fill missing fields with defaults
        explanation = {
            "code": err["code"],
            "summary": response.get("summary", "No explanation provided."),
            "likely_cause": response.get("likely_cause", "Unknown cause."),
            "fix_steps": response.get("fix_steps", []),
            "proposed_patch": response.get("proposed_patch", []),
            "confidence": float(response.get("confidence", 0.0)),
            "needs_human_review": bool(response.get("needs_human_review", True)),
        }
        explanations.append(explanation)
    return explanations


def suggest_patch(errors: list[ValidationError], board: dict[str, Any]) -> list[dict[str, Any]]:
    """Heuristically suggest a list of JSON patch operations to fix errors.

    This function does not use an LLM. Instead, it encodes a small set of
    heuristic fixes for known error codes. If multiple errors refer to the
    same field, only the last suggestion is kept.

    Args:
        errors: The list of validation errors.
        board: The board data as a Python dictionary.

    Returns:
        A list of JSON patch operations (RFC6902) that may fix some errors.
    """
    patch_ops: dict[str, dict[str, Any]] = {}
    for err in errors:
        code = err["code"]
        path = err["json_path"]
        # Heuristic fix for negative trace width: set to a default positive value
        if code == "trace.width.negative":
            # Determine a sensible width: choose 0.1 mm (or 4 mil) regardless of units
            new_value = 0.1
            patch_ops[path] = {"op": "replace", "path": path, "value": new_value}
        # Heuristic fix for via hole >= diameter: shrink hole to half of diameter
        elif code == "via.hole.exceeds_diameter":
            # Evaluate current diameter from board data
            # Remove leading '/' from path to navigate dictionary
            parts = path.lstrip("/").split("/")  # e.g., ["vias", "via1"]
            # Attempt to read current diameter
            current_via = board
            try:
                for p in parts:
                    current_via = current_via[p]
            except Exception:
                current_via = None
            # If diameter is available, set hole to half of diameter
            try:
                diameter = float(current_via.get("diameter"))
                new_value = diameter / 2.0
                # Path to hole field
                hole_path = f"{path}/hole"
                patch_ops[hole_path] = {"op": "replace", "path": hole_path, "value": new_value}
            except Exception:
                # fallback: no patch
                continue
        # Additional heuristics can be implemented here

    # Return patch operations in a deterministic order
    return list(patch_ops.values())
