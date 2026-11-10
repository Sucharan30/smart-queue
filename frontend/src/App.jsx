import React, { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import LandingPage from './pages/LandingPage';
import { checkHealth } from './services/api';

function App() {
  const [healthData, setHealthData] = useState({
    overallStatus: 'backend_unavailable',
    backendOnline: false,
    databaseConnected: false,
    message: 'Initializing connection check...',
    data: null,
  });
  const [loading, setLoading] = useState(true);

  const fetchHealthStatus = useCallback(async () => {
    setLoading(true);
    try {
      const result = await checkHealth();
      setHealthData(result);
    } catch (err) {
      setHealthData({
        overallStatus: 'backend_unavailable',
        backendOnline: false,
        databaseConnected: false,
        message: 'Unexpected network error while contacting backend.',
        data: null,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchHealthStatus();
    // Periodic polling every 30 seconds to keep live status fresh
    const interval = setInterval(fetchHealthStatus, 30000);
    return () => clearInterval(interval);
  }, [fetchHealthStatus]);

  return (
    <Router>
      <MainLayout overallStatus={healthData.overallStatus}>
        <Routes>
          <Route
            path="/"
            element={
              <LandingPage
                healthData={healthData}
                loading={loading}
                onRefresh={fetchHealthStatus}
              />
            }
          />
        </Routes>
      </MainLayout>
    </Router>
  );
}

export default App;

