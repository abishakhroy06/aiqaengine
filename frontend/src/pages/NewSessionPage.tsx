import { useState, useRef, DragEvent } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { PageWrapper } from '../components/layout/PageWrapper';
import { GlassCard } from '../components/ui/GlassCard';
import { GradientButton } from '../components/ui/GradientButton';
import { AnimatedInput } from '../components/ui/AnimatedInput';
import { TemplateSelector } from '../components/session/TemplateSelector';
import { useCreateSession } from '../hooks/useSession';
import { sessionService } from '../services/sessionService';
import { QAContext } from '../types/session';
import { BuiltInTemplateId } from '../types/template';

type Step = 'requirement' | 'context' | 'template' | 'generate';
type InputMode = 'paste' | 'upload';

export default function NewSessionPage() {
  const navigate = useNavigate();
  const createSession = useCreateSession();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [step, setStep] = useState<Step>('requirement');
  const [inputMode, setInputMode] = useState<InputMode>('paste');
  const [name, setName] = useState('');
  const [requirement, setRequirement] = useState('');
  const [uploadedFileName, setUploadedFileName] = useState('');
  const [isDragging, setIsDragging] = useState(false);
  const [isExtracting, setIsExtracting] = useState(false);
  const [extractError, setExtractError] = useState('');
  const [context, setContext] = useState<QAContext>({
    product: '', platform: '', users_roles: '',
    rules_constraints: '', risks: '', environment: '',
  });
  const [selectedTemplate, setSelectedTemplate] = useState<BuiltInTemplateId>('full');
  const [error, setError] = useState('');

  const handleFile = async (file: File) => {
    setExtractError('');
    const allowed = ['pdf', 'docx', 'doc', 'txt', 'md'];
    const ext = file.name.split('.').pop()?.toLowerCase() || '';
    if (!allowed.includes(ext)) {
      setExtractError('Unsupported file type. Please upload a PDF, DOCX, or TXT file.');
      return;
    }
    setIsExtracting(true);
    try {
      const result = await sessionService.extractTextFromFile(file);
      setRequirement(result.text);
      setUploadedFileName(file.name);
      if (!name) setName(file.name.replace(/\.[^/.]+$/, ''));
    } catch (e: unknown) {
      const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
      setExtractError(msg || 'Failed to extract text from file. Please try again.');
    } finally {
      setIsExtracting(false);
    }
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) handleFile(file);
  };

  const handleGenerate = async () => {
    setError('');
    try {
      const session = await createSession.mutateAsync({
        name: name || `Session ${new Date().toLocaleDateString()}`,
        requirement,
        context,
        template: selectedTemplate,
      });
      navigate(`/sessions/${session.id}`);
    } catch {
      setError('Failed to create session. Please try again.');
    }
  };

  const updateContext = (field: keyof QAContext, value: string) => {
    setContext(prev => ({ ...prev, [field]: value }));
  };

  const steps: Step[] = ['requirement', 'context', 'template', 'generate'];
  const stepIndex = steps.indexOf(step);

  return (
    <PageWrapper>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-100 px-8 py-6">
          <div className="max-w-3xl mx-auto">
            <button
              onClick={() => navigate('/sessions')}
              className="text-gray-400 hover:text-gray-600 text-sm mb-2 flex items-center gap-1"
            >
              ← Back to Sessions
            </button>
            <h1 className="text-2xl font-bold text-gray-900">New QA Session</h1>
            <p className="text-gray-500 text-sm mt-1">Upload your requirement document or paste the text — AI generates test cases strictly from what's written.</p>
          </div>
        </div>

        {/* Progress */}
        <div className="max-w-3xl mx-auto px-8 pt-6">
          <div className="flex items-center gap-2 mb-8">
            {['Requirement', 'Context', 'Template', 'Generate'].map((label, i) => (
              <div key={label} className="flex items-center gap-2">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-sm font-bold transition-colors ${
                  i < stepIndex ? 'bg-green-500 text-white' :
                  i === stepIndex ? 'bg-purple-500 text-white' :
                  'bg-gray-200 text-gray-400'
                }`}>
                  {i < stepIndex ? '✓' : i + 1}
                </div>
                <span className={`text-sm font-medium ${i === stepIndex ? 'text-purple-700' : 'text-gray-400'}`}>
                  {label}
                </span>
                {i < steps.length - 1 && <div className="w-8 h-px bg-gray-200 mx-1" />}
              </div>
            ))}
          </div>
        </div>

        <div className="max-w-3xl mx-auto px-8 pb-12">
          <AnimatePresence mode="wait">

            {/* Step 1: Requirement */}
            {step === 'requirement' && (
              <motion.div
                key="requirement"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <GlassCard>
                  <h2 className="text-xl font-bold text-gray-800 mb-1">Requirement Document</h2>
                  <p className="text-gray-500 text-sm mb-5">
                    Upload a document or paste your requirement text. Test cases will be generated strictly from this content — nothing will be assumed or added.
                  </p>

                  <AnimatedInput
                    label="Session Name (optional)"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="e.g. Login Feature QA"
                    className="mb-5"
                  />

                  {/* Toggle */}
                  <div className="flex bg-gray-100 rounded-xl p-1 mb-5 w-fit">
                    {(['upload', 'paste'] as InputMode[]).map((mode) => (
                      <button
                        key={mode}
                        onClick={() => { setInputMode(mode); setExtractError(''); }}
                        className={`px-5 py-2 rounded-lg text-sm font-medium transition-all ${
                          inputMode === mode
                            ? 'bg-white text-purple-700 shadow-sm'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                      >
                        {mode === 'upload' ? '📎 Upload Document' : '✏️ Paste Text'}
                      </button>
                    ))}
                  </div>

                  {inputMode === 'upload' && (
                    <div className="space-y-3">
                      {/* Drop zone */}
                      <div
                        onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                        onDragLeave={() => setIsDragging(false)}
                        onDrop={handleDrop}
                        onClick={() => fileInputRef.current?.click()}
                        className={`border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all ${
                          isDragging
                            ? 'border-purple-400 bg-purple-50'
                            : 'border-gray-300 hover:border-purple-300 hover:bg-gray-50'
                        }`}
                      >
                        <input
                          ref={fileInputRef}
                          type="file"
                          accept=".pdf,.docx,.doc,.txt,.md"
                          className="hidden"
                          onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                        />
                        {isExtracting ? (
                          <div className="space-y-2">
                            <div className="w-8 h-8 border-2 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto" />
                            <p className="text-sm text-gray-500">Extracting text...</p>
                          </div>
                        ) : uploadedFileName ? (
                          <div className="space-y-1">
                            <p className="text-2xl">📄</p>
                            <p className="text-sm font-medium text-green-700">{uploadedFileName}</p>
                            <p className="text-xs text-gray-400">{requirement.length.toLocaleString()} characters extracted — click to replace</p>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            <p className="text-3xl">📂</p>
                            <p className="text-sm font-medium text-gray-700">Drop your file here or click to browse</p>
                            <p className="text-xs text-gray-400">Supports PDF, DOCX, TXT — max 10 MB</p>
                          </div>
                        )}
                      </div>

                      {extractError && (
                        <p className="text-red-500 text-sm">{extractError}</p>
                      )}

                      {/* Show extracted text preview */}
                      {requirement && (
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">
                            Extracted Text <span className="text-gray-400 font-normal">(review and edit if needed)</span>
                          </label>
                          <textarea
                            value={requirement}
                            onChange={(e) => setRequirement(e.target.value)}
                            className="w-full h-48 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 outline-none transition-colors bg-white/80 resize-none text-sm font-mono"
                          />
                        </div>
                      )}
                    </div>
                  )}

                  {inputMode === 'paste' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Requirement Text <span className="text-red-400">*</span>
                      </label>
                      <motion.textarea
                        whileFocus={{ scale: 1.005 }}
                        value={requirement}
                        onChange={(e) => setRequirement(e.target.value)}
                        placeholder="Paste your full requirement document, user story, BRD, or feature specification here..."
                        className="w-full h-56 px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-purple-400 outline-none transition-colors bg-white/80 resize-none"
                      />
                      <p className="text-xs text-gray-400 mt-1">{requirement.length.toLocaleString()} characters</p>
                    </div>
                  )}

                  <GradientButton
                    onClick={() => setStep('context')}
                    disabled={!requirement.trim() || isExtracting}
                    className="w-full mt-5"
                  >
                    Next: Add Context →
                  </GradientButton>
                </GlassCard>
              </motion.div>
            )}

            {/* Step 2: Context */}
            {step === 'context' && (
              <motion.div
                key="context"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <GlassCard>
                  <h2 className="text-xl font-bold text-gray-800 mb-1">Context Pack</h2>
                  <p className="text-gray-500 text-sm mb-4">
                    Optional but recommended — helps the AI understand constraints, roles, and environment without inventing them.
                  </p>
                  <div className="grid grid-cols-2 gap-4">
                    <AnimatedInput
                      label="Product / Domain"
                      value={context.product}
                      onChange={(e) => updateContext('product', e.target.value)}
                      placeholder="e.g. E-commerce, Banking, SaaS"
                    />
                    <AnimatedInput
                      label="Platform"
                      value={context.platform}
                      onChange={(e) => updateContext('platform', e.target.value)}
                      placeholder="e.g. Web, iOS, Android, API"
                    />
                    <AnimatedInput
                      label="Users / Roles"
                      value={context.users_roles}
                      onChange={(e) => updateContext('users_roles', e.target.value)}
                      placeholder="e.g. Admin, Customer, Guest"
                    />
                    <AnimatedInput
                      label="Rules / Constraints"
                      value={context.rules_constraints}
                      onChange={(e) => updateContext('rules_constraints', e.target.value)}
                      placeholder="e.g. Max 100 chars, GDPR compliant"
                    />
                    <AnimatedInput
                      label="Risks"
                      value={context.risks}
                      onChange={(e) => updateContext('risks', e.target.value)}
                      placeholder="e.g. Data loss, Payment failure"
                    />
                    <AnimatedInput
                      label="Environment"
                      value={context.environment}
                      onChange={(e) => updateContext('environment', e.target.value)}
                      placeholder="e.g. Production, Staging, Dev"
                    />
                  </div>
                  <div className="flex gap-3 mt-6">
                    <GradientButton variant="secondary" onClick={() => setStep('requirement')} className="flex-1">
                      ← Back
                    </GradientButton>
                    <GradientButton onClick={() => setStep('template')} className="flex-1">
                      Next: Template →
                    </GradientButton>
                  </div>
                </GlassCard>
              </motion.div>
            )}

            {/* Step 3: Template */}
            {step === 'template' && (
              <motion.div
                key="template"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <GlassCard>
                  <h2 className="text-xl font-bold text-gray-800 mb-1">Output Template</h2>
                  <p className="text-gray-500 text-sm mb-5">
                    Choose how test cases are displayed. The AI always generates all fields — this controls what you see and export.
                  </p>
                  <TemplateSelector selected={selectedTemplate} onChange={setSelectedTemplate} />
                  <div className="flex gap-3 mt-6">
                    <GradientButton variant="secondary" onClick={() => setStep('context')} className="flex-1">
                      ← Back
                    </GradientButton>
                    <GradientButton onClick={() => setStep('generate')} className="flex-1">
                      Next: Generate →
                    </GradientButton>
                  </div>
                </GlassCard>
              </motion.div>
            )}

            {/* Step 4: Confirm & Generate */}
            {step === 'generate' && (
              <motion.div
                key="generate"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
              >
                <GlassCard>
                  <h2 className="text-xl font-bold text-gray-800 mb-4">Ready to Generate</h2>

                  <div className="bg-gray-50 rounded-xl p-4 mb-4 space-y-2 text-sm text-gray-700">
                    {uploadedFileName && (
                      <p><span className="font-medium">Source:</span> 📄 {uploadedFileName}</p>
                    )}
                    <p>
                      <span className="font-medium">Requirement:</span>{' '}
                      {requirement.slice(0, 150)}{requirement.length > 150 ? '...' : ''}
                    </p>
                    <p><span className="font-medium">Length:</span> {requirement.length.toLocaleString()} characters</p>
                    {context.product && <p><span className="font-medium">Product:</span> {context.product}</p>}
                    {context.platform && <p><span className="font-medium">Platform:</span> {context.platform}</p>}
                    <p><span className="font-medium">Template:</span> {selectedTemplate.charAt(0).toUpperCase() + selectedTemplate.slice(1)}</p>
                  </div>

                  <div className="bg-purple-50 rounded-xl p-4 mb-6 text-sm text-purple-700">
                    <p className="font-medium mb-2">Generation guarantees:</p>
                    <ul className="space-y-1">
                      <li>✓ Every test case traces back to your requirement</li>
                      <li>✓ No features invented beyond what's written</li>
                      <li>✓ No duplicate test cases</li>
                      <li>✓ Every requirement line covered</li>
                      <li>✓ Scenario Map, Test Cases, Assumptions, Questions, Checklist</li>
                    </ul>
                  </div>

                  {error && (
                    <p className="text-red-500 text-sm mb-4 text-center">{error}</p>
                  )}

                  <div className="flex gap-3">
                    <GradientButton variant="secondary" onClick={() => setStep('template')} className="flex-1">
                      ← Back
                    </GradientButton>
                    <GradientButton
                      onClick={handleGenerate}
                      isLoading={createSession.isPending}
                      className="flex-1"
                    >
                      ✨ Generate Test Cases
                    </GradientButton>
                  </div>
                </GlassCard>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </PageWrapper>
  );
}
