import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { ChevronDown, AlertTriangle, ArrowLeft } from "lucide-react";
import panadolResult from "../assets/Screenshot 2025-12-08 194948.png";
export default function IdentificationResult() {
  const [open, setOpen] = useState<string | null>(null);
  const location = useLocation();
  const navigate = useNavigate();
  type IdResult = {
    success: boolean;
    top_match?: { medicine: { name: string; generic_name?: string; dosage_form?: string }; confidence: number } | null;
    alternatives?: Array<{ medicine: { name: string }; confidence: number }>;
  };
  const result = (location.state as { result?: IdResult } | undefined)?.result;

  const toggle = (section: string) => {
    setOpen(open === section ? null : section);
  };


  return (
    <div className="relative w-full min-h-screen bg-gray-50 p-4 pb-40">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <button className="p-2" onClick={() => navigate(-1)}>
          <ArrowLeft size={24} />
        </button>
        <h1 className="text-lg font-semibold">Identification Result</h1>
      </div>

      {/* Pill Image Section */}
      <div className="w-full bg-black rounded-xl overflow-hidden mb-4">
        <img
          src={panadolResult}
          alt="pill"
          className="w-full object-cover"
        />
      </div>

      {/* Accuracy Badge */}
      <div className="w-full flex justify-center -mt-6 mb-2">
        <div className="bg-green-600 text-white px-4 py-1 rounded-full text-sm shadow">
          {typeof result?.top_match?.confidence === "number"
            ? `${Math.round(result.top_match.confidence * 100)}% Match`
            : "Match"}
        </div>
      </div>

      {/* Title + Info */}
      <div className="text-center mb-2">
        <h2 className="text-2xl font-bold">{result?.top_match?.medicine?.name ?? "Unknown medicine"}</h2>
        <p className="text-gray-600">
          {result?.top_match?.medicine?.generic_name ?? ""} {result?.top_match?.medicine?.dosage_form ?? ""}
        </p>
        <p className="text-gray-500 text-sm mt-1">
          Identified through 8 questions (98.2% accuracy)
        </p>
      </div>

      {/* Critical Warning */}
      <div className="bg-red-50 border border-red-300 rounded-xl p-4 mt-4 flex gap-3">
        <AlertTriangle className="text-red-600 mt-1" />
        <div>
          <h3 className="font-semibold text-red-700">Critical Warning</h3>
          <p className="text-sm text-red-700 mt-1">
            Do not take with any medication containing Paracetamol. Overdose may
            cause serious liver damage.
          </p>
        </div>
      </div>

      {/* Accordion Sections */}
      <div className="mt-6 space-y-3">
        {[
          { title: "Dosage & How to Use", content: "Adults: 500–1000 mg every 6 hours." },
          { title: "Side Effects", content: "Nausea, rash, abdominal discomfort (rare)." },
          { title: "Drug Interactions", content: "Avoid taking with other Paracetamol products." },
        ].map((section) => (
          <div
            key={section.title}
            className="bg-white rounded-xl shadow-sm border"
          >
            <button
              onClick={() => toggle(section.title)}
              className="w-full flex justify-between items-center py-3 px-4"
            >
              <span className="font-medium">{section.title}</span>
              <ChevronDown
                className={`transition-transform ${open === section.title ? "rotate-180" : ""
                  }`}
              />
            </button>

            {open === section.title && (
              <div className="px-4 pb-4 text-gray-600 text-sm">
                {section.content}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Alternatives */}
      <p className="mt-6 text-gray-600 font-medium">
        Not the right pill? Check other matches:
      </p>

      <div className="flex gap-3 mt-3 overflow-x-auto pb-4">
        {(result?.alternatives && result.alternatives.length > 0 ? result.alternatives.map((alt) => ({
          name: alt.medicine.name,
          img: "https://via.placeholder.com/120x90",
          accuracy: Math.round((alt.confidence ?? 0) * 100),
        })) : []).map((alt) => (
          <div
            key={alt.name}
            className="bg-white border rounded-xl p-3 min-w-[140px] shrink-0 shadow-sm"
          >
            <img
              src={alt.img}
              alt={alt.name}
              className="w-full h-20 object-cover rounded-md"
            />
            <p className="font-medium mt-2">{alt.name}</p>
            <span className="text-green-600 text-sm">{alt.accuracy}%</span>
          </div>
        ))}
      </div>

      {/* FIXED Bottom Button */}
      <div className="fixed bottom-0 left-0 w-full px-4 pb-6 bg-linear-to-t from-white/95 to-white/40">
        <button className="w-full py-3 bg-blue-600 text-white rounded-xl font-semibold shadow-lg" onClick={() => navigate("/pharmacy/drug-input")}>
          Check Drug Interactions
        </button>
      </div>
    </div>
  );
}
