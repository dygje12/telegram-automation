import { useState } from 'react';
import { useAuth } from '../../hooks/useAuth.jsx';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2, MessageSquare, ArrowLeft } from 'lucide-react';

export const CodeVerification = () => {
  const { verifyCode, resetAuth, isLoading, tempData } = useAuth();
  const [code, setCode] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!code.trim()) {
      setError('Please enter the verification code');
      return;
    }

    const result = await verifyCode(code.trim());
    if (!result.success) {
      setError(result.message);
    }
  };

  const handleBack = () => {
    resetAuth();
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 p-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <CardTitle className="text-2xl font-bold text-gray-900">
            Verify Your Phone
          </CardTitle>
          <CardDescription>
            We sent a verification code to {tempData?.phone_number}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="code" className="flex items-center gap-2">
                <MessageSquare className="w-4 h-4" />
                Verification Code
              </Label>
              <Input
                id="code"
                name="code"
                type="text"
                placeholder="Enter 5-digit code"
                value={code}
                onChange={(e) => setCode(e.target.value)}
                disabled={isLoading}
                maxLength={5}
                className="text-center text-lg tracking-widest"
                required
              />
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            <div className="space-y-2">
              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading}
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Verifying...
                  </>
                ) : (
                  'Verify Code'
                )}
              </Button>

              <Button 
                type="button" 
                variant="outline" 
                className="w-full" 
                onClick={handleBack}
                disabled={isLoading}
              >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Back to Login
              </Button>
            </div>
          </form>

          <div className="mt-6 text-sm text-gray-600 text-center">
            <p>Check your Telegram app for the verification code.</p>
            <p className="mt-2">The code should arrive within a few seconds.</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

