"use client";

import { useEffect, useState } from "react";

type UserSummary = {
  id: number;
  name: string;
  email: string;
  role: string;
  department: string;
};

type Analytics = {
  total_documents: number;
  total_chunks: number;
  total_queries: number;
  total_feedback: number;
  low_confidence_queries: number;
  helpful_feedback: number;
  incorrect_feedback: number;
  incomplete_feedback: number;
};

type DocumentItem = {
  id: number;
  title: string;
  filename: string;
  document_type: string;
  department: string;
  version: string;
  approved: boolean;
  upload_date: string;
};

type ChatCitation = {
  document_id: number;
  document_title: string;
  department: string;
  version: string;
  snippet: string;
  chunk_index: number;
  score: number;
};

type ChatResponse = {
  query_id: number;
  answer: string;
  citations: ChatCitation[];
  confidence: number;
  follow_up_suggestions: string[];
  action_items: string[];
  fallback_used: boolean;
  answered_at: string;
};

type ViewName = "overview" | "library" | "chat" | "analytics";

const demoUsers = [
  { label: "Admin demo", email: "admin@copilot.local", password: "admin123" },
  { label: "Employee demo", email: "employee@copilot.local", password: "employee123" },
  { label: "Viewer demo", email: "viewer@copilot.local", password: "viewer123" }
];

const apiBaseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export function WorkspaceClient() {
  const [view, setView] = useState<ViewName>("overview");
  const [email, setEmail] = useState(demoUsers[0].email);
  const [password, setPassword] = useState(demoUsers[0].password);
  const [user, setUser] = useState<UserSummary | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [question, setQuestion] = useState("What does the onboarding playbook require before a new hire starts?");
  const [departmentFilter, setDepartmentFilter] = useState("People Ops");
  const [chatResponse, setChatResponse] = useState<ChatResponse | null>(null);
  const [status, setStatus] = useState("Sign in with one of the seeded demo users.");
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  useEffect(() => {
    if (!user) {
      return;
    }
    void Promise.all([loadDocuments(user.email), loadAnalytics(user)]).then(() => {
      setStatus(`Signed in as ${user.name}.`);
    });
  }, [user]);

  async function signIn() {
    setStatus("Signing in...");
    const response = await fetch(`${apiBaseUrl}/api/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password })
    });
    if (!response.ok) {
      setStatus("Sign-in failed. Check the seeded credentials in the demo card.");
      return;
    }
    const data = await response.json();
    setUser(data.user);
  }

  async function loadDocuments(userEmail: string) {
    const response = await fetch(`${apiBaseUrl}/api/documents/`, {
      headers: { "X-User-Email": userEmail }
    });
    if (!response.ok) {
      return;
    }
    const data = await response.json();
    setDocuments(data.items);
  }

  async function loadAnalytics(currentUser: UserSummary) {
    if (currentUser.role !== "admin") {
      setAnalytics(null);
      return;
    }
    const response = await fetch(`${apiBaseUrl}/api/analytics/overview`, {
      headers: { "X-User-Email": currentUser.email }
    });
    if (!response.ok) {
      setAnalytics(null);
      return;
    }
    setAnalytics(await response.json());
  }

  async function askQuestion() {
    if (!user) {
      return;
    }
    setStatus("Running grounded retrieval...");
    const response = await fetch(`${apiBaseUrl}/api/chat/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Email": user.email
      },
      body: JSON.stringify({
        question,
        department: departmentFilter || null
      })
    });
    if (!response.ok) {
      setStatus("The backend could not answer this query.");
      return;
    }
    const data = await response.json();
    setChatResponse(data);
    setView("chat");
    setStatus(`Query answered with confidence ${data.confidence}.`);
    await loadAnalytics(user);
  }

  async function submitFeedback(rating: string) {
    if (!user || !chatResponse) {
      return;
    }
    const response = await fetch(`${apiBaseUrl}/api/feedback/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-User-Email": user.email
      },
      body: JSON.stringify({
        chat_query_id: chatResponse.query_id,
        rating,
        notes: `Submitted from the frontend demo as ${rating}.`
      })
    });
    if (response.ok) {
      setStatus(`Stored ${rating} feedback for query ${chatResponse.query_id}.`);
      await loadAnalytics(user);
    }
  }

  async function uploadDocument() {
    if (!user || user.role !== "admin" || !uploadFile) {
      return;
    }
    setUploadMessage("Uploading document...");
    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("department", departmentFilter || "Operations");
    formData.append("version", "1.0");
    formData.append("document_type", "policy");
    formData.append("approved", "true");

    const response = await fetch(`${apiBaseUrl}/api/documents/upload`, {
      method: "POST",
      headers: { "X-User-Email": user.email },
      body: formData
    });

    if (!response.ok) {
      setUploadMessage("Upload failed.");
      return;
    }

    const data = await response.json();
    setUploadMessage(`Uploaded ${data.title} with ${data.chunks_created} chunks.`);
    setUploadFile(null);
    await loadDocuments(user.email);
    await loadAnalytics(user);
  }

  const metrics = analytics
    ? [
        { label: "Documents", value: analytics.total_documents },
        { label: "Chunks", value: analytics.total_chunks },
        { label: "Queries", value: analytics.total_queries },
        { label: "Low confidence", value: analytics.low_confidence_queries }
      ]
    : [
        { label: "Documents", value: documents.length },
        { label: "Role", value: user?.role ?? "guest" },
        { label: "Department", value: user?.department ?? "unassigned" },
        { label: "Status", value: user ? "live" : "demo" }
      ];

  return (
    <main className="page-shell">
      <section className="hero">
        <div className="panel hero-card">
          <div className="eyebrow">Enterprise AI Workspace</div>
          <h1>Internal Knowledge Copilot</h1>
          <p>
            Upload internal policy docs, run grounded retrieval over approved content, and return
            answers with citations, confidence, follow-up suggestions, and action items.
          </p>
          <div className="hero-badges">
            <span className="badge">Role-aware access</span>
            <span className="badge">Grounded answers</span>
            <span className="badge">Feedback capture</span>
            <span className="badge">Audit-friendly logs</span>
          </div>
        </div>

        <div className="panel login-card">
          <h2>Demo Sign-In</h2>
          <p className="muted">Use one of the seeded demo accounts from the backend.</p>
          <select
            className="select"
            value={email}
            onChange={(event) => {
              const selected = demoUsers.find((item) => item.email === event.target.value);
              setEmail(event.target.value);
              if (selected) {
                setPassword(selected.password);
              }
            }}
          >
            {demoUsers.map((item) => (
              <option key={item.email} value={item.email}>
                {item.label}
              </option>
            ))}
          </select>
          <input className="field" value={email} onChange={(event) => setEmail(event.target.value)} />
          <input
            className="field"
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
          <div className="actions">
            <button className="button" onClick={() => void signIn()}>
              Sign In
            </button>
            {user ? (
              <button
                className="button ghost"
                onClick={() => {
                  setUser(null);
                  setAnalytics(null);
                  setChatResponse(null);
                  setStatus("Signed out.");
                }}
              >
                Sign Out
              </button>
            ) : null}
          </div>
          <div className="muted">{status}</div>
        </div>
      </section>

      {user ? (
        <section className="grid">
          <aside className="panel sidebar">
            <div className="brand">
              <strong>{user.name}</strong>
              <span className="muted">
                {user.role} · {user.department}
              </span>
            </div>
            <div className="nav">
              <button className={view === "overview" ? "active" : ""} onClick={() => setView("overview")}>
                Overview
              </button>
              <button className={view === "library" ? "active" : ""} onClick={() => setView("library")}>
                Knowledge Library
              </button>
              <button className={view === "chat" ? "active" : ""} onClick={() => setView("chat")}>
                Chat Workspace
              </button>
              {user.role === "admin" ? (
                <button className={view === "analytics" ? "active" : ""} onClick={() => setView("analytics")}>
                  Admin Analytics
                </button>
              ) : null}
            </div>
          </aside>

          <div className="workspace">
            <section className="metrics">
              {metrics.map((item) => (
                <article className="panel metric-card" key={item.label}>
                  <div className="metric-label">{item.label}</div>
                  <div className="metric-value">{item.value}</div>
                </article>
              ))}
            </section>

            {view === "overview" ? (
              <section className="content-grid">
                <article className="panel content-card">
                  <div className="section-header">
                    <h2>Command Center</h2>
                  </div>
                  <p className="muted">
                    This workspace is tuned for grounded internal knowledge flows. Admins can upload
                    documents, employees can ask policy questions, and everyone sees source-backed answers.
                  </p>
                  <div className="actions">
                    <button className="button" onClick={() => setView("chat")}>
                      Open Chat
                    </button>
                    <button className="button secondary" onClick={() => setView("library")}>
                      Review Documents
                    </button>
                  </div>
                </article>

                <article className="panel content-card">
                  <div className="section-header">
                    <h2>Suggested Questions</h2>
                  </div>
                  <ul className="list">
                    <li className="list-item">What is the incident escalation window for high-severity issues?</li>
                    <li className="list-item">What should managers finish before a new hire starts?</li>
                    <li className="list-item">Which department owns quarterly access reviews?</li>
                  </ul>
                </article>
              </section>
            ) : null}

            {view === "library" ? (
              <section className="stack">
                <article className="panel content-card">
                  <div className="section-header">
                    <h2>Knowledge Library</h2>
                    <span className="muted">{documents.length} documents indexed</span>
                  </div>
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Title</th>
                        <th>Department</th>
                        <th>Type</th>
                        <th>Version</th>
                        <th>Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {documents.map((item) => (
                        <tr key={item.id}>
                          <td>{item.title}</td>
                          <td>{item.department}</td>
                          <td>{item.document_type}</td>
                          <td>{item.version}</td>
                          <td>{item.approved ? "Approved" : "Pending"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </article>

                {user.role === "admin" ? (
                  <article className="panel content-card">
                    <div className="section-header">
                      <h2>Upload Document</h2>
                      <span className="muted">Admin only</span>
                    </div>
                    <div className="stack">
                      <input
                        className="field"
                        type="file"
                        onChange={(event) => setUploadFile(event.target.files?.[0] ?? null)}
                      />
                      <input
                        className="field"
                        value={departmentFilter}
                        onChange={(event) => setDepartmentFilter(event.target.value)}
                        placeholder="Department"
                      />
                      <div className="actions">
                        <button className="button" onClick={() => void uploadDocument()}>
                          Upload
                        </button>
                      </div>
                      <div className="muted">{uploadMessage}</div>
                    </div>
                  </article>
                ) : null}
              </section>
            ) : null}

            {view === "chat" ? (
              <section className="chat-layout">
                <article className="panel content-card stack">
                  <div className="section-header">
                    <h2>Grounded Chat</h2>
                    <span className="muted">Only answers from retrieved knowledge</span>
                  </div>
                  <textarea
                    className="textarea"
                    value={question}
                    onChange={(event) => setQuestion(event.target.value)}
                  />
                  <input
                    className="field"
                    value={departmentFilter}
                    onChange={(event) => setDepartmentFilter(event.target.value)}
                    placeholder="Optional department filter"
                  />
                  <div className="actions">
                    <button className="button" onClick={() => void askQuestion()}>
                      Ask Question
                    </button>
                  </div>
                  {chatResponse ? (
                    <div className="answer-box">
                      <div className="eyebrow">Answer</div>
                      <p>{chatResponse.answer}</p>
                      <p className={chatResponse.fallback_used ? "danger-text" : "muted"}>
                        Confidence: {chatResponse.confidence} ·{" "}
                        {chatResponse.fallback_used ? "Fallback response" : "Grounded response"}
                      </p>
                    </div>
                  ) : null}
                </article>

                <article className="stack">
                  <div className="panel content-card">
                    <div className="section-header">
                      <h2>Citations</h2>
                    </div>
                    <ul className="list">
                      {chatResponse?.citations.map((item) => (
                        <li className="list-item" key={`${item.document_id}-${item.chunk_index}`}>
                          <strong>{item.document_title}</strong>
                          <div className="muted">
                            {item.department} · v{item.version} · score {item.score}
                          </div>
                          <p>{item.snippet}</p>
                        </li>
                      )) ?? <li className="list-item">Run a query to populate source citations.</li>}
                    </ul>
                  </div>

                  <div className="panel content-card">
                    <div className="section-header">
                      <h2>Next Steps</h2>
                    </div>
                    <ul className="list">
                      {chatResponse?.follow_up_suggestions.map((item) => (
                        <li className="list-item" key={item}>
                          {item}
                        </li>
                      )) ?? <li className="list-item">Follow-up suggestions will appear here.</li>}
                    </ul>
                    <div className="actions">
                      <button className="button secondary" onClick={() => void submitFeedback("helpful")}>
                        Helpful
                      </button>
                      {user.role !== "viewer" ? (
                        <>
                          <button className="button secondary" onClick={() => void submitFeedback("incorrect")}>
                            Incorrect
                          </button>
                          <button className="button secondary" onClick={() => void submitFeedback("incomplete")}>
                            Incomplete
                          </button>
                        </>
                      ) : null}
                    </div>
                  </div>
                </article>
              </section>
            ) : null}

            {view === "analytics" && user.role === "admin" ? (
              <section className="content-grid">
                <article className="panel content-card">
                  <div className="section-header">
                    <h2>Quality Signals</h2>
                  </div>
                  <ul className="list">
                    <li className="list-item">Helpful feedback: {analytics?.helpful_feedback ?? 0}</li>
                    <li className="list-item">Incorrect feedback: {analytics?.incorrect_feedback ?? 0}</li>
                    <li className="list-item">Incomplete feedback: {analytics?.incomplete_feedback ?? 0}</li>
                  </ul>
                </article>

                <article className="panel content-card">
                  <div className="section-header">
                    <h2>Admin Notes</h2>
                  </div>
                  <p className="muted">
                    Low-confidence activity should trigger review of missing source coverage, prompt wording,
                    and approval status for uploaded documents.
                  </p>
                </article>
              </section>
            ) : null}
          </div>
        </section>
      ) : null}
    </main>
  );
}
