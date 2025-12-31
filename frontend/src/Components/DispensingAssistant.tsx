// Removed shadcn/ui imports
// Using plain Tailwind components instead

import { Pill, Barcode, X } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function DispensingAssistant() {
  const navigate = useNavigate();
  return (
    <div className="w-full min-h-screen bg-gray-50 p-6 flex flex-col items-center">
      {/* Header */}
      <div className="w-full max-w-md mb-6">
        <h1 className="text-xl font-semibold">Dispensing Assistant</h1>
      </div>

      {/* Progress Steps */}
      <div className="w-full max-w-md flex justify-between items-center mb-6 text-sm font-semibold">
        <span className="text-blue-600">1. Scan</span>
        <span className="text-gray-400">2. Check</span>
        <span className="text-gray-400">3. Verify</span>
      </div>

      {/* Title */}
      <div className="w-full max-w-md mb-4">
        <h2 className="text-2xl font-bold">1. Scan Medications</h2>
        <p className="text-gray-600 text-sm">
          Scan medication barcodes to build the prescription list.
        </p>
      </div>

      {/* Medication List */}
      <div className="w-full max-w-md space-y-4 mb-6">
        {[{ name: "Amoxicillin 500mg", form: "Tablet" }, { name: "Ibuprofen 200mg", form: "Tablet" }].map((med, i) => (
          <div key={i} className="bg-white rounded-2xl shadow p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Pill className="w-6 h-6 text-gray-600" />
              <div>
                <p className="font-semibold">{med.name}</p>
                <p className="text-sm text-gray-500">{med.form}</p>
              </div>
            </div>
            <X className="w-5 h-5 text-gray-400 hover:text-red-500 cursor-pointer" />
          </div>
        ))}
      </div>

      {/* Buttons */}
      <div className="w-full max-w-md flex gap-3 mb-10">
        <button className="w-1/2 bg-white border rounded-xl py-3 font-medium text-blue-600" onClick={() => navigate("/pharmacy/drug-input")}>+ Manual Entry</button>
        <button className="w-1/2 bg-blue-600 text-white rounded-xl py-3 flex items-center justify-center gap-2 font-medium" onClick={() => navigate("/pharmacy/camera")}>
          <Barcode className="w-4 h-4" /> Scan Item
        </button>
      </div>

      {/* Bottom Button */}
      <button className="w-full max-w-md py-5 rounded-xl bg-blue-600 text-white text-lg font-semibold shadow" onClick={() => navigate("/pharmacy/drug-input")}>
        Check Interactions (2) →
      </button>
    </div>
  );
}
