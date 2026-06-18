import { Routes, Route } from 'react-router-dom';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Overview from './pages/Overview';
import Forecasting from './pages/Forecasting';
import Alerts from './pages/Alerts';
import Controls from './pages/Controls';
import DashboardLayout from './components/DashboardLayout';
import ProtectedRoute from './components/ProtectedRoute';
import { useLiveGrid } from './hooks/useLiveGrid';

export default function App() {
  const { nodes, summary, alerts, connected, toggleNode, acknowledgeAlert } = useLiveGrid();

  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardLayout alertCount={alerts.length} connected={connected} />
          </ProtectedRoute>
        }
      >
        <Route index element={<Overview nodes={nodes} summary={summary} />} />
        <Route path="forecasting" element={<Forecasting nodes={nodes} />} />
        <Route path="alerts" element={<Alerts alerts={alerts} acknowledgeAlert={acknowledgeAlert} />} />
        <Route path="controls" element={<Controls nodes={nodes} toggleNode={toggleNode} />} />
      </Route>
    </Routes>
  );
}
