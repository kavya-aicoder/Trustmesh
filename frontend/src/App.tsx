import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import Identities from "./pages/Identities";
import Dashboard from "./pages/Dashboard";
import Login from "./pages/Login";
import Policies from "./pages/Policies";
import Resources from "./pages/Resources";
import Assets from "./pages/Assets";
import Security from "./pages/Security";
import Recovery from "./pages/Recovery";


function Placeholder({ title }: { title: string }) {
  return (
    <div className="app-shell">
      <div className="main-area">
        <main className="dashboard">
          <div className="eyebrow">TRUSTLAYER</div>
          <h1>{title}</h1>
          <p>Module under construction.</p>
        </main>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/identities" element={<Identities />} />
        <Route path="/policies" element={<Policies />} />
        <Route path="/resources" element={<Resources />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/audit" element={<Placeholder title="Audit Log" />} />
        <Route path="/security" element={<Security />} />
        <Route path="/recovery" element={<Recovery />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;