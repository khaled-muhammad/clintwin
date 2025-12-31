import { useState } from "react";
import { Search, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router-dom";

type StatusType = "success" | "warning" | "neutral";

interface ActivityItem {
  name: string;
  type: string;
  date: string;
  status: StatusType;
}

const activitiesData: ActivityItem[] = [
  {
    name: "Panadol Extra",
    type: "Photo Identification",
    date: "Today, 10:30 AM",
    status: "success",
  },
  {
    name: "Aspirin + Plavix",
    type: "Interaction Check",
    date: "Yesterday, 9:15 PM",
    status: "warning",
  },
  {
    name: "Cataflam",
    type: "Photo Identification",
    date: "15 Oct, 11:00 AM",
    status: "success",
  },
  {
    name: "Amoxicillin",
    type: "Identification by Questions",
    date: "14 Oct, 3:45 PM",
    status: "neutral",
  },
];

const StatusIcon = ({
  status,
  selected,
}: {
  status: StatusType;
  selected: boolean;
}) => {
  const base =
    "w-5 h-5 rounded-full flex items-center justify-center text-white text-sm";

  // Selected → show checkmark
  if (selected) return <div className={`${base} bg-green-600`}>✓</div>;

  // Default icons (no checkmarks)
  if (status === "success")
    return <div className="w-4 h-4 rounded-full bg-green-500" />;

  if (status === "warning")
    return <div className="w-4 h-4 rounded-full bg-orange-500" />;

  return <div className="w-4 h-4 rounded-full bg-gray-400" />;
};

const RecentActivity = () => {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const navigate = useNavigate();

  const handleSelect = (index: number) => {
    setSelectedIndex((prev) => (prev === index ? null : index));
  };

  function openItem(index: number) {
    const item = activitiesData[index];
    if (!item) return;
    if (item.type === "Photo Identification") {
      navigate("/pharmacy/camera");
    } else if (item.type === "Identification by Questions") {
      navigate("/pharmacy/med-finder/start");
    } else if (item.type === "Interaction Check") {
      navigate("/pharmacy/drug-input");
    } else {
      navigate("/pharmacy/dashboard");
    }
  }

  return (
    <div className="max-w-sm mx-auto p-4 py-6 bg-white h-screen">
      <h1 className="text-xl font-semibold mb-4">Recent Activity</h1>

      <div className="relative mb-4">
        <Search className="absolute left-3 top-3 text-gray-400 w-5 h-5" />
        <input
          type="text"
          placeholder="Search by drug name..."
          className="w-full pl-10 pr-4 py-2 rounded-xl border border-gray-300"
        />
      </div>

      <div className="space-y-5">
        {activitiesData.map((item, index) => {
          const isSelected = selectedIndex === index;

          return (
            <button
              key={index}
              onClick={() => {
                handleSelect(index);
                openItem(index);
              }}
              className="flex items-center justify-between w-full text-left"
            >
              <div className="flex items-center gap-3">
                <StatusIcon status={item.status} selected={isSelected} />

                <div>
                  <p className="font-semibold">{item.name}</p>
                  <p className="text-gray-500 text-sm">{item.type}</p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <p className="text-gray-500 text-sm whitespace-nowrap">
                  {item.date}
                </p>
                <ChevronRight className="text-gray-400" />
              </div>
            </button>
          );
        })}
      </div>

      <div className="fixed bottom-0 left-0 right-0 bg-white py-3 flex items-center justify-around shadow-inner">
        <button className="text-gray-700 text-xs" onClick={() => navigate("/pharmacy/home")}>Home</button>
        <button className="text-gray-700 text-xs" onClick={() => navigate("/pharmacy/camera")}>Scan</button>
        <button className="text-gray-700 text-xs" onClick={() => navigate("/pharmacy/drug-input")}>Interactions</button>
        <button className="text-gray-700 text-xs" onClick={() => navigate("/pharmacy/dashboard")}>Dashboard</button>
      </div>
    </div>
  );
};

export default RecentActivity;
