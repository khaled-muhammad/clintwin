import {
  Camera,
  FileText,
  ShieldAlert,
  ShieldCheck,
  ChevronRight,
  User,
  Phone,
} from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../lib/LanguageContext";
import logo from "../assets/logo.png";

export default function HomeScreen() {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <div className="roboto min-h-screen bg-linear-to-b from-white to-gray-100 p-4 font-sans max-w-sm mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <img src={logo} alt="ClinTwin Logo" className="w-8 h-8" />
        <h1 className="text-lg font-semibold text-gray-800">{t.home.appName}</h1>
        <User className="w-6 h-6 text-gray-700" />
      </div>

      {/* Greeting */}
      <h2 className="text-2xl font-semibold text-gray-900 mb-4">
        {t.home.greeting}
      </h2>

      {/* Action Cards */}
      <div className="space-y-4 mb-6">
        <div
          className="flex items-start gap-3 p-4 bg-white rounded-2xl shadow-sm cursor-pointer"
          onClick={() => navigate("/pharmacy/camera")}
        >
          <div className="bg-blue-500 p-3 rounded-xl text-white">
            <Camera className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800">{t.home.identifyByPhoto}</h3>
            <p className="text-sm text-gray-600">
              {t.home.identifyByPhotoDesc}
            </p>
          </div>
        </div>

        <div
          className="flex items-start gap-3 p-4 bg-white rounded-2xl shadow-sm cursor-pointer"
          onClick={() => navigate("/pharmacy/med-finder/start")}
        >
          <div className="bg-blue-500 p-3 rounded-xl text-white">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800">
              {t.home.identifyByDescription}
            </h3>
            <p className="text-sm text-gray-600">
              {t.home.identifyByDescriptionDesc}
            </p>
          </div>
        </div>

        <div
          className="flex items-start gap-3 p-4 bg-white rounded-2xl shadow-sm cursor-pointer"
          onClick={() => navigate("/pharmacy/drug-input")}
        >
          <div className="bg-blue-500 p-3 rounded-xl text-white">
            <ShieldAlert className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-800">{t.home.checkInteractions}</h3>
            <p className="text-sm text-gray-600">
              {t.home.checkInteractionsDesc}
            </p>
          </div>
        </div>
      </div>

      {/* Green Banner */}
      <div className="flex items-center gap-3 bg-green-100 p-4 rounded-xl shadow-sm mb-6">
        <ShieldCheck className="text-green-600 w-6 h-6" />
        <div>
          <h3 className="text-green-700 font-semibold text-sm">
            {t.home.errorsPrevented}
          </h3>
          <p className="text-gray-700 text-xs">
            {t.home.joinUsers}
          </p>
        </div>
      </div>

      {/* Recent Activity */}
      <h3 className="font-semibold text-gray-800 mb-3">{t.home.recentActivity}</h3>

      <div className="space-y-3 mb-20">
        <div className="flex items-center justify-between p-4 bg-white rounded-2xl shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gray-200"></div>
            <div>
              <p className="font-semibold text-gray-800">Aspirin 81mg</p>
              <p className="text-xs text-gray-600">{t.home.identifiedViaPhoto}</p>
            </div>
          </div>
          <ChevronRight className="text-gray-500" />
        </div>

        <div className="flex items-center justify-between p-4 bg-white rounded-2xl shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-black"></div>
            <div>
              <p className="font-semibold text-gray-800">Amoxicillin 500mg</p>
              <p className="text-xs text-gray-600">{t.home.interactionCheck}</p>
            </div>
          </div>
          <ChevronRight className="text-gray-500" />
        </div>
      </div>

      {/* Bottom Nav */}
      <div className="fixed bottom-0 left-0 right-0 bg-white py-4 flex items-center justify-around shadow-xl">
        <button className="flex gap-2 justify-center items-center  bg-red-600 text-white px-6 py-3 rounded-full font-semibold">
          <Phone />  {t.home.emergency}
        </button>
        <button className="bg-blue-600 p-4 rounded-full text-white" onClick={() => navigate("/pharmacy/camera")}>
          <Camera className="w-6 h-6" />
        </button>
      </div>
    </div>
  );
}
