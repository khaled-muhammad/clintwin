import { useEffect, useMemo, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { startAkinator, submitAkinatorAnswer } from "../lib/api";
import type { AkinatorQuestionResponse, AkinatorResultResponse } from "../lib/api";

export default function QuestionInterface() {
  const location = useLocation();
  const navigate = useNavigate();

  type Question = { question_text: string; options: string[] };
  const initialSessionId = (location.state as { sessionId?: string } | undefined)?.sessionId;
  const initialQuestion = (location.state as { question?: Question } | undefined)?.question;
  const initialAsked = (location.state as { questionsAsked?: number } | undefined)?.questionsAsked;
  const initialConfidence = (location.state as { confidence?: number } | undefined)?.confidence;

  const [sessionId, setSessionId] = useState<string | undefined>(initialSessionId);
  const [question, setQuestion] = useState<typeof initialQuestion | undefined>(initialQuestion);
  const [selected, setSelected] = useState<string | undefined>(undefined);
  const [questionsAsked, setQuestionsAsked] = useState<number>(initialAsked ?? 0);
  const [confidence, setConfidence] = useState<number>(initialConfidence ?? 0);

  const totalSteps = 8;
  const progressWidth = useMemo(() => Math.min(100, ((questionsAsked) / totalSteps) * 100), [questionsAsked]);

  useEffect(() => {
    async function boot() {
      if (!initialSessionId || !initialQuestion) {
        try {
          const res = await startAkinator();
          setSessionId(res.session_id);
          setQuestion(res.question);
          setQuestionsAsked(res.questions_asked);
          setConfidence(res.confidence);
        } catch (e) {
          console.error(e);
          alert("Failed to load question. Is the backend running?");
        }
      }
    }
    boot();
  }, [initialSessionId, initialQuestion]);

  async function handleNext() {
    if (!sessionId || !selected) return;
    try {
      const res = await submitAkinatorAnswer(sessionId, selected) as AkinatorQuestionResponse | AkinatorResultResponse;
      if (res.type === "question") {
        setQuestion(res.question);
        setQuestionsAsked(res.questions_asked);
        setConfidence(res.confidence);
        setSelected(undefined);
      } else if (res.type === "result") {
        navigate("/pharmacy/med-finder/results", { state: { result: res } });
      } else {
        alert("Unexpected response");
      }
    } catch (e) {
      console.error(e);
      alert("Failed to submit answer");
    }
  }

  return (
    <div className="w-full min-h-screen bg-white p-4 flex flex-col">
      <div className="flex items-center gap-3">
        <button className="text-xl" onClick={() => navigate(-1)}>✖</button>
        <h2 className="text-lg font-semibold">Medicine Identifier</h2>
      </div>

      <div className="mt-4">
        <div className="flex justify-between text-sm text-gray-600 mb-1">
          <span>Step {questionsAsked} of {totalSteps}</span>
          <span>{Math.round(confidence * 100)}% confidence</span>
        </div>
        <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
          <div
            className="h-full bg-blue-500 rounded-full transition-all duration-300"
            style={{ width: `${progressWidth}%` }}
          ></div>
        </div>
      </div>

      <h1 className="text-2xl font-bold mt-6">{question?.question_text ?? "Loading question..."}</h1>

      <div className="grid grid-cols-2 gap-4 mt-4">
        {question?.options?.map((opt) => (
          <button
            key={opt}
            onClick={() => setSelected(opt)}
            className={`flex flex-col items-center justify-center p-6 rounded-xl border text-center transition-all shadow-sm 
              ${selected === opt ? "border-green-600 bg-green-50" : "border-gray-200 bg-gray-50"}`}
          >
            <span className="font-medium">{opt}</span>
          </button>
        ))}
      </div>

      <div className="mt-auto flex justify-between items-center pt-6">
        <button
          className="px-6 py-3 rounded-lg border bg-gray-100"
          onClick={() => navigate(-1)}
        >
          Back
        </button>

        <button
          className="px-8 py-3 rounded-lg bg-blue-600 text-white font-semibold shadow"
          onClick={handleNext}
          disabled={!selected}
        >
          Next
        </button>
      </div>
    </div>
  );
}
