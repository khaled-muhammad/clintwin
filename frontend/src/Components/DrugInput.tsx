import { useState, useEffect } from "react";
import { Trash2, Plus, ChevronLeft, Search } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { checkInteractionsByNames, getMedicines, searchMedicines, type MedicineListItem } from "../lib/api";

const DrugInput = () => {
  const [medications, setMedications] = useState(["Aspirin", "Congestal"]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [common, setCommon] = useState<MedicineListItem[]>([]);
  const [suggestions, setSuggestions] = useState<MedicineListItem[]>([]);
  const [searching, setSearching] = useState(false);
  useEffect(() => {
    let active = true;
    async function load() {
      try {
        const meds = await getMedicines();
        if (active) setCommon(meds.slice(0, 6));
      } catch {
        if (active) setCommon([]);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, []);
  const navigate = useNavigate();

  const recent = ["Panadol", "Augmentin", "Cetal"];

  const removeMed = (name: string) =>
    setMedications(medications.filter((m) => m !== name));

  return (
    <div className="max-w-sm mx-auto bg-white h-screen p-4">
      {/* Header */}
      <div className="flex items-center gap-3 mb-4">
        <ChevronLeft className="w-5 h-5 cursor-pointer" onClick={() => navigate(-1)} />
        <h2 className="text-lg font-semibold">Drug Interaction Checker</h2>
      </div>

      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Enter drug name (e.g., Panadol)"
          className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-300 focus:outline-none"
          value={input}
          onChange={async (e) => {
            const v = e.target.value;
            setInput(v);
            if (v.trim().length === 0) {
              setSuggestions([]);
              return;
            }
            try {
              setSearching(true);
              const res = await searchMedicines(v.trim(), 8);
              setSuggestions(res.results);
            } catch {
            } finally {
              setSearching(false);
            }
          }}
        />
      </div>
      {input && (
        <div className="mt-2 border rounded-xl">
          <div className="max-h-40 overflow-auto">
            {searching ? (
              <div className="px-3 py-2 text-sm text-gray-500">Searching...</div>
            ) : suggestions.length > 0 ? (
              suggestions.map((s) => (
                <button
                  key={s.id}
                  className="w-full flex justify-between items-center px-3 py-2 text-left hover:bg-gray-50"
                  onClick={() => {
                    setMedications((prev) => [...prev, s.name]);
                    setInput("");
                    setSuggestions([]);
                  }}
                >
                  <span className="text-sm">{s.name}</span>
                  <Plus className="text-blue-600 w-4 h-4" />
                </button>
              ))
            ) : (
              <div className="px-3 py-2 text-sm text-gray-500">No matches</div>
            )}
          </div>
        </div>
      )}

      <p className="text-sm text-gray-500 mt-2">
        Add at least two medications to check for interactions.
      </p>

      {/* Your Medications */}
      <h3 className="mt-5 font-semibold">Your Medications ({medications.length})</h3>

      <div className="mt-2 space-y-3">
        {medications.map((med) => (
          <div
            key={med}
            className="flex items-center justify-between bg-gray-100 px-4 py-3 rounded-xl"
          >
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-full bg-blue-200" />
              <span>{med}</span>
            </div>

            <Trash2
              className="text-red-500 cursor-pointer"
              onClick={() => removeMed(med)}
            />
          </div>
        ))}
      </div>

      {/* Recently Added */}
      <h3 className="mt-6 font-semibold">Recently Added</h3>
      <div className="flex gap-2 mt-2 flex-wrap">
        {recent.map((item) => (
          <span
            key={item}
            className="bg-blue-100 text-blue-600 px-3 py-1 rounded-full text-sm"
          >
            {item}
          </span>
        ))}
      </div>

      {/* Common Medications */}
      <h3 className="mt-6 font-semibold">Common Medications</h3>
      <div className="space-y-3 mt-2">
        {common.length === 0 ? (
          <div className="text-sm text-gray-500">Loading...</div>
        ) : common.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between border px-4 py-3 rounded-xl"
          >
            <span>{item.name}</span>
            <Plus className="text-blue-600 cursor-pointer" onClick={() => setMedications((prev) => [...prev, item.name])} />
          </div>
        ))}
      </div>

      {/* Button */}
      <div className="flex gap-2 mt-6">
        <button
          className="flex-1 bg-gray-100 text-gray-800 py-3 rounded-xl text-lg border"
          onClick={() => {
            if (input.trim()) setMedications((prev) => [...prev, input.trim()]);
            setInput("");
          }}
        >
          Add Medicine
        </button>
        <button
          className="flex-1 bg-blue-600 text-white py-3 rounded-xl text-lg"
          disabled={loading || medications.length < 2}
          onClick={async () => {
            try {
              setLoading(true);
              const res = await checkInteractionsByNames(medications);
              navigate("/pharmacy/drug-results", { state: { result: res } });
            } catch (e) {
              console.error(e);
              alert("Failed to check interactions");
            } finally {
              setLoading(false);
            }
          }}
        >
          {loading ? "Checking..." : "Check for Interactions"}
        </button>
      </div>
    </div>
  );
};

export default DrugInput;
