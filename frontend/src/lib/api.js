const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

async function request(path, options = {}) {
  const isFormData = options.body instanceof FormData;
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...(options.headers || {})
    }
  });

  const payload = await response.json().catch(() => ({}));

  if (!response.ok || payload.success === false) {
    throw new Error(payload.message || `Request failed with status ${response.status}`);
  }

  return payload.data ?? payload;
}

export function getPeople() {
  return request("/people");
}

export function createPerson(data) {
  return request("/people/create", { method: "POST", body: JSON.stringify(data) });
}

export function updatePerson(id, data) {
  return request(`/people/${id}`, { method: "PUT", body: JSON.stringify(data) });
}

export function deletePerson(id) {
  return request(`/people/${id}`, { method: "DELETE" });
}

export function getTimings() {
  return request("/timings");
}

export function createTiming(data) {
  return request("/timings/create", { method: "POST", body: JSON.stringify(data) });
}

export function startAttendanceSession(data) {
  return request("/attendance/session/start", { method: "POST", body: JSON.stringify(data) });
}

export function getAttendanceToday() {
  return request("/attendance/today");
}

export function markAttendance(data) {
  return request("/attendance/mark", { method: "POST", body: JSON.stringify(data) });
}

export function startFaceEnrollment(personId) {
  return request(`/face/enrollment/start/${personId}`, { method: "POST" });
}

export function getFaceEnrollmentStatus(personId) {
  return request(`/face/enrollment/status/${personId}`);
}

export function sendEnrollmentFrame(formData) {
  return request("/face/enrollment/frame", { method: "POST", body: formData });
}

export function recognizeFace(formData) {
  const data = formData instanceof FormData ? Object.fromEntries(formData.entries()) : formData;
  return request("/face/recognize", { method: "POST", body: JSON.stringify(data || {}) });
}

export { API_BASE_URL };
