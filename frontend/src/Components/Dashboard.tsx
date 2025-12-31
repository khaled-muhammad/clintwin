import { Camera, History, Settings, ScanSearch, Activity, Pill, User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import logo from "../assets/logo.png";

export default function ProfessionalDashboard() {
  const navigate = useNavigate();
  return (
    <div className="w-full min-h-screen bg-gray-50 p-4 flex flex-col items-center text-gray-800">
      {/* Header */}
      <div className="w-full max-w-sm flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <img src={logo} alt="ClinTwin Logo" className="w-8 h-8" />
          <h1 className="text-lg font-semibold">Professional Dashboard</h1>
        </div>
        <User className="w-8 h-8 bg-gray-200 rounded-full" />
      </div>

      {/* Stats Row */}
      <div className="w-full max-w-sm grid grid-cols-3 gap-2 mb-4">
        <div className="bg-white p-3 rounded-xl shadow">
          <p className="text-xs text-gray-500">Identifications Today</p>
          <p className="text-xl font-bold">142</p>
          <p className="text-green-500 text-xs">+10%</p>
        </div>
        <div className="bg-white p-3 rounded-xl shadow">
          <p className="text-xs text-gray-500">Interactions Found</p>
          <p className="text-xl font-bold">8</p>
          <p className="text-red-500 text-xs">-5%</p>
        </div>
        <div className="bg-white p-3 rounded-xl shadow">
          <p className="text-xs text-gray-500">Errors Avoided</p>
          <p className="text-xl font-bold">5</p>
          <p className="text-red-500 text-xs">+2 This week</p>
        </div>
      </div>

      {/* Trend Chart Placeholder */}
      <div className="w-full max-w-sm bg-white p-4 rounded-xl shadow mb-4">
        <div className="flex gap-3 mb-2">
          <button className="text-sm font-semibold border-b-2 border-black">Weekly</button>
          <button className="text-sm text-gray-500">Monthly</button>
        </div>
        <div className="w-full h-28 bg-gray-200 rounded-lg" />
        <div className="flex justify-between mt-2 text-xs text-gray-500">
          <span>Mon</span><span>Tue</span><span>Wed</span><span>Thu</span><span>Fri</span><span>Sat</span><span>Sun</span>
        </div>
      </div>

      {/* Quick Access */}
      <div className="w-full max-w-sm grid grid-cols-3 gap-3 mb-4">
        <button className="bg-teal-600 text-white p-3 rounded-xl shadow flex flex-col items-center gap-1" onClick={() => navigate("/pharmacy/camera")}>
          <Camera size={20} />
          New Scan
        </button>
        <button className="bg-white p-3 rounded-xl shadow flex flex-col items-center gap-1" onClick={() => navigate("/pharmacy/drug-input")}>
          <Activity size={20} />
          Interaction
        </button>
        <button className="bg-white p-3 rounded-xl shadow flex flex-col items-center gap-1" onClick={() => navigate("/")}>
          <History size={20} />
          Full History
        </button>
      </div>

      {/* Recent Patient History */}
      <div className="w-full max-w-sm">
        <h2 className="text-md font-semibold mb-2">Recent Patient History</h2>

        {[{ id: 12345, d: "3 drugs, 1 interaction", t: "2h ago" }, { id: 67890, d: "5 drugs, 0 interactions", t: "5h ago" }, { id: 11223, d: "2 drugs, 1 interaction", t: "Yesterday" }].map((p) => (
          <div key={p.id} className="bg-white p-3 rounded-xl shadow mb-2 flex items-center gap-3">
            <div className="w-8 h-8 bg-teal-100 rounded-full flex items-center justify-center">
              <Pill size={16} />
            </div>
            <div className="flex-1">
              <p className="text-sm font-medium">Patient ID: {p.id}</p>
              <p className="text-xs text-gray-500">{p.d}</p>
            </div>
            <p className="text-xs text-gray-500">{p.t}</p>
          </div>
        ))}
      </div>

      {/* Bottom Nav */}
      <div className="fixed bottom-0 w-full max-w-sm bg-white flex justify-around py-3 shadow-inner">
        <button className="text-teal-600 font-semibold flex flex-col items-center text-xs" onClick={() => navigate("/pharmacy/dashboard")}><ScanSearch size={18} />Dashboard</button>
        <button className="text-gray-500 flex flex-col items-center text-xs" onClick={() => navigate("/pharmacy/camera")}><Camera size={18} />Scan</button>
        <button className="text-gray-500 flex flex-col items-center text-xs" onClick={() => navigate("/")}><History size={18} />History</button>
        <button className="text-gray-500 flex flex-col items-center text-xs" onClick={() => navigate("/permissions/language")}><Settings size={18} />Settings</button>
      </div>
    </div>
  );
}
