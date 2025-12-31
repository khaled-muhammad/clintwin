import { Camera, Zap } from "lucide-react";
import { useNavigate } from "react-router-dom";

const CamInterface = () => {
  const navigate = useNavigate();
  return (
    <div className="relative flex h-dvh w-full flex-col font-display group/design-root overflow-hidden">
      {/* Background image */}
      <div
        className="absolute inset-0 w-full h-full bg-cover bg-center"
        style={{
          backgroundImage:
            "url('https://lh3.googleusercontent.com/aida-public/AB6AXuA9z5Dv2ZWve5yjtt5RPVo3pK-lWv8BqpDtl4QOvLzNq_HynKGYetFABB20dmkixOwhNBANf02PLwtKVOaqpnEhW-JTsVjsSQg9kIJQWw5-6vWiBIGrYsyOcxmvw2osRpVXbgzPeHti_aAglr1YH6CuqIZkSWtUH6UynH0NnpDY89mGhwFegUQHHEXCMrJJbpuo_z7-08RO-yI58SK_5MDqxRrp8ctMzNlrERfos2_oemPk0KFk_Igg1yGxaq7Hya8mT3A5sgeO6g')",
        }}
        aria-label="Abstract image of a science lab, representing the camera viewfinder background."
      ></div>

      {/* Overlay */}
      <div className="absolute inset-0 bg-black/30"></div>

      {/* Content */}
      <div className="relative z-10 flex flex-col h-full p-6 text-white">
        <div className="shrink-0"></div>

        <div className="grow flex flex-col items-center justify-center">
          {/* Heading */}
          <div className="text-center">
            <h2 className="text-white tracking-light text-[22px] font-semibold leading-tight drop-shadow-md">
              Place one medicine item on a plain background
            </h2>
            <p className="text-white/80 text-base mt-1 drop-shadow-md">
              ضع عنصرًا دوائيًا واحدًا على خلفية سادة
            </p>
          </div>

          {/* Camera view placeholder */}
          <div className="mt-8 flex h-80 w-full max-w-[280px] items-center justify-center">
            <div className="h-full w-full rounded-xl border-2 border-dashed border-white/60 bg-white/10 backdrop-blur-sm"></div>
          </div>
        </div>

        {/* Controls */}
        <div className="shrink-0 flex flex-col items-center pb-8">
          <div className="flex w-full max-w-sm items-center justify-around gap-6">
            {/* Flash button */}
            <button className="flex shrink-0 items-center justify-center rounded-full w-12 h-12 bg-black/40 text-white transition-colors hover:bg-black/60">
              <span
                className="material-symbols-outlined text-2xl"
                style={{ fontVariationSettings: '"FILL" 1, "wght" 400' }}
              >
              <Zap />
              </span>
            </button>

            {/* Capture button */}
            <button className="flex shrink-0 items-center justify-center rounded-full w-20 h-20 bg-medical-blue text-white shadow-lg ring-4 ring-white/30 transition-transform active:scale-95" onClick={() => navigate("/pharmacy/med-finder/start")}>
              <div className="w-16 h-16 rounded-full bg-white"></div>
            </button>

            {/* Flip camera button */}
            <button className="flex shrink-0 items-center justify-center rounded-full w-12 h-12 bg-black/40 text-white transition-colors hover:bg-black/60">
              <span
                className="material-symbols-outlined text-2xl"
                style={{ fontVariationSettings: '"FILL" 1, "wght" 400' }}
              >
                <Camera />
              </span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CamInterface;
