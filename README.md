# Vernex Smart Attendance

Face-recognition attendance for courses and batches. A phone (or any webcam) streams live video to the
backend, which finds every face in the frame, matches it against enrolled students, and marks attendance.

- `backend/` — FastAPI + SQLAlchemy, Supabase PostgreSQL, DeepFace (YOLOv8 face detector + Facenet512)
- `frontend/` — React + Vite admin dashboard, enrollment camera and live scanner

## Run it

You need Python 3.10, Node 20+, and the PC and phone on the same Wi-Fi.

### 1. Backend (first terminal)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `backend/.env` (never committed):

```env
DATABASE_URL=postgresql://postgres.PROJECT_REF:ENCODED_PASSWORD@aws-0-REGION.pooler.supabase.com:6543/postgres
FRONTEND_ORIGIN=http://localhost:5173
DEFAULT_TIMEZONE=Asia/Kolkata
```

Copy the host from Supabase → Connect → Transaction pooler; the region must be your project's.
In the password, write `@` as `%40` and `%` as `%25`. Without `DATABASE_URL` the app uses a local SQLite file.

```powershell
python scripts/test_supabase_connection.py   # should print "connection successful"
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Tables are created automatically on startup. Wait for `face models ready` in the log (about 30 seconds;
the first ever start also downloads ~100 MB of model weights). Check http://localhost:8000/health.

### 2. Frontend (second terminal)

```powershell
cd frontend
npm install
npm run dev:https
```

HTTPS is required because browsers only open the camera on secure pages. The terminal prints the links;
use the one that starts with your Wi-Fi address, for example `https://192.168.1.11:5173`.

### 3. Connect the phone

1. Open `https://<PC Wi-Fi address>:5173/attendance-scanner` in the phone's browser.
2. The certificate is self-signed, so accept the warning (Advanced → Proceed).
3. Log in, then allow camera access when asked.

If the page does not load: confirm both devices are on the same Wi-Fi, and allow Node.js through
Windows Firewall for your network type. The phone only talks to the frontend; Vite forwards `/api`
calls to the backend, so port 8000 does not need to be reachable from the phone.

## Workflow

1. **Courses → Batches → Students.** Create a course, a batch under it, then students assigned to both.
2. **Face Enrollment.** Pick course, batch and student, press Start Enrollment, and follow the five
   guided shots (front, left, right, close, far), which are captured automatically. Left and right mean
   really turning the head (about 15 degrees), so the system learns the face from several angles. Each shot is checked for one face, light, sharpness,
   distance and position; a rejected shot says why. Enrolling again replaces the old reference faces.
3. **Attendance Scanner.** Pick course and batch, press Start Session, and point the camera at the class.
   Frames are sent continuously. Green boxes are recognized students, red boxes are unknown faces.
4. **Marking.** A student is marked once they are matched in 3 frames within 10 seconds: `present`,
   `late` after the session's grace time, `absent` after its end time. Each student is marked once per session.
5. **Stop Session**, then see **Reports** for the records by date, course and batch.

## How recognition works

1. YOLOv8 finds every face in the frame; faces under 50 px are skipped as too far away.
2. Facenet512 turns each face into a 512-number vector.
3. The vector is compared (cosine similarity) with the enrolled vectors of that session's batch only.
4. A match needs similarity ≥ 0.60 **and** a lead of ≥ 0.05 over the next most similar student,
   otherwise the face stays "Unknown".
5. One student can only be one face per frame, and several agreeing frames are needed before marking.
6. Before a student is marked, a liveness model (MiniFASNet) checks that the face is a real person and
   not a printed photo or a screen. A rejected face shows a red "Photo detected" box, and the student's
   count starts again after a 3 second pause. Enrollment refuses photos the same way.

Settings in `backend/.env`:

| Variable | Default | Meaning |
| --- | --- | --- |
| `FACE_MATCH_THRESHOLD` | `0.60` | Raise to be stricter (fewer wrong names, more "Unknown") |
| `FACE_MATCH_MARGIN` | `0.05` | Required lead over the second-best student |
| `FACE_CONFIRM_FRAMES` | `3` | Matching frames needed before attendance is written |
| `FACE_LIVENESS` | `true` | Set `false` to turn the photo/screen check off |
| `FACE_LIVENESS_THRESHOLD` | `0.50` | "Real face" score needed; raise to be stricter with photos |
| `FACE_DETECTOR` | `yolov8n` | DeepFace detector name |
| `FACE_MODEL` | `Facenet512` | Changing it requires enrolling everyone again |
| `FACE_NORMALIZATION` | `Facenet2018` | Input scaling for the model; changing it also requires enrolling again |

## Accuracy and limits

Measured with the default settings:

- DeepFace's 300 labelled photo pairs (clear portraits): 299 of 300 correct, no wrong-person matches.
- LFW, 1000 pairs of small, unconstrained web photos: 98.6% at the best threshold; at a threshold with
  no wrong-person matches, 93% of genuine pairs are accepted from a single photo. GhostFaceNet (91.5%)
  and SFace (93.2%) scored lower in the same test.

No face recognition system is 100% accurate; results depend on enrollment quality, lighting and distance.

- The liveness check looks at single camera frames. It stops ordinary printed photos and phone screens,
  but a sharp, well-lit screen or a video can still get through, and poor lighting can make it reject a real face.
- The login page does not verify credentials and the API has no authentication. Use it on a trusted network only.
- The models run on the CPU: about 0.2–0.35 seconds per frame on a laptop (7 faces: ~0.35 s), so 2–3 frames per second live.

## Tests

```powershell
cd backend
python -m pytest
```
