import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import { BrowserRouter, Route, Routes, Outlet } from "react-router-dom";

import CamAccess from "./Components/CamAccess";
import LanguageSelector from "./Components/LanguageSelector";
import UserType from "./Components/UserType";
import Home from "./Components/Home";
import CamInterface from "./Components/CamInterface";
import InitScreen from "./Components/InitScreen";
import DrugResults from "./Components/DrugResults";
import Dashboard from "./Components/Dashboard";
import QuestionInterface from "./Components/QuestionInterface";
import IdentificationResult from "./Components/IdentificationResult";
import DrugInput from "./Components/DrugInput";
import RecentActivity from "./Components/RecentActivity";
import DispensingAssistant from "./Components/DispensingAssistant";

import Landing from "./Components/Landing";
import { LanguageProvider } from "./lib/LanguageContext";

// Layouts
export const PermissionsLayout = () => <Outlet />;
export const PharmacyLayout = () => <Outlet />;
export const MedicineLayout = () => <Outlet />;

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <LanguageProvider>
      <BrowserRouter>
        <Routes>

          {/* Default route */}
          <Route path="/" element={<Landing />} />
          <Route path="/recent" element={<RecentActivity />} />

          {/* Permissions */}
          <Route path="/permissions" element={<PermissionsLayout />}>
            <Route path="language" element={<LanguageSelector />} />
            <Route path="user-type" element={<UserType />} />
            <Route path="camera-access" element={<CamAccess />} />
          </Route>

          {/* Pharmacy */}
          <Route path="/pharmacy" element={<PharmacyLayout />}>

            <Route path="home" element={<Home />} />
            <Route path="camera" element={<CamInterface />} />
            <Route path="drug-input" element={<DrugInput />} />

            <Route path="drug-results" element={<DrugResults />} />

            {/* Medicine identifier flow */}
            <Route path="med-finder" element={<MedicineLayout />}>
              <Route index element={<InitScreen />} />
              <Route path="start" element={<InitScreen />} />
              <Route path="questions" element={<QuestionInterface />} />
              <Route path="results" element={<IdentificationResult />} />
            </Route>

            <Route path="start" element={<InitScreen />} />
            <Route path="dashboard" element={<Dashboard />} />

            {/* ✅ Dispensing Assistant Page */}
            <Route path="dispense" element={<DispensingAssistant />} />
          </Route>

        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  </StrictMode>
);
