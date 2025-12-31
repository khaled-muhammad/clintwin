import { useNavigate } from "react-router-dom"
import { useLanguage } from "../lib/LanguageContext"
import logo from "../assets/logo.png"

const LanguageSelector = () => {
  const navigate = useNavigate();
  const { setLanguage, t } = useLanguage();

  const handleLanguageSelect = (language: 'en' | 'ar') => {
    setLanguage(language);
    // Navigate to next step
    navigate('/permissions/user-type');
  };

  return (
    <>

      <section className=" flex flex-col items-center pt-8 min-h-screen bg-gray-100 gap-6">
        {/* Logo Row */}
        <div className="flex items-center gap-3">
          <img src={logo} alt="ClinTwin Logo" className="w-12 h-12" />
          <h1 className="text-3xl font-semibold text-gray-800">{t.landing.title}</h1>
        </div>


        {/* Loading Bar */}
        <div className="flex w-40 h-2 rounded-full overflow-hidden">
          <div className="bg-red-600 w-1/3"></div>
          <div className="bg-white w-1/3"></div>
          <div className="bg-black w-1/3"></div>
        </div>
        <div className="flex justify-center items-center flex-col h-[70vh]">
          <h1 className="text-5xl roboto text-center ">{t.languageSelector.title}</h1>
          <h5 className="mt-3">{t.languageSelector.titleAr}</h5>
        </div>

        <div className="btns flex  flex-col w-100 px-7 gap-4 justify-center mt-6">
          <button
            onClick={() => handleLanguageSelect('ar')}
            className="bg-[#005A9C] text-white px-6 py-2 rounded-lg shadow-md hover:bg-[#004080] transition-colors duration-200 font-medium"
          >
            {t.languageSelector.arabic}
          </button>
          <button
            onClick={() => handleLanguageSelect('en')}
            className="mb-7 bg-[#E5E5E5] text-gray-800 px-6 py-2 rounded-lg shadow-md hover:bg-gray-300 transition-colors duration-200 font-medium"
          >
            {t.languageSelector.english}
          </button>
        </div>

      </section>



    </>)
}

export default LanguageSelector