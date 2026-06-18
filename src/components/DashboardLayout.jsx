import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAuth } from '../context/AuthContext';

const TITLES = {
  '/dashboard': ['Grid Overview', 'Real-time load monitoring across all substations'],
  '/dashboard/forecasting': ['Load Forecasting', 'Predicted demand and model accuracy'],
  '/dashboard/alerts': ['Alerts', 'Threshold breaches and operational notices'],
  '/dashboard/controls': ['Controls', 'Manual load balancing and substation power']
};

export default function DashboardLayout({ alertCount, connected }) {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const [title, subtitle] = TITLES[location.pathname] || TITLES['/dashboard'];

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar alertCount={alertCount} user={user} onLogout={handleLogout} />
      <div className="flex-1 min-w-0">
        <Header title={title} subtitle={subtitle} connected={connected} />
        <Outlet />
      </div>
    </div>
  );
}
