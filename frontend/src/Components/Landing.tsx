import { useNavigate } from "react-router-dom";
import { Sparkles, Activity, ArrowRight, Zap, CheckCircle } from "lucide-react";
import logo from "../assets/logo.png";

const Landing = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen bg-slate-50 font-sans text-slate-900 overflow-x-hidden">
            {/* Background blobs for aesthetics */}
            <div className="fixed top-0 left-0 w-full h-full overflow-hidden -z-10 pointer-events-none">
                <div className="absolute -top-[10%] -left-[10%] w-[50%] h-[50%] bg-blue-400 opacity-20 blur-[100px] rounded-full animate-pulse"></div>
                <div className="absolute top-[40%] -right-[10%] w-[60%] h-[60%] bg-indigo-400 opacity-15 blur-[120px] rounded-full"></div>
            </div>

            <main className="max-w-md mx-auto px-6 pt-12 pb-24 flex flex-col items-center">
                {/* Hero Section */}
                <div className="flex flex-col items-center text-center space-y-6 mb-16 animate-in fade-in slide-in-from-bottom-8 duration-700">
                    <div className="bg-white p-4 rounded-3xl shadow-xl shadow-blue-100/50 mb-4 inline-flex items-center justify-center">
                        <img src={logo} alt="ClinTwin Logo" className="w-16 h-16" />
                    </div>

                    <h1 className="text-5xl font-extrabold tracking-tight text-slate-900">
                        Clin<span className="text-blue-600">Twin</span>
                    </h1>

                    <p className="text-lg text-slate-600 leading-relaxed font-medium">
                        Your personal AI pharmacy mirror. Safer medication management at your fingertips.
                    </p>

                    <div className="flex flex-col w-full gap-4 pt-4">
                        <button
                            onClick={() => navigate("/permissions/language")}
                            className="group relative flex items-center justify-center gap-3 bg-blue-600 text-white px-8 py-4 rounded-2xl font-bold text-lg shadow-lg shadow-blue-200 hover:bg-blue-700 transition-all active:scale-[0.98]"
                        >
                            Get Started
                            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                        </button>
                        <p className="text-xs text-slate-400 font-medium uppercase tracking-widest">
                            Join 50,000+ Safety-First Users
                        </p>
                    </div>
                </div>

                {/* Features Preview */}
                <div className="w-full space-y-8 animate-in fade-in slide-in-from-bottom-12 delay-200 duration-1000 fill-mode-both">
                    <div className="bg-white/80 backdrop-blur-md p-6 rounded-3xl border border-white shadow-sm flex items-center gap-5">
                        <div className="bg-indigo-100 p-3 rounded-2xl text-indigo-600">
                            <Zap className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="font-bold text-slate-800">Instant AI Scan</h3>
                            <p className="text-sm text-slate-500">Identify any pill with just a photo</p>
                        </div>
                    </div>

                    <div className="bg-white/80 backdrop-blur-md p-6 rounded-3xl border border-white shadow-sm flex items-center gap-5">
                        <div className="bg-red-100 p-3 rounded-2xl text-red-600">
                            <Activity className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="font-bold text-slate-800">Safety Checks</h3>
                            <p className="text-sm text-slate-500">Cross-reference drug interactions</p>
                        </div>
                    </div>

                    <div className="bg-white/80 backdrop-blur-md p-6 rounded-3xl border border-white shadow-sm flex items-center gap-5">
                        <div className="bg-emerald-100 p-3 rounded-2xl text-emerald-600">
                            <CheckCircle className="w-6 h-6" />
                        </div>
                        <div>
                            <h3 className="font-bold text-slate-800">Verified Results</h3>
                            <p className="text-sm text-slate-500">Trusted data from clinical sources</p>
                        </div>
                    </div>
                </div>

                {/* Footer Accent */}
                <div className="mt-20 text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-50 text-blue-700 rounded-full text-sm font-semibold mb-4">
                        <Sparkles className="w-4 h-4" />
                        <span>Next-Gen Care</span>
                    </div>
                    <p className="text-xs text-slate-400">© 2025 ClinTwin. Modernizing Healthcare.</p>
                </div>
            </main>
        </div>
    );
};

export default Landing;
