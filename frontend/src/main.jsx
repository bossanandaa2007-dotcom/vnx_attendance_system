import React, { useEffect, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity, AlertTriangle, BarChart3, Camera, Check, ChevronRight,
  Clock, Download, FileSpreadsheet, GraduationCap, LayoutDashboard, LogOut,
  Menu, Plus, ScanFace, Search, Settings, ShieldCheck, Square,
  Trash2, Upload, UserCheck, Users, Wifi, X
} from "lucide-react";
import {
  API_BASE_URL,
  createPerson,
  deletePerson,
  getAttendanceToday,
  getPeople,
  getTimings,
  markAttendance,
  sendEnrollmentFrame,
  startAttendanceSession,
  startFaceEnrollment,
  updatePerson
} from "./lib/api";
import "./styles.css";

const DEFAULT_COURSES = ["Silambam", "Football", "Cricket", "Tuition", "Gym", "Dance", "Music"];
const DEFAULT_BATCHES = ["Morning A", "Evening A", "Weekend"];
const PEOPLE = [
  { id: "p1", name: "Aarav Kumar", phone: "9876543210", code: "VX101", type: "Student", category: "Silambam", batch: "Morning A", status: "Active", enrolled: true },
  { id: "p2", name: "Meera S", phone: "9876500000", code: "ST201", type: "Staff", category: "Front Desk", batch: "Morning A", status: "Active", enrolled: false },
  { id: "p3", name: "Kavin Raj", phone: "9876511111", code: "MB301", type: "Member", category: "Gym", batch: "Evening A", status: "Active", enrolled: false }
];
const SESSIONS = [{ id: "s1", name: "Morning A", category: "Silambam", start: "06:00", durationSeconds: 2700, state: "Idle" }];
const ROUTES = {
  dashboard: "/dashboard",
  students: "/users/students",
  staff: "/users/staff",
  members: "/users/members",
  enrollment: "/face-enrollment",
  scanner: "/attendance-scanner",
  reports: "/reports",
  settings: "/settings"
};
const PATH_TO_PAGE = Object.fromEntries(Object.entries(ROUTES).map(([page, path]) => [path, page]));
const FIELD_SCHEMAS = {
  Student: [
    ["code", "Student ID"], ["name", "Student Name"], ["parentName", "Parent Name"], ["phone", "Parent Contact Number"],
    ["category", "Category / Program", "select:courses"], ["batch", "Batch Name", "select:batches"], ["level", "Level / Class"], ["timing", "Timing"],
    ["joiningDate", "Joining Date", "date"], ["status", "Status", "select:status"], ["faceStatus", "Face Enrollment Status", "select:face"], ["notes", "Notes", "textarea"]
  ],
  Staff: [
    ["code", "Staff ID"], ["name", "Staff Name"], ["phone", "Staff Contact Number"], ["email", "Email", "email"],
    ["designation", "Designation"], ["department", "Department"], ["batch", "Shift Name", "select:batches"], ["timing", "Shift Timing"],
    ["joiningDate", "Joining Date", "date"], ["status", "Status", "select:status"], ["faceStatus", "Face Enrollment Status", "select:face"], ["notes", "Notes", "textarea"]
  ],
  Member: [
    ["code", "Member ID"], ["name", "Member Name"], ["phone", "Member Contact Number"], ["email", "Email", "email"],
    ["membershipType", "Membership Type"], ["planName", "Plan Name"], ["category", "Category / Program", "select:courses"], ["startDate", "Start Date", "date"],
    ["endDate", "End Date", "date"], ["status", "Status", "select:status"], ["faceStatus", "Face Enrollment Status", "select:face"], ["notes", "Notes", "textarea"]
  ]
};
const SCANS = [
  { id: "r1", name: "Aarav Kumar", code: "VX101", type: "Student", category: "Silambam", status: "Present", confidence: 96, time: new Date().toISOString() },
  { id: "r2", name: "Unknown", code: "-", type: "-", category: "-", status: "Unknown", confidence: 41, time: new Date().toISOString() }
];

function store(key, seed) {
  const [value, setValue] = useState(() => JSON.parse(localStorage.getItem(key) || "null") || seed);
  useEffect(() => localStorage.setItem(key, JSON.stringify(value)), [key, value]);
  return [value, setValue];
}

