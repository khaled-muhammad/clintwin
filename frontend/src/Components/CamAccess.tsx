import { FlaskConical, LockKeyhole, Pill } from "lucide-react";
import { FaCamera } from "react-icons/fa";
import { useNavigate } from "react-router-dom";
import { useLanguage } from "../lib/LanguageContext";

const CamAcess = () => {
  const navigate = useNavigate();
  const { t } = useLanguage();

  return (
    <section className="h-[105vh]  bg-[#F5F7F8]">
      <div className="flex flex-col items-center">
        <div className="relative w-fit mx-auto mt-5">
          {/* Camera Icon */}
          <div className="relative w-[110px] h-[110px] rounded-full
           bg-linear-to-tr from-[#264653]/20 to-[#2A9D8F]/20 flex items-center
            justify-center transform transition-transform duration-300 hover:scale-105">
            <FaCamera className="w-[90px] h-[90px] text-[#264653] p-3" />
          </div>

          {/* Lock Badge */}
          <div className="absolute bottom-0 right-0 bg-[#2A9D8F]
           rounded-full p-1 flex items-center justify-center w-6 h-6 shadow-md">
            <LockKeyhole className="text-white w-4 h-4" />
          </div>
        </div>

        <h2 className="capitalize roboto text-4xl w-[75%] 
        text-center text-[#264653] mt-6">
          {t.camAccess.title}
        </h2>

        <p className="capitalize pt-2 text-gray-900 px-5 mt-3 w-[95%]
         text-xl text-center">
          {t.camAccess.subtitle}
        </p>
      </div>

      <div className="mt-8 w-full flex flex-col items-center">
        <div className="card flex items-center gap-5 mx-4 my-4 p-4 
        rounded-2xl bg-white shadow-md hover:shadow-xl transition-shadow 
        duration-300 w-[90%]">
          <div className="icon bg-[#E6F3F2] w-[50px] h-[50px] p-2 flex 
          justify-center items-center rounded-2xl">
            <Pill className="text-[#2A9D8F]" />
          </div>
          <p className="capitalize roboto text-lg font-medium">
            {t.camAccess.identifyPills}
          </p>
        </div>

        <div className="card flex items-center gap-5 mx-4
         my-4 p-4 rounded-2xl bg-white shadow-md hover:shadow-xl
          transition-shadow duration-300 w-[90%]">
          <div className="icon bg-[#E6F3F2] w-[50px] h-[50px] p-2 
          flex justify-center items-center rounded-2xl">
            <FlaskConical className="text-[#2A9D8F]" />
          </div>
          <p className="capitalize roboto text-lg font-medium">
            {t.camAccess.checkInteractions}
          </p>
        </div>
      </div>

      <p className="capitalize pt-2 text-gray-900/60 px-5 mt-3 w-[95%] text-lg mx-auto text-center">
        {t.camAccess.privacyNote}
      </p>

      <div className="flex flex-col items-center justify-center mt-10 gap-4">
        <button
          className="capitalize bg-[#2A9D8F] text-white px-8 py-3 
          rounded-full shadow-lg hover:bg-[#238b7a] transition-colors
          duration-200 font-medium text-lg"
          onClick={() => navigate("/pharmacy/camera")}
        >
          {t.camAccess.allowAccess}
        </button>
        <button
          className="roboto capitalize text-gray-600 
          font-semibold px-8 py-3 rounded-full hover:bg-gray-200
           transition-colors duration-200 text-lg"
          onClick={() => navigate("/pharmacy/home")}
        >
          {t.camAccess.notNow}
        </button>
      </div>
    </section>
  );
};

export default CamAcess;
