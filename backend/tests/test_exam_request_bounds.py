"""Tests sur les bornes Pydantic de SubmitAnswerRequest (iter 39 Q3).

L'audit data iter 37 a relevé que les schémas Pydantic exposés par
`POST /exams/sessions/{id}/answer` n'avaient aucune borne — `time_seconds`
pouvait être négatif, `item_number` non borné, `sub_label` n'importe
quel `str`. Iter 39 ajoute les contraintes (`ge=0`, `ge=1 le=10`,
`Literal["a","b","c"]`) pour rejeter dès la validation.
"""
import uuid

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints.exams import SubmitAnswerRequest


def test_submit_answer_accept_qcm_path():
    req = SubmitAnswerRequest(
        question_id=uuid.uuid4(),
        answer="A",
        time_seconds=42,
    )
    assert req.time_seconds == 42
    assert req.item_number is None
    assert req.sub_label is None


def test_submit_answer_accept_cep_path():
    req = SubmitAnswerRequest(
        answer=12,
        item_number=2,
        sub_label="b",
        time_seconds=0,
    )
    assert req.item_number == 2
    assert req.sub_label == "b"


def test_time_seconds_negative_rejected():
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(answer=0, time_seconds=-1)


def test_time_seconds_zero_accepted():
    """Une réponse instantanée (idempotent retry, clock skew) reste valide."""
    req = SubmitAnswerRequest(answer=0, time_seconds=0)
    assert req.time_seconds == 0


def test_item_number_below_one_rejected():
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(answer=0, item_number=0, sub_label="a")


def test_item_number_above_ten_rejected():
    """Borne haute généreuse (10) pour absorber les futurs formats CEP."""
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(answer=0, item_number=11, sub_label="a")


def test_item_number_observed_range_accepted():
    """1..4 sont les valeurs observées en DB ; 10 est la borne haute."""
    for n in (1, 2, 3, 4, 10):
        SubmitAnswerRequest(answer=0, item_number=n, sub_label="a")


def test_sub_label_outside_vocabulary_rejected():
    """Aucune sous-question CEP en base n'utilise un label hors a/b/c."""
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(answer=0, item_number=1, sub_label="d")


def test_sub_label_uppercase_rejected():
    """Literal est sensible à la casse — protège contre les payloads cassés."""
    with pytest.raises(ValidationError):
        SubmitAnswerRequest(answer=0, item_number=1, sub_label="A")


def test_all_optionals_omitted_accepted():
    """Une requête `answer`-only doit rester valide pour rester compatible."""
    req = SubmitAnswerRequest(answer=None)
    assert req.question_id is None
    assert req.time_seconds is None
    assert req.item_number is None
    assert req.sub_label is None