function useBackendData() {
  const [people, setPeople] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  const refresh = async () => {
    setError("");
    try {
      const [peopleRows, timingRows, attendanceRows] = await Promise.all([
        getPeople(),
        getTimings(),
        getAttendanceToday()
      ]);
      setPeople((peopleRows || []).map(mapApiPerson));
      setSessions((timingRows || []).map(mapApiTiming));
      setRecords((attendanceRows || []).map(mapApiAttendance));
    } catch (err) {
      setError(err.message || "Unable to load backend data.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { refresh(); }, []);

  const notify = message => {
    setToast(message);
    setTimeout(() => setToast(""), 2800);
  };

  return { people, setPeople, sessions, setSessions, records, setRecords, loading, error, setError, toast, notify, refresh };
}

function App() {
  const mobile = location.pathname.toLowerCase().includes("mobile") || location.search.includes("mobile");
  const backend = useBackendData();
  const shared = {
    people: [backend.people, backend.setPeople],
    sessions: [backend.sessions, backend.setSessions],
    records: [backend.records, backend.setRecords],
    profile: store("vx_profile", { enterprise: "Vernex Gen Technologies", owner: "Admin", phone: "", address: "", sheet: "", logo: "", backend: API_BASE_URL }),
    courses: store("vx_courses", DEFAULT_COURSES),
    batches: store("vx_batches", DEFAULT_BATCHES),
    task: store("vx_mobile_task", null),
    backend
  };
  return mobile ? <MobileDashboard data={shared} /> : <AdminApp data={shared} />;
}

function AdminApp({ data }) {
  const [logged, setLogged] = useState(localStorage.getItem("vx_auth") === "yes");
  const [page, setPageState] = useState(() => PATH_TO_PAGE[location.pathname] || "dashboard");
  const [profile] = data.profile;
  const setPage = pageId => {
    setPageState(pageId);
    history.pushState(null, "", ROUTES[pageId] || "/dashboard");
  };
  useEffect(() => {
    const sync = () => setPageState(PATH_TO_PAGE[location.pathname] || "dashboard");
    addEventListener("popstate", sync);
    return () => removeEventListener("popstate", sync);
  }, []);
  if (!logged) return <Login onLogin={() => { localStorage.setItem("vx_auth", "yes"); setLogged(true); }} />;
  return <AdminShell page={page} profile={profile} setPage={setPage} logout={() => { localStorage.removeItem("vx_auth"); setLogged(false); }}>
    {page === "dashboard" && <Dashboard data={data} setPage={setPage} />}
    {page === "students" && <PeoplePage type="Student" data={data} />}
    {page === "staff" && <PeoplePage type="Staff" data={data} />}
    {page === "members" && <PeoplePage type="Member" data={data} />}
    {page === "enrollment" && <FaceEnrollment data={data} />}
    {page === "scanner" && <AttendanceScanner data={data} />}
    {page === "reports" && <Reports data={data} />}
    {page === "settings" && <SettingsPage data={data} />}
  </AdminShell>;
}

function Login({ onLogin }) {
  return <main className="grid min-h-screen place-items-center bg-slate-100 p-4">
    <section className="w-full max-w-md rounded-lg border border-slate-200 bg-white p-7 shadow-sm">
      <Brand />
      <div className="mt-8">
        <h1 className="text-3xl font-bold text-[#082248]">Admin Login</h1>
        <p className="mt-2 text-sm text-slate-500">Secure local attendance console for your institute.</p>
      </div>
      <form className="mt-7 grid gap-4" onSubmit={(event) => { event.preventDefault(); onLogin(); }}>
        <FormInput label="Admin ID" placeholder="Enter admin ID" autoComplete="username" />
        <FormInput label="Password" placeholder="Enter password" type="password" autoComplete="current-password" />
        <button className="inline-flex h-11 items-center justify-center rounded-lg bg-[#082248] px-4 font-semibold text-white transition hover:bg-[#12396f]">Login</button>
      </form>
      <div className="mt-5 flex items-center gap-2 rounded-lg bg-slate-50 px-3 py-2 text-sm text-slate-600"><ShieldCheck size={16} /> Face data stays inside your local system.</div>
    </section>
  </main>;
}

function AdminShell({ children, page, profile, setPage, logout }) {
  const [open, setOpen] = useState(false);
  return <div className="min-h-screen bg-[#f5f7fb] text-slate-950">
    <Sidebar open={open} page={page} profile={profile} setOpen={setOpen} setPage={setPage} logout={logout} />
    {open && <button className="fixed inset-0 z-30 bg-slate-950/35 lg:hidden" aria-label="Close navigation" onClick={() => setOpen(false)} />}
    <div className="min-w-0 lg:pl-72">
      <Header profile={profile} onMenu={() => setOpen(true)} />
      <main className="mx-auto w-full max-w-7xl px-4 py-5 sm:px-6 lg:px-8">{children}</main>
    </div>
  </div>;
}

function Sidebar({ open, page, profile, setOpen, setPage, logout }) {
  return <aside className={`fixed inset-y-0 left-0 z-40 w-72 border-r border-slate-200 bg-white transition-transform duration-200 lg:translate-x-0 ${open ? "translate-x-0" : "-translate-x-full"}`}>
    <div className="flex h-full flex-col p-5">
      <div className="flex items-start justify-between">
        <Brand profile={profile} />
        <button className="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 text-slate-600 lg:hidden" onClick={() => setOpen(false)}><X size={18} /></button>
      </div>
      <nav className="mt-8 grid gap-1.5">
        <SidebarItem id="dashboard" label="Dashboard" icon={LayoutDashboard} page={page} setPage={setPage} setOpen={setOpen} />
        <UserManagementMenu page={page} setPage={setPage} setOpen={setOpen} />
        <SidebarItem id="enrollment" label="Face Enrollment" icon={ScanFace} page={page} setPage={setPage} setOpen={setOpen} />
        <SidebarItem id="scanner" label="Attendance Scanner" icon={Camera} page={page} setPage={setPage} setOpen={setOpen} />
        <SidebarItem id="reports" label="Reports" icon={BarChart3} page={page} setPage={setPage} setOpen={setOpen} />
        <SidebarItem id="settings" label="Settings" icon={Settings} page={page} setPage={setPage} setOpen={setOpen} />
      </nav>
      <button className="mt-auto flex h-11 items-center gap-3 rounded-lg px-3 text-left text-sm font-semibold text-slate-600 hover:bg-slate-100" onClick={logout}><LogOut size={18} />Logout</button>
    </div>
  </aside>;
}

function SidebarItem({ id, label, icon: Icon, page, setPage, setOpen, child }) {
  const active = page === id;
  return <button className={`${child ? "ml-4 h-9 border-l-2 pl-4" : "h-11 px-3"} flex items-center gap-3 rounded-lg text-left text-sm font-semibold transition ${active ? child ? "border-[#c89736] bg-slate-50 text-[#082248]" : "bg-[#082248] text-white shadow-sm" : child ? "border-slate-200 text-slate-500 hover:border-[#c89736] hover:bg-slate-50 hover:text-[#082248]" : "text-slate-600 hover:bg-slate-100 hover:text-[#082248]"}`} onClick={() => { setPage(id); setOpen(false); }}>
    <Icon size={child ? 15 : 18} />{label}
  </button>;
}

function SidebarGroup({ children }) {
  return <div className="rounded-xl bg-slate-50/70 p-1">{children}</div>;
}

function UserManagementMenu({ page, setPage, setOpen }) {
  const userPages = ["students", "staff", "members"];
  const [expanded, setExpanded] = useState(userPages.includes(page));
  const active = userPages.includes(page);
  useEffect(() => { if (active) setExpanded(true); }, [active]);
  return <SidebarGroup>
    <button className={`flex h-11 w-full items-center gap-3 rounded-lg px-3 text-left text-sm font-semibold transition ${active ? "bg-white text-[#082248] shadow-sm ring-1 ring-slate-200" : "text-slate-600 hover:bg-white hover:text-[#082248]"}`} onClick={() => setExpanded(!expanded)}>
      <Users size={18} />
      <span className="flex-1">User Management</span>
      <ChevronRight size={16} className={`transition-transform ${expanded ? "rotate-90" : ""}`} />
    </button>
    {expanded && <div className="mt-1 grid gap-1 pb-1">
      <SidebarItem child id="students" label="Students" icon={GraduationCap} page={page} setPage={setPage} setOpen={setOpen} />
      <SidebarItem child id="staff" label="Staff" icon={UserCheck} page={page} setPage={setPage} setOpen={setOpen} />
      <SidebarItem child id="members" label="Members" icon={Users} page={page} setPage={setPage} setOpen={setOpen} />
    </div>}
  </SidebarGroup>;
}

function Header({ profile, onMenu }) {
  const now = useClock();
  return <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/95 backdrop-blur">
    <div className="mx-auto flex min-h-16 max-w-7xl items-center justify-between gap-3 px-4 sm:px-6 lg:px-8">
      <button className="grid h-10 w-10 place-items-center rounded-xl border border-slate-200 text-[#082248] lg:hidden" aria-label="Open navigation" onClick={onMenu}><Menu size={21} /></button>
      <div className="min-w-0">
        <p className="truncate text-sm font-medium text-slate-500">Local-first attendance over the same Wi-Fi network</p>
        <h1 className="truncate text-lg font-bold text-[#082248] sm:text-xl">{profile.enterprise}</h1>
      </div>
      <div className="shrink-0 rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-right">
        <p className="text-sm font-bold text-[#082248]">{now.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}</p>
        <p className="text-xs font-semibold text-slate-500">{now.toLocaleDateString([], { day: "2-digit", month: "short", year: "numeric" })}</p>
      </div>
    </div>
  </header>;
}

function Dashboard({ data, setPage }) {
  const [[people], [records], [profile], [courses]] = [data.people, data.records, data.profile, data.courses];
  const { loading, error, toast } = data.backend;
  const status = useBackendStatus(profile.backend);
  const today = records.filter(r => new Date(r.time).toDateString() === new Date().toDateString());
  const counts = {
    students: countType(people, "Student"),
    staff: countType(people, "Staff"),
    members: countType(people, "Member"),
    present: today.filter(r => r.status === "Present").length,
    late: today.filter(r => r.status === "Late").length,
    absent: Math.max(0, people.length - today.filter(r => r.status === "Present").length),
    pending: people.filter(p => !p.enrolled).length
  };
  return <PageContainer title={`${profile.enterprise} Dashboard`} subtitle="Professional attendance overview for coaching centres, academies, and small businesses.">
    {toast && <Notice tone="success">{toast}</Notice>}
    {error && <Notice tone="error">{error}</Notice>}
    {loading && <Notice>Loading live backend data...</Notice>}
    <section className="grid grid-cols-1 gap-5 xl:grid-cols-[1.15fr_.85fr]">
      <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
        <div className="flex flex-col gap-5 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.18em] text-[#c89736]">Today attendance</p>
            <h3 className="mt-3 text-4xl font-black tracking-tight text-[#082248] sm:text-5xl">{counts.present}</h3>
            <p className="mt-2 text-sm text-slate-500">People marked present from today’s scans.</p>
          </div>
          <div className="grid grid-cols-2 gap-3 sm:min-w-64">
            <MiniMetric label="Late" value={counts.late} />
            <MiniMetric label="Absent" value={counts.absent} tone="red" />
            <MiniMetric label="Pending Face" value={counts.pending} tone="gold" />
            <MiniMetric label="Sheet Sync" value={status} tone={status === "Online" ? "cyan" : "red"} />
          </div>
        </div>
      </div>
      <div className="grid grid-cols-3 gap-3">
        <AudienceTile icon={GraduationCap} label="Students" value={counts.students} />
        <AudienceTile icon={UserCheck} label="Staff" value={counts.staff} />
        <AudienceTile icon={Users} label="Members" value={counts.members} />
      </div>
    </section>
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
      <StatCard icon={Activity} title="Present" value={counts.present} description="Marked through scanner" accent="cyan" />
      <StatCard icon={Clock} title="Late" value={counts.late} description="Late entries today" accent="gold" />
      <StatCard icon={AlertTriangle} title="Absent" value={counts.absent} description="Pending attendance marks" accent="red" />
      <StatCard icon={FileSpreadsheet} title="Sheet Sync" value={status} description={profile.sheet || "Google Sheet not connected"} accent={status === "Online" ? "cyan" : "red"} />
    </div>
    <div className="grid grid-cols-1 gap-5 xl:grid-cols-2">
      <Card title="Course / Batch Summary" action={<button className="text-sm font-semibold text-[#082248]" onClick={() => setPage("settings")}>Manage</button>}>
        <div className="grid gap-3">
          {courses.map(course => <div key={course} className="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 p-3">
            <div><p className="font-semibold text-slate-900">{course}</p><p className="text-sm text-slate-500">{people.filter(p => p.category === course).length} users assigned</p></div>
            <ChevronRight className="text-slate-400" size={18} />
          </div>)}
        </div>
      </Card>
      <Card title="Recent Attendance">
        <DataTable columns={["Name", "Code", "Type", "Status", "Time"]} rows={today.slice(0, 5).map(r => [r.name, r.code, r.type || "-", <StatusBadge status={r.status} />, new Date(r.time).toLocaleTimeString()])} empty="No scans recorded today." />
      </Card>
    </div>
  </PageContainer>;
}

function PeoplePage({ type, data }) {
  const [people, setPeople] = data.people;
  const [, setTask] = data.task;
  const [courses, setCourses] = data.courses;
  const [batches, setBatches] = data.batches;
  const { loading, error, toast, notify, refresh } = data.backend;
  const blank = {
    name: "", phone: "", code: "", type, parentName: "", email: "", designation: "", department: "",
    membershipType: "", planName: "", level: "", timing: "", joiningDate: "", startDate: "", endDate: "",
    notes: "", category: courses[0] || "", batch: batches[0] || "", status: "Active", faceStatus: "Pending", enrolled: false
  };
  const [form, setForm] = useState(blank);
  const [q, setQ] = useState("");
  const [filter, setFilter] = useState("All");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [newCourse, setNewCourse] = useState("");
  const [newBatch, setNewBatch] = useState("");
  const rows = people.filter(p => p.type === type).filter(p => filter === "All" || p.status === filter).filter(p => JSON.stringify(p).toLowerCase().includes(q.toLowerCase()));
  const save = async event => {
    event.preventDefault();
    if (form.phone.length !== 10) { setMessage("Phone number must contain exactly 10 digits."); return; }
    setSaving(true);
    setMessage("");
    try {
      await createPerson(toPersonPayload(form, type));
      await refresh();
      setForm({ ...blank, category: courses[0] || "", batch: batches[0] || "" });
      notify(`${type} created successfully.`);
      setMessage(`${type} created successfully.`);
    } catch (err) {
      setMessage(err.message || `Unable to create ${type.toLowerCase()}.`);
    } finally {
      setSaving(false);
    }
  };
  const remove = async id => {
    try {
      await deletePerson(id);
      setPeople(people.filter(x => x.id !== id));
      notify(`${type} deleted.`);
    } catch (err) {
      setMessage(err.message || `Unable to delete ${type.toLowerCase()}.`);
    }
  };
  return <PageContainer title={`${type} Details`} subtitle={`Create, filter, and manage ${type.toLowerCase()} attendance profiles.`}>
    {toast && <Notice tone="success">{toast}</Notice>}
    {error && <Notice tone="error">{error}</Notice>}
    {loading && <Notice>Loading {type.toLowerCase()} records from FastAPI...</Notice>}
    <Card title={`Create ${type}`}>
      <form className="grid gap-4 md:grid-cols-2" onSubmit={save}>
        {FIELD_SCHEMAS[type].map(([key, label, kind]) => <FieldRenderer key={key} fieldKey={key} label={label} kind={kind} form={form} setForm={setForm} courses={courses} batches={batches} />)}
        <div className="flex flex-col gap-2 md:col-span-2 sm:flex-row">
          <button disabled={saving} className="inline-flex h-11 flex-1 items-center justify-center gap-2 rounded-xl bg-[#082248] px-4 font-semibold text-white hover:bg-[#12396f] disabled:cursor-not-allowed disabled:opacity-60"><Plus size={17} />{saving ? "Saving..." : `Save ${type}`}</button>
          <button type="button" className="h-11 rounded-xl border border-slate-200 px-4 font-semibold text-slate-700 hover:bg-slate-50" onClick={() => { setForm(blank); setMessage(""); }}>Reset</button>
        </div>
        {message && <p className={`md:col-span-2 rounded-lg px-3 py-2 text-sm font-medium ${message.includes("must") ? "bg-red-50 text-red-700" : "bg-emerald-50 text-emerald-700"}`}>{message}</p>}
      </form>
    </Card>
    <Card title="Create Batch / Category">
      <div className="grid gap-3 md:grid-cols-2">
        <InlineCreate placeholder="Create course / class" value={newCourse} setValue={setNewCourse} onAdd={() => addUnique(newCourse, courses, setCourses, setNewCourse)} />
        <InlineCreate placeholder="Create batch" value={newBatch} setValue={setNewBatch} onAdd={() => addUnique(newBatch, batches, setBatches, setNewBatch)} />
      </div>
    </Card>
    <Card title={`${type} List`} action={<ListTools q={q} setQ={setQ} filter={filter} setFilter={setFilter} />}>
      <DataTable columns={["Name", "Phone", "Code", "Course", "Batch", "Status", "Face", "Action"]} rows={rows.map(p => [
        p.name,
        p.phone,
        p.code,
        p.category,
        p.batch,
        <StatusBadge status={p.status} />,
        <StatusBadge status={p.enrolled ? "Completed" : "Pending"} />,
        <div className="flex gap-2"><button className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-semibold text-[#082248]" onClick={() => setTask({ mode: "enroll", personId: p.id, createdAt: Date.now() })}>Enroll</button><button className="grid h-9 w-9 place-items-center rounded-lg border border-slate-200 text-slate-500" onClick={() => remove(p.id)}><Trash2 size={16} /></button></div>
      ])} empty={`No ${type.toLowerCase()} records found.`} />
    </Card>
  </PageContainer>;
}

function FaceEnrollment({ data }) {
  const [people, setPeople] = data.people;
  const [, setTask] = data.task;
  const [profile] = data.profile;
  const { error, toast, notify, refresh } = data.backend;
  const [message, setMessage] = useState("");
  const [mobileLink, setMobileLink] = useState("");
  const [busy, setBusy] = useState(false);
  const pending = people.filter(p => !p.enrolled);
  const selected = pending[0] || people[0];
  const steps = ["Look straight", "Move left", "Move right", "Move closer", "Move backward", "Optional specs reference"];
  const warnings = ["Low light detected", "Face too far", "Face too close", "Multiple faces detected", "Remove spectacles"];
  const sendToMobile = async () => {
    if (!selected) return;
    setBusy(true);
    setMessage("");
    try {
      await startFaceEnrollment(selected.id);
      const task = { mode: "enroll", personId: selected.id, createdAt: Date.now() };
      setTask(task);
      const link = buildMobileLink(task, profile.backend);
      setMobileLink(link);
      await navigator.clipboard?.writeText(link).catch(() => {});
      notify(`Enrollment started for ${selected.name}.`);
    } catch (err) {
      setMessage(err.message || "Unable to start face enrollment.");
    } finally {
      setBusy(false);
    }
  };
  const complete = async () => {
    if (!selected) return;
    setBusy(true);
    setMessage("");
    try {
      await updatePerson(selected.id, { face_enrollment_status: "completed" });
      setPeople(people.map(p => p.id === selected.id ? { ...p, enrolled: true, faceStatus: "Completed" } : p));
      await refresh();
      notify(`Enrollment completed for ${selected.name}.`);
    } catch (err) {
      setMessage(err.message || "Unable to complete enrollment.");
    } finally {
      setBusy(false);
    }
  };
  return <PageContainer title="Face Enrollment" subtitle="Guide users through a clear camera-based enrollment flow.">
    {toast && <Notice tone="success">{toast}</Notice>}
    {(error || message) && <Notice tone="error">{message || error}</Notice>}
    <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.1fr_.9fr]">
      <CameraPanel title="Enrollment Camera" subtitle={selected ? `${selected.name} - ${selected.code}` : "No user selected"} />
      <Card title="Current Instruction" action={<StatusBadge status={selected?.enrolled ? "Completed" : "Pending"} />}>
        <div className="space-y-5">
          <div className="rounded-lg bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-500">Selected user</p>
            <p className="mt-1 text-xl font-bold text-[#082248]">{selected?.name || "No user available"}</p>
            <p className="text-sm text-slate-500">{selected?.type || "-"} - {selected?.category || "-"} - {selected?.batch || "-"}</p>
          </div>
          <div>
            <div className="mb-2 flex justify-between text-sm font-semibold"><span>Enrollment progress</span><span>67%</span></div>
            <div className="h-3 overflow-hidden rounded-full bg-slate-100"><div className="h-full w-2/3 rounded-full bg-[#082248]" /></div>
          </div>
          <div className="grid gap-2 sm:grid-cols-2">
            {steps.map((step, index) => <div key={step} className="flex items-center gap-2 rounded-xl border border-slate-200 p-3 text-sm font-semibold text-slate-700"><span className={`grid h-6 w-6 place-items-center rounded-full text-xs ${index < 3 ? "bg-emerald-100 text-emerald-700" : "bg-slate-100 text-slate-500"}`}>{index < 3 ? <Check size={14} /> : index + 1}</span>{step}</div>)}
          </div>
          <div className="grid gap-2">
            {warnings.map(warning => <div key={warning} className="flex items-center gap-2 rounded-xl bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-700"><AlertTriangle size={16} />{warning}</div>)}
          </div>
          <div className="flex flex-col gap-2 sm:flex-row">
            <button disabled={busy || !selected} className="h-11 flex-1 rounded-xl bg-[#082248] px-4 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60" onClick={sendToMobile}>{busy ? "Working..." : "Send to Mobile"}</button>
            <button disabled={busy || !selected} className="h-11 flex-1 rounded-xl border border-slate-200 px-4 font-semibold text-slate-700 disabled:cursor-not-allowed disabled:opacity-60" onClick={complete}>Mark Complete</button>
          </div>
          {mobileLink && <div className="rounded-lg border border-cyan-100 bg-cyan-50 p-3 text-sm text-cyan-900">
            <p className="font-bold">Open this on your phone:</p>
            <a className="break-all underline" href={mobileLink} target="_blank">{mobileLink}</a>
            <button className="mt-2 rounded-lg bg-[#082248] px-3 py-2 text-xs font-bold text-white" onClick={() => navigator.clipboard?.writeText(mobileLink)}>Copy phone link</button>
            <p className="mt-2 text-xs">Do not click this on laptop. Type/paste it in your phone browser on the same Wi-Fi.</p>
          </div>}
        </div>
      </Card>
    </div>
    <Card title="Enrollment Queue">
      <DataTable columns={["User", "Type", "Course", "Batch", "Status"]} rows={pending.map(p => [p.name, p.type, p.category, p.batch, <StatusBadge status="Pending" />])} empty="All users are enrolled." />
    </Card>
  </PageContainer>;
}

function AttendanceScanner({ data }) {
  const [[people], [records, setRecords], [sessions, setSessions]] = [data.people, data.records, data.sessions];
  const { error, toast, notify, refresh } = data.backend;
  const [running, setRunning] = useState(false);
  const [recognized, setRecognized] = useState(null);
  const [activeSession, setActiveSession] = useState(null);
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const startStop = async () => {
    if (running) {
      setRunning(false);
      setActiveSession(null);
      setSessions(sessions.map((s, index) => index === 0 ? { ...s, state: "Idle" } : s));
      return;
    }
    const timing = sessions[0];
    setBusy(true);
    setMessage("");
    try {
      const session = await startAttendanceSession({
        session_name: timing?.name || "Live Attendance",
        session_type: "regular",
        category_program: timing?.category || null,
        batch_name: timing?.batch || null,
        timing_id: timing?.id || null,
        start_time: timing?.start || null
      });
      setActiveSession(session);
      setRunning(true);
      setSessions(sessions.map((s, index) => index === 0 ? { ...s, state: "Running", startedAt: Date.now() } : s));
      notify("Attendance session started.");
    } catch (err) {
      setMessage(err.message || "Unable to start attendance session.");
    } finally {
      setBusy(false);
    }
  };
  const scan = async () => {
    const person = people.find(p => p.enrolled) || people[0];
    if (!person) { setMessage("No person records are available to mark."); return; }
    setBusy(true);
    setMessage("");
    try {
      const record = await markAttendance({
        session_id: activeSession?.id || null,
        person_id: person.id,
        person_code: person.code,
        confidence_score: 0.94,
        recognition_method: "face_ai",
        device_name: "frontend-scanner"
      });
      const next = mapApiAttendance(record);
      setRecognized(next);
      setRecords([next, ...records]);
      notify(`${person.name} marked ${next.status}.`);
      await refresh();
    } catch (err) {
      setMessage(err.message || "Unable to mark attendance.");
    } finally {
      setBusy(false);
    }
  };
  return <PageContainer title="Attendance Scanner" subtitle="Start a camera session, recognize users, and review recent scans.">
    {toast && <Notice tone="success">{toast}</Notice>}
    {(error || message) && <Notice tone="error">{message || error}</Notice>}
    <div className="grid grid-cols-1 gap-5 xl:grid-cols-[1.1fr_.9fr]">
      <CameraPanel title="Scanner Camera" subtitle={running ? "Session running" : "Session stopped"} />
      <Card title="Session Control">
        <div className="space-y-4">
          <button disabled={busy} className={`inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl px-4 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60 ${running ? "bg-red-600" : "bg-[#082248]"}`} onClick={startStop}>{running ? <Square size={17} /> : <Camera size={17} />}{running ? "Stop Session" : busy ? "Starting..." : "Start Session"}</button>
          <button disabled={busy} className="h-11 w-full rounded-xl border border-slate-200 font-semibold text-[#082248] disabled:cursor-not-allowed disabled:opacity-60" onClick={scan}>{busy ? "Processing..." : "Simulate Scan"}</button>
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <p className="text-sm font-semibold text-slate-500">Recognized person</p>
            <p className="mt-2 text-2xl font-bold text-[#082248]">{recognized?.name || "Waiting for scan"}</p>
            <p className="text-sm text-slate-500">Confidence: {recognized?.confidence || 0}%</p>
            <div className="mt-3"><StatusBadge status={recognized?.status || "Unknown"} /></div>
          </div>
        </div>
      </Card>
    </div>
    <Card title="Recent Scans">
      <DataTable columns={["Name", "Code", "Type", "Confidence", "Status", "Time"]} rows={records.slice(0, 8).map(r => [r.name, r.code, r.type || "-", `${r.confidence || 0}%`, <StatusBadge status={r.status} />, new Date(r.time).toLocaleTimeString()])} empty="No recent scans." />
    </Card>
  </PageContainer>;
}

function Reports({ data }) {
  const [[people], [records], [profile]] = [data.people, data.records, data.profile];
  const { loading, error } = data.backend;
  const status = useBackendStatus(profile.backend);
  const today = records.filter(r => new Date(r.time).toDateString() === new Date().toDateString());
  return <PageContainer title="Reports" subtitle="Clean attendance summaries and export placeholders.">
    {error && <Notice tone="error">{error}</Notice>}
    {loading && <Notice>Loading report data from FastAPI...</Notice>}
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-5">
      <StatCard icon={Activity} title="Today Summary" value={today.length} description="Scans recorded" />
      <StatCard icon={GraduationCap} title="Students" value={summaryFor(people, records, "Student")} description="Student attendance" />
      <StatCard icon={UserCheck} title="Staff" value={summaryFor(people, records, "Staff")} description="Staff attendance" />
      <StatCard icon={Users} title="Members" value={summaryFor(people, records, "Member")} description="Member attendance" />
      <StatCard icon={FileSpreadsheet} title="Sheet Sync" value={status} description={profile.sheet || "Not configured"} />
    </div>
    <Card title="Attendance Records" action={<button className="inline-flex items-center gap-2 rounded-xl bg-[#082248] px-4 py-2 text-sm font-semibold text-white"><Download size={16} />Export</button>}>
      <DataTable columns={["Name", "Code", "Type", "Course", "Status", "Time"]} rows={records.map(r => [r.name, r.code, r.type || "-", r.category, <StatusBadge status={r.status} />, new Date(r.time).toLocaleString()])} empty="No report data available." />
    </Card>
  </PageContainer>;
}

function SettingsPage({ data }) {
  const [profile, setProfile] = data.profile;
  const [courses, setCourses] = data.courses;
  const [batches, setBatches] = data.batches;
  const status = useBackendStatus(profile.backend);
  const [message, setMessage] = useState("");
  const [newCourse, setNewCourse] = useState("");
  const [newBatch, setNewBatch] = useState("");
  const setLogo = event => {
    const file = event.target.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => setProfile({ ...profile, logo: reader.result });
    reader.readAsDataURL(file);
  };
  return <PageContainer title="Settings" subtitle="Enterprise profile, logo, backend URL, sheet sync, batches, and categories.">
    <Card title="Enterprise Settings" action={<StatusBadge status={status === "Online" ? "Completed" : "Pending"} />}>
      <form className="grid gap-4 md:grid-cols-2" onSubmit={e => { e.preventDefault(); setMessage("Settings saved locally."); }}>
        <div className="md:col-span-2 flex flex-col gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between">
          <Brand profile={profile} />
          <label className="inline-flex h-10 cursor-pointer items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 text-sm font-semibold text-[#082248]"><Upload size={16} />Upload logo<input className="hidden" type="file" accept="image/*" onChange={setLogo} /></label>
        </div>
        <FormInput label="Enterprise name" value={profile.enterprise || ""} onChange={e => setProfile({ ...profile, enterprise: e.target.value })} />
        <FormInput label="Admin / owner" value={profile.owner || ""} onChange={e => setProfile({ ...profile, owner: e.target.value })} />
        <FormInput label="Phone" inputMode="numeric" maxLength={10} value={profile.phone || ""} onChange={e => setProfile({ ...profile, phone: onlyNumbers(e.target.value).slice(0, 10) })} />
        <FormInput label="Address" value={profile.address || ""} onChange={e => setProfile({ ...profile, address: e.target.value })} />
        <FormInput label="Backend URL" value={profile.backend || ""} onChange={e => setProfile({ ...profile, backend: e.target.value })} />
        <FormInput label="Google Sheet ID" value={profile.sheet || ""} onChange={e => setProfile({ ...profile, sheet: e.target.value })} />
        <div className="flex flex-col gap-2 md:col-span-2 sm:flex-row">
          <button className="h-11 flex-1 rounded-xl bg-[#082248] font-semibold text-white">Save Settings</button>
          <button type="button" className="h-11 rounded-xl border border-slate-200 px-4 font-semibold text-slate-700" onClick={() => setMessage("")}>Cancel</button>
        </div>
        {message && <p className="md:col-span-2 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">{message}</p>}
      </form>
    </Card>
    <Card title="Create Batch / Category">
      <div className="grid gap-3 md:grid-cols-2">
        <InlineCreate placeholder="Create course / class" value={newCourse} setValue={setNewCourse} onAdd={() => addUnique(newCourse, courses, setCourses, setNewCourse)} />
        <InlineCreate placeholder="Create batch" value={newBatch} setValue={setNewBatch} onAdd={() => addUnique(newBatch, batches, setBatches, setNewBatch)} />
      </div>
    </Card>
  </PageContainer>;
}

function PageContainer({ title, subtitle, children }) {
  return <div className="space-y-5">
    <div>
      <h2 className="text-2xl font-bold tracking-tight text-[#082248] sm:text-3xl">{title}</h2>
      <p className="mt-1 max-w-3xl text-sm text-slate-500">{subtitle}</p>
    </div>
    {children}
  </div>;
}

function Card({ title, action, children }) {
  return <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm sm:p-5">
    <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <h3 className="text-lg font-bold text-[#082248]">{title}</h3>
      {action}
    </div>
    {children}
  </section>;
}

function Notice({ tone = "info", children }) {
  const styles = {
    info: "border-cyan-100 bg-cyan-50 text-cyan-800",
    success: "border-emerald-100 bg-emerald-50 text-emerald-800",
    error: "border-red-100 bg-red-50 text-red-800"
  };
  return <div className={`rounded-xl border px-4 py-3 text-sm font-semibold ${styles[tone]}`}>{children}</div>;
}

function StatCard({ icon: Icon, title, value, description, accent = "navy" }) {
  const styles = {
    navy: "bg-[#082248] text-white",
    cyan: "bg-cyan-50 text-cyan-700",
    gold: "bg-amber-50 text-amber-700",
    red: "bg-red-50 text-red-700"
  };
  return <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
    <div className="flex items-start justify-between gap-3">
      <div>
        <p className="text-sm font-semibold text-slate-500">{title}</p>
        <p className="mt-2 text-3xl font-bold text-[#082248]">{value}</p>
      </div>
      <div className={`grid h-11 w-11 place-items-center rounded-lg ${styles[accent]}`}><Icon size={21} /></div>
    </div>
    <p className="mt-4 text-sm text-slate-500">{description}</p>
  </article>;
}

function MiniMetric({ label, value, tone = "slate" }) {
  const tones = {
    slate: "bg-slate-50 text-slate-700",
    red: "bg-red-50 text-red-700",
    gold: "bg-amber-50 text-amber-700",
    cyan: "bg-cyan-50 text-cyan-700"
  };
  return <div className={`rounded-lg px-3 py-3 ${tones[tone]}`}>
    <p className="text-xs font-bold uppercase tracking-wide opacity-75">{label}</p>
    <p className="mt-1 truncate text-xl font-black">{value}</p>
  </div>;
}

function AudienceTile({ icon: Icon, label, value }) {
  return <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
    <Icon className="text-[#082248]" size={22} />
    <p className="mt-5 text-3xl font-black text-[#082248]">{value}</p>
    <p className="mt-1 text-sm font-semibold text-slate-500">{label}</p>
  </div>;
}

function DataTable({ columns, rows, empty }) {
  return <div className="overflow-hidden rounded-xl border border-slate-200">
    <div className="hidden overflow-x-auto md:block">
      <table className="min-w-full divide-y divide-slate-200 text-sm">
        <thead className="bg-slate-50">{columns.map(column => <th key={column} className="px-4 py-3 text-left font-bold text-slate-500">{column}</th>)}</thead>
        <tbody className="divide-y divide-slate-100 bg-white">{rows.map((row, index) => <tr key={index}>{row.map((cell, cellIndex) => <td key={cellIndex} className="px-4 py-3 align-middle text-slate-700">{cell}</td>)}</tr>)}</tbody>
      </table>
    </div>
    <div className="grid gap-3 bg-slate-50 p-3 md:hidden">
      {rows.map((row, index) => <div key={index} className="rounded-xl border border-slate-200 bg-white p-3 shadow-sm">
        {row.map((cell, cellIndex) => <div key={cellIndex} className="flex items-start justify-between gap-3 border-b border-slate-100 py-2 last:border-0">
          <span className="text-xs font-bold uppercase text-slate-400">{columns[cellIndex]}</span>
          <span className="text-right text-sm font-medium text-slate-700">{cell}</span>
        </div>)}
      </div>)}
    </div>
    {!rows.length && <div className="bg-white px-4 py-8 text-center text-sm text-slate-500">{empty}</div>}
  </div>;
}

function FormInput({ label, className = "", ...props }) {
  return <label className={`grid gap-1.5 ${className}`}>
    <span className="text-sm font-semibold text-slate-700">{label}</span>
    <input className="h-11 rounded-xl border border-slate-200 bg-white px-3 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#082248] focus:ring-4 focus:ring-slate-200" {...props} />
  </label>;
}

function FormSelect({ label, options, ...props }) {
  return <label className="grid gap-1.5">
    <span className="text-sm font-semibold text-slate-700">{label}</span>
    <select className="h-11 rounded-xl border border-slate-200 bg-white px-3 text-slate-900 outline-none transition focus:border-[#082248] focus:ring-4 focus:ring-slate-200" {...props}>{options.map(option => <option key={option}>{option}</option>)}</select>
  </label>;
}

function FieldRenderer({ fieldKey, label, kind, form, setForm, courses, batches }) {
  const setValue = value => setForm({ ...form, [fieldKey]: value });
  if (kind === "select:courses") return <FormSelect label={label} value={form[fieldKey] || ""} onChange={e => setValue(e.target.value)} options={courses} />;
  if (kind === "select:batches") return <FormSelect label={label} value={form[fieldKey] || ""} onChange={e => setValue(e.target.value)} options={batches} />;
  if (kind === "select:status") return <FormSelect label={label} value={form[fieldKey] || "Active"} onChange={e => setValue(e.target.value)} options={["Active", "Pending", "Inactive"]} />;
  if (kind === "select:face") return <FormSelect label={label} value={form[fieldKey] || "Pending"} onChange={e => setValue(e.target.value)} options={["Pending", "Completed"]} />;
  if (kind === "textarea") return <label className="grid gap-1.5 md:col-span-2"><span className="text-sm font-semibold text-slate-700">{label}</span><textarea className="min-h-24 rounded-xl border border-slate-200 bg-white px-3 py-3 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-[#082248] focus:ring-4 focus:ring-slate-200" value={form[fieldKey] || ""} onChange={e => setValue(e.target.value)} placeholder="Optional notes" /></label>;
  const isPhone = fieldKey === "phone";
  return <FormInput label={label} type={kind === "date" ? "date" : kind === "email" ? "email" : "text"} placeholder={label} inputMode={isPhone ? "numeric" : undefined} maxLength={isPhone ? 10 : undefined} value={form[fieldKey] || ""} onChange={e => setValue(isPhone ? onlyNumbers(e.target.value).slice(0, 10) : e.target.value)} required={["code", "name", "phone"].includes(fieldKey)} />;
}

function CameraPanel({ title, subtitle }) {
  return <Card title={title} action={<StatusBadge status="Active" />}>
    <div className="overflow-hidden rounded-lg border border-slate-200 bg-slate-950">
      <div className="aspect-[4/3] w-full sm:aspect-video">
        <div className="grid h-full place-items-center bg-slate-900 text-center text-white">
          <div>
            <Camera className="mx-auto mb-3 text-cyan-300" size={42} />
            <p className="text-lg font-bold">{subtitle}</p>
            <p className="text-sm text-slate-300">Camera preview area</p>
          </div>
        </div>
      </div>
    </div>
  </Card>;
}

function StatusBadge({ status }) {
  const classes = {
    Active: "bg-emerald-50 text-emerald-700",
    Completed: "bg-emerald-50 text-emerald-700",
    Present: "bg-emerald-50 text-emerald-700",
    Pending: "bg-amber-50 text-amber-700",
    Late: "bg-amber-50 text-amber-700",
    Absent: "bg-red-50 text-red-700",
    Unknown: "bg-slate-100 text-slate-600",
    "Already Marked": "bg-cyan-50 text-cyan-700"
  };
  return <span className={`inline-flex min-h-7 items-center rounded-full px-3 text-xs font-bold ${classes[status] || "bg-slate-100 text-slate-600"}`}>{status}</span>;
}

function ListTools({ q, setQ, filter, setFilter }) {
  return <div className="grid w-full gap-2 sm:w-auto sm:grid-cols-[220px_140px]">
    <label className="flex h-10 items-center gap-2 rounded-xl border border-slate-200 px-3"><Search size={16} className="text-slate-400" /><input className="min-w-0 flex-1 bg-transparent text-sm outline-none" placeholder="Search" value={q} onChange={e => setQ(e.target.value)} /></label>
    <select className="h-10 rounded-xl border border-slate-200 px-3 text-sm outline-none" value={filter} onChange={e => setFilter(e.target.value)}><option>All</option><option>Active</option><option>Pending</option></select>
  </div>;
}

function InlineCreate({ placeholder, value, setValue, onAdd }) {
  return <div className="grid gap-2 sm:grid-cols-[1fr_auto]">
    <input className="h-11 rounded-xl border border-slate-200 px-3 outline-none focus:border-[#082248] focus:ring-4 focus:ring-slate-200" placeholder={placeholder} value={value} onChange={e => setValue(e.target.value)} />
    <button className="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-slate-200 px-4 font-semibold text-[#082248] hover:bg-slate-50" type="button" onClick={onAdd}><Plus size={16} />Add</button>
  </div>;
}

function Brand({ profile }) {
  const enterprise = profile?.enterprise || "Vernex Gen Technologies";
  const words = enterprise.split(/\s+/);
  return <div className="flex min-w-0 items-center gap-3">
    {profile?.logo ? <img className="h-12 w-12 rounded-xl border border-slate-200 object-cover" src={profile.logo} alt="" /> : <div className="grid h-12 w-12 shrink-0 place-items-center rounded-xl bg-[#082248] text-xl font-black text-[#c89736]">{enterprise[0] || "V"}</div>}
    <div className="min-w-0">
      <p className="truncate text-xl font-black uppercase tracking-[0.16em] text-[#082248]">{words[0] || "Vernex"}</p>
      <p className="truncate text-xs font-semibold uppercase tracking-[0.18em] text-[#c89736]">{words.slice(1).join(" ") || "Gen Technologies"}</p>
    </div>
  </div>;
}

function MobileDashboard({ data }) {
  const [[people, setPeople], [sessions], [records, setRecords], [profile], [task, setTask]] = [data.people, data.sessions, data.records, data.profile, data.task];
  const camera = useCamera();
  const video = camera.ref;
  const now = useClock();
  const [currentStep, setCurrentStep] = useState("front");
  const [progress, setProgress] = useState(0);
  const [warning, setWarning] = useState("");
  const [done, setDone] = useState(false);
  const [busy, setBusy] = useState(false);
  const [started, setStarted] = useState(false);
  const [stepStartedAt, setStepStartedAt] = useState(Date.now());
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const mode = params.get("mode");
    if (!mode) return;
    setTask({
      mode,
      personId: Number(params.get("personId")) || undefined,
      sessionId: Number(params.get("sessionId")) || undefined,
      category: params.get("category") || undefined,
      durationSeconds: Number(params.get("durationSeconds")) || undefined,
      createdAt: Number(params.get("createdAt")) || Date.now()
    });
  }, [setTask]);
  const person = people.find(p => p.id === task?.personId);
  const session = sessions.find(s => s.id === task?.sessionId);
  const mark = () => {
    const p = people.find(x => x.category === task?.category) || people[0];
    setRecords([{ id: crypto.randomUUID(), name: p?.name || "Unknown", code: p?.code || "-", type: p?.type || "-", category: task?.category || "-", status: p ? "Present" : "Unknown", confidence: p ? 94 : 0, time: new Date().toISOString() }, ...records]);
  };
  const captureStep = async () => {
    if (!person || !video.current || busy || done) return;
    setBusy(true);
    setWarning("");
    console.log("selected person_id", person.id);
    console.log("current_step", currentStep);
    try {
      const blob = await captureVideoFrame(video.current);
      const form = new FormData();
      form.append("person_id", person.id);
      form.append("current_step", currentStep);
      form.append("has_specs", currentStep === "with_specs" ? "true" : "false");
      form.append("image", blob, `${currentStep}.jpg`);
      console.log("request status", "uploading");
      const response = await sendEnrollmentFrame(form);
      console.log("API response", response);
      setProgress(response.progress_percentage || 0);
      if (response.warning) setWarning(response.warning);
      if (response.completed) {
        signalCaptured();
        setDone(true);
        setStarted(false);
        setPeople(people.map(p => p.id === person.id ? { ...p, enrolled: true, faceStatus: "Completed" } : p));
      } else {
        signalCaptured();
        setCurrentStep(response.next_step || currentStep);
        setStepStartedAt(Date.now());
      }
    } catch (err) {
      console.log("warning/error", err.message);
      setWarning(err.message || "Capture failed.");
    } finally {
      setBusy(false);
    }
  };
  useEffect(() => {
    if (!started || done || task?.mode !== "enroll") return;
    const id = setInterval(() => {
      if (Date.now() - stepStartedAt > 20000) setWarning("Adjust your face and try again");
      captureStep();
    }, 1000);
    return () => clearInterval(id);
  }, [started, done, task?.mode, currentStep, busy, stepStartedAt]);
  const remaining = task?.mode === "attendance" ? Math.max(0, Number(task.durationSeconds || 0) - Math.floor((now - task.createdAt) / 1000)) : 0;
  return <main className="mx-auto min-h-screen max-w-xl bg-white p-5">
    <Brand profile={profile} />
    <h1 className="mt-6 text-2xl font-bold text-[#082248]">{profile.enterprise}</h1>
    {!task && <MobileCamera title="Waiting for admin" subtitle="Enrollment or attendance will start here automatically." />}
    {task?.mode === "enroll" && <MobileCamera video={video} cameraError={camera.error} title={done ? "Enrollment completed" : stepInstruction(currentStep)} subtitle={person ? `${person.name} - ${person.code} - ${progress}%` : "Waiting for admin"} action={done ? "Completed" : started ? busy ? "Checking..." : "Auto capturing..." : "Start Enrollment"} onClick={() => { setStarted(true); setStepStartedAt(Date.now()); }} done={done} warning={warning} />}
    {task?.mode === "attendance" && <MobileCamera video={video} title={session?.name || "Attendance Session"} subtitle={`Timer: ${formatDuration(remaining)}`} action="Mark Attendance" onClick={mark} />}
    <div className="mt-5 flex items-center justify-center gap-2 text-sm text-slate-500"><Wifi size={15} /> Same Wi-Fi local device</div>
  </main>;
}

function MobileCamera({ video, cameraError, title, subtitle, action, onClick, done, warning }) {
  return <section className="mt-5 rounded-lg border border-slate-200 bg-slate-50 p-4">
    <h2 className="text-xl font-bold text-[#082248]">{title}</h2>
    <p className="mt-1 text-sm text-slate-500">{subtitle}</p>
    <div className="relative mt-4 aspect-[3/4] overflow-hidden rounded-lg bg-slate-950">
      {video ? <video className="h-full w-full scale-x-[-1] object-cover" ref={video} autoPlay playsInline muted /> : <div className="grid h-full place-items-center text-white"><Camera size={34} /></div>}
      <div className="pointer-events-none absolute inset-[16%] rounded-full border-2 border-white/90" />
    </div>
    {cameraError && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-sm font-semibold text-red-700">{cameraError}</p>}
    {warning && <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-sm font-semibold text-amber-700">{warning}</p>}
    {action && <button disabled={done || action === "Checking..." || action === "Auto capturing..."} className="mt-4 inline-flex h-11 w-full items-center justify-center gap-2 rounded-xl bg-[#082248] font-semibold text-white disabled:opacity-60" onClick={onClick}>{done ? <Check size={17} /> : <Camera size={17} />}{done ? "Completed" : action}</button>}
  </section>;
}

function countType(people, type) { return people.filter(p => p.type === type).length; }
function summaryFor(people, records, type) { return records.filter(r => r.type === type && r.status === "Present").length || `${countType(people, type)} users`; }
function addUnique(value, values, setValues, reset) { const v = value.trim(); if (!v || values.some(x => x.toLowerCase() === v.toLowerCase())) return; setValues([...values, v]); reset(""); }
function onlyNumbers(value) { return value.replace(/\D/g, ""); }
function formatDuration(seconds) { const s = Math.max(0, Number(seconds) || 0); return `${Math.floor(s / 60)}m ${String(s % 60).padStart(2, "0")}s`; }
function stepInstruction(step) {
  return ({ front: "Look straight", left: "Move face slightly left", right: "Move face slightly right", close: "Move face closer", far: "Move face backward", with_specs: "Optional with spectacles" })[step] || "Enrollment completed";
}
function captureVideoFrame(video) {
  return new Promise((resolve, reject) => {
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth || 640;
    canvas.height = video.videoHeight || 480;
    canvas.getContext("2d").drawImage(video, 0, 0, canvas.width, canvas.height);
    canvas.toBlob(blob => blob ? resolve(blob) : reject(new Error("Unable to capture frame.")), "image/jpeg", 0.9);
  });
}
function buildMobileLink(task, backendUrl) {
  const host = getNetworkHost(backendUrl);
  const origin = host ? `${location.protocol}//${host}:${location.port || "5173"}` : location.origin;
  const url = new URL(origin + "/mobile");
  Object.entries(task).forEach(([key, value]) => value !== undefined && url.searchParams.set(key, value));
  return url.toString();
}
function getNetworkHost(backendUrl) {
  try {
    const host = new URL(backendUrl).hostname;
    return host === "localhost" || host === "127.0.0.1" ? "" : host;
  } catch {
    return "";
  }
}
function signalCaptured() {
  navigator.vibrate?.(120);
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.frequency.value = 880;
    gain.gain.value = 0.08;
    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start();
    setTimeout(() => { osc.stop(); ctx.close(); }, 120);
  } catch {}
}
function titleCase(value) { return value ? value.charAt(0).toUpperCase() + value.slice(1) : ""; }
function toUiType(value) { return titleCase(value || "student"); }
function toApiType(value) { return String(value || "student").toLowerCase(); }
function toUiStatus(value) {
  const normalized = String(value || "active").toLowerCase();
  if (normalized === "not_started" || normalized === "in_progress") return "Pending";
  if (normalized === "completed") return "Completed";
  return titleCase(normalized);
}
function toApiFaceStatus(value) {
  return String(value || "").toLowerCase() === "completed" ? "completed" : "not_started";
}
function mapApiPerson(person) {
  const type = toUiType(person.person_type);
  return {
    ...person,
    id: person.id,
    code: person.person_code || "",
    name: person.full_name || "",
    phone: person.guardian_phone || person.phone || "",
    type,
    parentName: person.guardian_name || "",
    email: person.email || "",
    designation: person.designation || "",
    department: person.department || "",
    membershipType: person.membership_type || "",
    planName: person.plan_name || "",
    level: person.level_class || "",
    timing: person.timing_id || "",
    joiningDate: person.joining_date || "",
    notes: person.notes || "",
    category: person.category_program || "",
    batch: person.batch_name || "",
    status: toUiStatus(person.status),
    faceStatus: toUiStatus(person.face_enrollment_status),
    enrolled: person.face_enrollment_status === "completed"
  };
}
function mapApiTiming(timing) {
  return {
    ...timing,
    id: timing.id,
    name: timing.name || "Timing",
    category: timing.category_program || "",
    batch: timing.batch_name || "",
    start: timing.start_time || "",
    state: timing.status === "active" ? "Idle" : toUiStatus(timing.status),
    durationSeconds: 2700
  };
}
function mapApiAttendance(record) {
  return {
    ...record,
    id: record.id,
    name: record.person_name || "Unknown",
    code: record.person_code || "-",
    type: toUiType(record.person_type || ""),
    category: record.category_program || "-",
    batch: record.batch_name || "-",
    status: toUiStatus(record.status),
    confidence: Math.round(Number(record.confidence_score || 0) * 100) || 0,
    time: record.marked_time || record.created_at || new Date().toISOString()
  };
}
function toPersonPayload(form, type) {
  const personType = toApiType(type);
  return {
    person_code: form.code,
    full_name: form.name,
    phone: personType === "student" ? null : form.phone || null,
    email: form.email || null,
    person_type: personType,
    guardian_name: form.parentName || null,
    guardian_phone: personType === "student" ? form.phone || null : null,
    category_program: form.category || null,
    batch_name: form.batch || null,
    level_class: form.level || null,
    designation: form.designation || null,
    department: form.department || null,
    membership_type: form.membershipType || null,
    plan_name: form.planName || null,
    timing_id: form.timing ? Number(form.timing) : null,
    joining_date: form.joiningDate || form.startDate || null,
    status: String(form.status || "Active").toLowerCase(),
    face_enrollment_status: toApiFaceStatus(form.faceStatus),
    notes: form.notes || null
  };
}
function useClock() { const [t, setT] = useState(new Date()); useEffect(() => { const id = setInterval(() => setT(new Date()), 1000); return () => clearInterval(id); }, []); return t; }
function useBackendStatus(url) {
  const [status, setStatus] = useState("Checking");
  useEffect(() => {
    if (!url) { setStatus("Offline"); return; }
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), 1400);
    fetch(`${url.replace(/\/$/, "")}/health`, { signal: controller.signal }).then(response => setStatus(response.ok ? "Online" : "Offline")).catch(() => setStatus("Offline")).finally(() => clearTimeout(id));
    return () => { controller.abort(); clearTimeout(id); };
  }, [url]);
  return status;
}
function useCamera() {
  const ref = useRef(null);
  const [error, setError] = useState("");
  useEffect(() => {
    let stream;
    navigator.mediaDevices?.getUserMedia({ video: { facingMode: "user" } })
      .then(s => {
        stream = s;
        setError("");
        if (ref.current) ref.current.srcObject = s;
      })
      .catch(err => setError(`Camera not opened: ${err.message || "permission denied"}. Allow camera permission or use HTTPS/local HTTPS tunnel on phone.`));
    return () => stream?.getTracks().forEach(track => track.stop());
  }, []);
  return { ref, error };
}

createRoot(document.getElementById("root")).render(<App />);
