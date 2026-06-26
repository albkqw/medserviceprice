"""Service name matcher.

Priority:
  1. Exact / synonym lookup  — O(1), dict keyed on normalize_text()
  2. Fuzzy match              — O(N), rapidfuzz token_sort_ratio
  3. Unmatched                — returned when score < threshold

To scale beyond ~5k canonical services, swap _fuzzy_match() to use a
TF-IDF matrix (sklearn) or Postgres pg_trgm. The MatchResult contract
and ServiceMatcher.match() signature never change.
"""

import uuid
from dataclasses import dataclass

from rapidfuzz import fuzz, process

from app.models.service import Service
from app.normalization.text import normalize_text, strip_parentheses

FUZZY_THRESHOLD = 85.0
SUGGESTION_THRESHOLD = 60.0  # below this we don't even suggest


@dataclass
class MatchResult:
    service_id: uuid.UUID | None       # set when method != "unmatched"
    suggested_id: uuid.UUID | None     # best guess for admin review (may be None)
    score: float
    method: str                        # "exact" | "synonym" | "fuzzy" | "unmatched"


class ServiceMatcher:
    """Immutable index built once per normalization run from all active services."""

    def __init__(self, services: list[Service], threshold: float = FUZZY_THRESHOLD) -> None:
        self._threshold = threshold

        # exact[normalized_name] → service_id
        self._exact: dict[str, uuid.UUID] = {}

        # fuzzy candidates list and reverse lookup
        self._names: list[str] = []
        self._name_to_id: dict[str, uuid.UUID] = {}

        for svc in services:
            all_names = [svc.name] + list(svc.synonyms or [])
            for raw in all_names:
                norm = normalize_text(raw)
                stripped = strip_parentheses(norm)

                # exact lookup: both the full normalized form and the stripped form
                self._exact.setdefault(norm, svc.id)
                if stripped and stripped != norm:
                    self._exact.setdefault(stripped, svc.id)

                # fuzzy candidates: deduplicate
                if norm not in self._name_to_id:
                    self._names.append(norm)
                    self._name_to_id[norm] = svc.id

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def match(self, raw_name: str) -> MatchResult:
        norm = normalize_text(raw_name)
        stripped = strip_parentheses(norm)

        # 1. Exact / synonym
        for key in (norm, stripped):
            if key in self._exact:
                return MatchResult(
                    service_id=self._exact[key],
                    suggested_id=None,
                    score=100.0,
                    method="exact",
                )

        if not self._names:
            return MatchResult(service_id=None, suggested_id=None, score=0.0, method="unmatched")

        # 2. Fuzzy — use stripped form (shorter = fewer noise tokens)
        best = process.extractOne(
            stripped or norm,
            self._names,
            scorer=fuzz.token_sort_ratio,
        )
        if best is None:
            return MatchResult(service_id=None, suggested_id=None, score=0.0, method="unmatched")

        best_name, best_score, _ = best
        best_id = self._name_to_id[best_name]

        if best_score >= self._threshold:
            return MatchResult(
                service_id=best_id,
                suggested_id=None,
                score=float(best_score),
                method="fuzzy",
            )

        # 3. Unmatched — still carry suggestion if score is meaningful
        suggested = best_id if best_score >= SUGGESTION_THRESHOLD else None
        return MatchResult(
            service_id=None,
            suggested_id=suggested,
            score=float(best_score),
            method="unmatched",
        )

    @property
    def service_count(self) -> int:
        return len(self._name_to_id)
