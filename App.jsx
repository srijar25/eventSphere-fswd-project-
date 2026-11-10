import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { Navbar } from './components/Navbar';
import { DiscoveryPage } from './pages/DiscoveryPage';
import { EventDetailsPage } from './pages/EventDetailsPage';
import { MyRegistrationsPage } from './pages/MyRegistrationsPage';
import { EventPassportPage } from './pages/EventPassportPage';
import { OrganizerDashboardPage } from './pages/OrganizerDashboardPage';
import { QuickCheckScannerPage } from './pages/QuickCheckScannerPage';
import { AttendeeListPage } from './pages/AttendeeListPage';
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-react';

function AppContent() {
  const [notification, setNotification] = useState(null);

  const showNotification = (message, type = 'info') => {
    setNotification({ message, type, id: Date.now() });
    setTimeout(() => {
      setNotification(prev => (prev?.message === message ? null : prev));
    }, 4000);
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-800">
      {/* Global Notification Toast */}
      {notification && (
        <div className="fixed bottom-6 right-6 z-50 animate-in slide-in-from-bottom-5 duration-300 max-w-sm">
          <div className={`p-4 rounded-2xl shadow-xl border flex items-center space-x-3 ${
            notification.type === 'success'
              ? 'bg-emerald-950 text-white border-emerald-700'
              : notification.type === 'error'
              ? 'bg-rose-950 text-white border-rose-700'
              : notification.type === 'warning'
              ? 'bg-amber-950 text-white border-amber-700'
              : 'bg-slate-900 text-white border-slate-700'
          }`}>
            {notification.type === 'success' && <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0" />}
            {notification.type === 'error' && <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />}
            {notification.type === 'warning' && <AlertCircle className="w-5 h-5 text-amber-400 shrink-0" />}
            {notification.type === 'info' && <Info className="w-5 h-5 text-sky-400 shrink-0" />}

            <p className="text-xs font-medium flex-1">{notification.message}</p>
            <button
              onClick={() => setNotification(null)}
              className="text-white/60 hover:text-white p-1"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Navigation */}
      <Navbar onNotify={showNotification} />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <Routes>
          <Route path="/" element={<DiscoveryPage onNotify={showNotification} />} />
          <Route path="/events/:id" element={<EventDetailsPage onNotify={showNotification} />} />
          <Route path="/my-registrations" element={<MyRegistrationsPage onNotify={showNotification} />} />
          <Route path="/passport" element={<EventPassportPage onNotify={showNotification} />} />
          <Route path="/organizer/dashboard" element={<OrganizerDashboardPage onNotify={showNotification} />} />
          <Route path="/organizer/scanner" element={<QuickCheckScannerPage onNotify={showNotification} />} />
          <Route path="/organizer/events/:eventId/attendees" element={<AttendeeListPage onNotify={showNotification} />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 mt-auto py-8 text-xs text-slate-500">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-between items-center gap-4">
          <div>
            <div className="font-bold text-slate-800 text-sm">
              EventSphere • Discover. Register. Connect.
            </div>
            <p className="text-[11px] text-slate-400 mt-0.5">
              Full Stack Web Development (FSWD) Course Project | Team 19 • CSE-B
            </p>
          </div>

          <div className="text-center sm:text-right text-[11px] space-y-0.5">
            <div>G Srija Santoshini (1602-24-733-117) • Front End Lead</div>
            <div>Siddheeshwar CH (1602-24-733-114) • Back End Lead</div>
            <div>E Keerthi Teja (1602-24-733-081) • Quality & QR Pass Lead</div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <AppContent />
      </AuthProvider>
    </Router>
  );
}

