import docImg from "../assets/doc.png";
import { useNavigate } from "react-router-dom";
import { startAkinator } from "../lib/api";

const InitScreen = () => {
  const navigate = useNavigate();

  async function handleStart() {
    try {
      const res = await startAkinator();
      navigate("/pharmacy/med-finder/questions", {
        state: {
          sessionId: res.session_id,
          question: res.question,
          questionsAsked: res.questions_asked,
          confidence: res.confidence,
        },
      });
    } catch (e) {
      console.error(e);
      alert("Failed to start identification. Please ensure the backend is running.");
    }
  }

  return (
    <section className=" flex flex-col min-h-screen bg-gray-50 px-6 md:px-20">
      {/* Middle content */}
      <div className="flex flex-col items-center justify-center grow">
        <img
          src={docImg}
          alt="Doctor Illustration"
          className="w-64 md:w-80 mb-6 object-contain"
        />
        <h1 className="roboto text-3xl md:text-4xl font-semibold text-gray-900 mb-4 text-center">
          I will help you identify your medicine.
        </h1>
        <p className="text-gray-600 text-lg md:text-base text-center">
          I'll ask you a few simple questions.
        </p>
      </div>

      {/* Button at the bottom */}
      <div className="w-full py-6">
        <button
          className="roboto w-full bg-[#095CB0] hover:bg-[#074a91] text-white font-semibold px-8 py-4 rounded-xl shadow-md transition-colors duration-300"
          onClick={handleStart}
        >
          Let's start
        </button>
      </div>
    </section>
  );
};

export default InitScreen;
