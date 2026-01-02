import { User } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../lib/LanguageContext";

const UserType = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <section className="max-w-4xl mx-auto px-4 py-10 flex flex-col justify-between h-screen ">
      {/* Top content */}
      <div>
        <h1 className="roboto text-3xl font-semibold text-center mb-8">
          {t.userType.title}
        </h1>

        <div className="grid gap-6 mb-8">
          {/* Patient Card */}
          <div
            className="flex gap-4 items-center px-6 py-5 rounded-2xl border-2 border-[#64748B] bg-white shadow-lg"
          >
            <div
              className="w-[70px] h-[70px] flex items-center justify-center rounded-full"
              style={{ backgroundColor: "#64748B20" }}
            >
              <User className="w-10 h-10 text-[#64748B]" />
            </div>
            <div className="flex-1">
              <h3 className="roboto text-lg font-semibold capitalize text-[#64748B]">
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
          className="w-full md:w-1/3 px-6 py-3 rounded-xl font-semibold text-white transition-all duration-300 bg-[#64748B] hover:bg-[#576075] shadow-md"
          onClick={() => {
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
