from datetime import date

from app.models.attendance import AttendanceSession
from app.models.course import Course, CourseBatch
from app.models.person import Person
from app.schemas.attendance_schema import AttendanceMark
from app.services.attendance_service import mark_attendance


def _seed_course_batch(db_session):
    course = Course(course_code="CS101", course_name="Comp Sci")
    db_session.add(course)
    db_session.commit()
    db_session.refresh(course)

    batch = CourseBatch(course_id=course.id, batch_name="Morning A")
    db_session.add(batch)
    db_session.commit()
    db_session.refresh(batch)

    return course, batch


def test_non_student_can_be_marked_present_despite_no_course_or_batch(db_session):
    course, batch = _seed_course_batch(db_session)

    session = AttendanceSession(
        session_name="Morning",
        session_type="class",
        course_id=course.id,
        batch_id=batch.id,
        session_date=date(2026, 1, 1),
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    staff = Person(
        person_code="T1",
        full_name="Bob",
        person_type="staff",
        course_id=None,
        batch_id=None,
    )
    db_session.add(staff)
    db_session.commit()
    db_session.refresh(staff)

    payload = AttendanceMark(session_id=session.id, person_id=staff.id)
    record, message = mark_attendance(db_session, payload)

    assert record is not None, f"expected staff to be marked present, got rejection: {message}"
    assert record.status in {"present", "late"}


def test_student_is_still_rejected_for_mismatched_course(db_session):
    course, batch = _seed_course_batch(db_session)
    other_course = Course(course_code="EE101", course_name="Electrical")
    db_session.add(other_course)
    db_session.commit()
    db_session.refresh(other_course)

    session = AttendanceSession(
        session_name="Morning",
        session_type="class",
        course_id=course.id,
        batch_id=batch.id,
        session_date=date(2026, 1, 1),
    )
    db_session.add(session)
    db_session.commit()
    db_session.refresh(session)

    student = Person(
        person_code="S1",
        full_name="Alice",
        person_type="student",
        course_id=other_course.id,
        batch_id=None,
    )
    db_session.add(student)
    db_session.commit()
    db_session.refresh(student)

    payload = AttendanceMark(session_id=session.id, person_id=student.id)
    record, message = mark_attendance(db_session, payload)

    assert record is None
    assert message == "Person does not belong to this course"
