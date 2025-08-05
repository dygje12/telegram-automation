import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth.jsx';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, Phone, Key, Hash } from 'lucide-react';

export const LoginForm = () => {
  const { login, isLoading } = useAuth();
  const [formData, setFormData] = useState({
    api_id: '',
    api_hash: '',
    phone_number: ''
  });
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.api_id || !formData.api_hash || !formData.phone_number) {
      setError('Please fill in all fields');
      return;
    }

    const result = await login(formData);
    if (!result.success) {
      setError(result.message);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">
            Telegram Automation
          </CardTitle>
          <CardDescription>
            Sign in with your Telegram API credentials
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="api_id" className="flex items-center gap-2">
                <Hash className="w-4 h-4" />
                API ID
              </Label>
              <Input
                id="api_id"
                name="api_id"
                type="text"
                placeholder="Enter your API ID"
                value={formData.api_id}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="api_hash" className="flex items-center gap-2">
                <Key className="w-4 h-4" />
                API Hash
              </Label>
              <Input
                id="api_hash"
                name="api_hash"
                type="text"
                placeholder="Enter your API Hash"
                value={formData.api_hash}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="phone_number" className="flex items-center gap-2">
                <Phone className="w-4 h-4" />
                Phone Number
              </Label>
              <Input
                id="phone_number"
                name="phone_number"
                type="tel"
                placeholder="+1234567890"
                value={formData.phone_number}
                onChange={handleChange}
                disabled={isLoading}
                required
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <Button 
              type="submit" 
              className="w-full" 
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Sending Code...
                </>
              ) : (
                'Send Verification Code'
              )}
            </Button>
          </form>

          <div className="mt-6 text-sm text-gray-600">
            <p className="mb-2">
              <strong>How to get API credentials:</strong>
            </p>
            <ol className="list-decimal list-inside space-y-1 text-xs">
              <li>Go to <a href="https://my.telegram.org" target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">my.telegram.org</a></li>
              <li>Log in with your phone number</li>
              <li>Go to "API development tools"</li>
              <li>Create a new application</li>
              <li>Copy your API ID and API Hash</li>
            </ol>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

