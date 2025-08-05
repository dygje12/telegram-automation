import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './hooks/useAuth.jsx';
import { LoginForm } from './components/auth/LoginForm';
import { CodeVerification } from './components/auth/CodeVerification';
import { TwoFactorAuth } from './components/auth/TwoFactorAuth';
import { Layout } from './components/Layout';
import { Dashboard } from './components/Dashboard';
import { Loader2 } from 'lucide-react';
import './App.css';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
});

// Auth wrapper component
const AuthWrapper = () => {
  const { isAuthenticated, isLoading, authStep } = useAuth();
  const [activeTab, setActiveTab] = useState('dashboard');

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
        <div className="text-center">
          <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    switch (authStep) {
      case 'code':
        return <CodeVerification />;
      case '2fa':
        return <TwoFactorAuth />;
      default:
        return <LoginForm />;
    }
  }

  // Render main app content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'messages':
        return <div>Messages Component (Coming Soon)</div>;
      case 'groups':
        return <div>Groups Component (Coming Soon)</div>;
      case 'blacklist':
        return <div>Blacklist Component (Coming Soon)</div>;
      case 'scheduler':
        return <div>Scheduler Component (Coming Soon)</div>;
      case 'settings':
        return <div>Settings Component (Coming Soon)</div>;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Layout activeTab={activeTab} setActiveTab={setActiveTab}>
      {renderContent()}
    </Layout>
  );
};

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <AuthWrapper />
      </AuthProvider>
    </QueryClientProvider>
  );
}

export default App;
