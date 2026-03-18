import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { PageWrapper } from '../components/layout/PageWrapper';
import { MeshBackground } from '../components/layout/MeshBackground';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { AnimatedInput } from '../components/ui/AnimatedInput';
import { authService } from '../services/authService';
import { useAuth } from '../context/AuthContext';
import { motion } from 'framer-motion';

export default function RegisterPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (password.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    setIsLoading(true);
    try {
      await authService.register(email, password, fullName);
      await login(email, password);
      navigate('/dashboard');
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      setError(axiosErr.response?.data?.detail ?? 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageWrapper>
      <MeshBackground />
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="w-full max-w-md">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
              AI QA Engine
            </h1>
            <p className="text-gray-500 mt-2">Create your free account</p>
          </motion.div>

          <GlassCard>
            <form onSubmit={handleSubmit} className="space-y-4">
              <AnimatedInput
                label="Full Name"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Jane Smith"
              />
              <AnimatedInput
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
              <AnimatedInput
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
              />
              {error && (
                <motion.p
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="text-red-500 text-sm text-center"
                >
                  {error}
                </motion.p>
              )}
              <GradientButton type="submit" isLoading={isLoading} className="w-full">
                Create Account
              </GradientButton>
            </form>
            <p className="text-center text-sm text-gray-500 mt-4">
              Already have an account?{' '}
              <Link to="/login" className="text-purple-600 hover:text-purple-700 font-medium">
                Sign in
              </Link>
            </p>
          </GlassCard>
        </div>
      </div>
    </PageWrapper>
  );
}
