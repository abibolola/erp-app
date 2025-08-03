import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./modules/auth/pages/Login";
import LeadsList from "./modules/crm/pages/LeadsList";

const Router = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/auth/login" element={<Login />} />
        <Route path="/crm/leads" element={<LeadsList />} />
        {/* You can add a Dashboard, Contacts, etc. later */}
      </Routes>
    </BrowserRouter>
  );
};

export default Router;
