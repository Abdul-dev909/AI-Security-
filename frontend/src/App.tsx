import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppLayout } from './layouts/AppLayout';
import { Dashboard } from './pages/Dashboard/Dashboard';
import { AttackEngine } from './pages/AttackEngine/AttackEngine';
import { Detection } from './pages/Detection/Detection';
import { Evidence } from './pages/Evidence/Evidence';
import { Forensics } from './pages/Forensics/Forensics';
import { Analytics } from './pages/Analytics/Analytics';
import { Settings } from './pages/Settings/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/attacks" element={<AttackEngine />} />
          <Route path="/detection" element={<Detection />} />
          <Route path="/evidence" element={<Evidence />} />
          <Route path="/forensics" element={<Forensics />} />
          <Route path="/analytics" element={<Analytics />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
