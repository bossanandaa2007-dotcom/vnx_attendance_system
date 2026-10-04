import json
from types import SimpleNamespace

from app.config import settings
from app.services import face_service
from app.services.face_service import best_match, build_gallery, confirm_match


def _stored(person_id, vector):
    return SimpleNamespace(person_id=person_id, embedding_vector=json.dumps(vector))


def test_best_match_returns_the_closest_person():
    gallery = build_gallery([_stored(1, [1.0, 0.0, 0.0]), _stored(2, [0.0, 1.0, 0.0])])

    match = best_match([0.9, 0.1, 0.0], gallery)

    assert match["embedding"].person_id == 1
    assert match["confidence"] > settings.face_match_threshold


def test_best_match_rejects_a_face_below_the_threshold():
    gallery = build_gallery([_stored(1, [1.0, 0.0, 0.0])])

    assert best_match([0.3, 1.0, 0.0], gallery) is None


def test_best_match_rejects_a_face_that_resembles_two_people():
    gallery = build_gallery([_stored(1, [1.0, 0.0, 0.0]), _stored(2, [0.96, 0.28, 0.0])])

    assert best_match([0.99, 0.14, 0.0], gallery) is None


def test_best_match_ignores_other_photos_of_the_same_person_for_the_margin():
    gallery = build_gallery([_stored(1, [1.0, 0.0, 0.0]), _stored(1, [0.96, 0.28, 0.0])])

    assert best_match([0.99, 0.14, 0.0], gallery)["embedding"].person_id == 1


def test_best_match_handles_an_empty_gallery():
    assert best_match([1.0, 0.0, 0.0], build_gallery([])) is None


def test_confirm_match_needs_several_frames(monkeypatch):
    monkeypatch.setattr(settings, "face_confirm_frames", 3)
    face_service.recent_matches.clear()

    assert [confirm_match(7, 1) for _ in range(3)] == [False, False, True]
    assert confirm_match(7, 2) is False


def test_confirm_match_starts_over_after_a_spoof_frame(monkeypatch):
    monkeypatch.setattr(settings, "face_confirm_frames", 3)
    face_service.recent_matches.clear()
    face_service.blocked_until.clear()
    clock = iter([0.0, 1.0, 2.0, 3.0, 6.0, 7.0, 8.0])
    monkeypatch.setattr(face_service.time, "monotonic", lambda: next(clock))

    # Two live frames, a spoof frame, a frame inside the pause, then three clean live frames.
    verdicts = [confirm_match(7, 1, live) for live in (True, True, False, True, True, True, True)]

    assert verdicts == [False, False, False, False, False, False, True]


def test_confirm_match_forgets_old_frames(monkeypatch):
    monkeypatch.setattr(settings, "face_confirm_frames", 2)
    face_service.recent_matches.clear()
    clock = iter([0.0, 60.0, 61.0])
    monkeypatch.setattr(face_service.time, "monotonic", lambda: next(clock))

    assert [confirm_match(7, 1) for _ in range(3)] == [False, False, True]
