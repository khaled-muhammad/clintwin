import {
  ArrowLeft,
  AlertCircle,
  ChevronDown,
  CheckCircle2,
  Info,
} from "lucide-react";
import { useLocation } from "react-router-dom";
import type { InteractionCheckByNamesResponse } from "../lib/api";
import { useNavigate } from "react-router-dom";

export default function DrugResults() {
  const location = useLocation();
  const result = (location.state as { result?: InteractionCheckByNamesResponse } | undefined)?.result;
  const navigate = useNavigate();
  return (
    <div className="w-full min-h-screen bg-gray-50 p-4 flex flex-col items-center text-gray-800 pb-24">
      {/* Header */}
      <div className="w-full max-w-sm flex items-center gap-2 mb-4">
        <ArrowLeft className="text-gray-700 cursor-pointer" onClick={() => navigate(-1)} />
        <h1 className="text-lg font-semibold">Interaction Results</h1>
      </div>

      {/* Alert Summary */}
      {result?.risk_level ? (
        <div className="w-full max-w-sm bg-yellow-100 text-yellow-700 py-2 px-3 rounded-lg text-center text-sm font-medium mb-4">
          {result.summary}
        </div>
      ) : (
        <div className="w-full max-w-sm bg-gray-100 text-gray-700 py-2 px-3 rounded-lg text-center text-sm font-medium mb-4">
          No results data
        </div>
      )}

      {/* Tabs */}
      <div className="w-full max-w-sm flex gap-2 overflow-x-auto mb-4 text-sm">
        <button className="bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full">
          All (5)
        </button>
        <button className="bg-red-100 text-red-700 px-3 py-1 rounded-full">
          Critical (1)
        </button>
        <button className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full">
          Moderate (1)
        </button>
        <button className="bg-yellow-50 text-yellow-700 px-3 py-1 rounded-full">
          Minor (1)
        </button>
      </div>

      {/* Critical Section */}
      <div className="w-full max-w-sm mb-3">
        <h2 className="text-red-600 font-semibold mb-2">Warnings</h2>

        <div className="bg-red-50 border border-red-300 p-4 rounded-xl">
          <div className="flex items-start gap-2 mb-2">
            <AlertCircle className="text-red-600" />
            <div>
              {result?.warnings?.length ? (
                <>
                  <p className="font-semibold text-red-700">{result.warnings[0].title}</p>
                  <p className="text-sm text-red-600">{result.warnings[0].message}</p>
                </>
              ) : (
                <p className="text-sm text-red-600">No critical warnings.</p>
              )}
            </div>
          </div>

          {result?.warnings?.length ? (
            <p className="text-sm text-gray-700 mb-3">
              {result.warnings[0].recommendation}
            </p>
          ) : null}

          <div className="bg-red-100 text-red-800 text-sm p-2 rounded-md font-medium">
            {result?.warnings?.length ? result.warnings[0].title : "No warnings"}
          </div>
        </div>
      </div>

      {/* Moderate Section */}
      <div className="w-full max-w-sm mb-3">
        <h2 className="text-yellow-600 font-semibold mb-2">Moderate</h2>

        <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-xl flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Info className="text-yellow-500" />
            <p className="font-medium text-gray-800">Aspirin & Ibuprofen</p>
          </div>
          <ChevronDown className="text-gray-600" />
        </div>
      </div>

      {/* Minor Section */}
      <div className="w-full max-w-sm mb-3">
        <h2 className="text-yellow-600 font-semibold mb-2">Minor</h2>

        <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-xl flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Info className="text-yellow-500" />
            <p className="font-medium text-gray-800">Amoxicillin & Metformin</p>
          </div>
          <ChevronDown className="text-gray-600" />
        </div>
      </div>

      {/* Safe Section */}
      <div className="w-full max-w-sm mb-3">
        <h2 className="text-green-700 font-semibold mb-2">
          Safe to Take Together
        </h2>

        {[
          {
            pair: "Panadol & Amoxicillin",
            note: "No significant interaction found.",
          },
          {
            pair: "Ibuprofen & Metformin",
            note: "No significant interaction found.",
          },
        ].map((item) => (
          <div
            key={item.pair}
            className="bg-green-50 border border-green-200 p-3 rounded-xl flex gap-3 mb-2"
          >
            <CheckCircle2 className="text-green-600 mt-1" />
            <div>
              <p className="font-medium text-gray-800">{item.pair}</p>
              <p className="text-sm text-gray-600">{item.note}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Button */}
      <button className="fixed bottom-4 w-full max-w-sm bg-yellow-500 hover:bg-yellow-600 text-white font-semibold py-3 rounded-xl shadow">
        <span className="flex items-center gap-2 justify-center">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5 5m0 0l5-5m-5 5V4"
            />
          </svg>
          Export for Pharmacist
        </span>
      </button>
    </div>
  );
}
