import { Stethoscope, User } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../lib/LanguageContext";

const UserType = () => {
  const [selected, setSelected] = useState<string | null>(null);
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <section className="max-w-4xl mx-auto px-4 py-10 flex flex-col justify-between h-screen ">
      {/* Top content */}
      <div>
        <h1 className="roboto text-3xl font-semibold text-center mb-8">
          {t.userType.title}
        </h1>

        <div className="grid gap-6 md:grid-cols-2 mb-8">
          {/* Pharmacy Card */}
          <div
            onClick={() => setSelected("pharmacy")}
            className={`
          flex gap-4 items-center px-6 py-5 rounded-2xl cursor-pointer transition-all duration-300
          border-2 ${selected === "pharmacy" ? "border-[#0A66C2] shadow-lg" : "border-transparent hover:shadow-md"}
          hover:scale-105
          bg-white
        `}
          >
            <div
              className="w-[70px] h-[70px] flex items-center justify-center rounded-full bg-[#E6EFF9]"
              style={{
                backgroundColor: selected === "pharmacy" ? "#0A66C220" : "#E6EFF9",
              }}
            >
              <Stethoscope className="w-10 h-10 text-[#0A66C2]" />
            </div>
            <div className="flex-1">
              <h3
                className="roboto text-lg font-semibold capitalize"
                style={{ color: selected === "pharmacy" ? "#0A66C2" : "#111827" }}
              >
                {t.userType.pharmacyTitle}
              </h3>
              <p className="text-gray-600 mt-1 text-sm">
                {t.userType.pharmacyDesc}
              </p>
            </div>
          </div>

          {/* Patient Card */}
          <div
            onClick={() => setSelected("patient")}
            className={`
          flex gap-4 items-center px-6 py-5 rounded-2xl cursor-pointer transition-all duration-300
          border-2 ${selected === "patient" ? "border-[#64748B] shadow-lg" : "border-transparent hover:shadow-md"}
          hover:scale-105
          bg-white
        `}
          >
            <div
              className="w-[70px] h-[70px] flex items-center justify-center rounded-full bg-[#E6EFF9]"
              style={{
                backgroundColor: selected === "patient" ? "#64748B20" : "#E6EFF9",
              }}
            >
              <User className="w-10 h-10 text-[#64748B]" />
            </div>
            <div className="flex-1">
              <h3
                className="roboto text-lg font-semibold capitalize"
                style={{ color: selected === "patient" ? "#64748B" : "#111827" }}
              >
                {t.userType.patientTitle}
              </h3>
              <p className="text-gray-600 mt-1 text-sm">
                {t.userType.patientDesc}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Button */}
      <div className="flex flex-col items-center gap-2">
        <button
          type="button"
          disabled={!selected}
          className={`
        w-full md:w-1/3 px-6 py-3 rounded-xl font-semibold text-white transition-all duration-300
        ${selected ? "bg-[#0A66C2] hover:bg-[#0A66C2] shadow-md" : "bg-gray-300 cursor-not-allowed"}
      `}
          onClick={() => {
            if (!selected) return;
            navigate("/pharmacy/home");
          }}
        >
          {t.userType.continue}
        </button>
        <p className="text-gray-500 text-sm text-center">
          {t.userType.changeNote}
        </p>
      </div>
    </section>

  );
};

export default UserType;
