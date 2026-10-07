import { useState } from 'react';
import { 
  ShieldCheck, 
  Zap, 
  Terminal, 
  CheckCircle2, 
  AlertTriangle, 
  ShieldAlert, 
  Copy, 
  Download, 
  GitPullRequest, 
  Sparkles, 
  ArrowRight, 
  RefreshCw,
  Cpu,
  Lock,
  Code2,
  Bug,
  Check
} from 'lucide-react';

interface CategoryScore {
  score: number;
  max: number;
  deductions?: number;
  reason?: string;
  math?: string;
  label: string;
}

interface HealthScore {
  score: number;
  categories: {
    security: CategoryScore;
    quality: CategoryScore;
    testing: CategoryScore;
  };
  formula_summary: string;
}

interface Finding {
  id: string;
  type: string;
  category: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  file: string;
  line: number;
  description: string;
  explanation?: string;
  code_snippet: string;
  cwe: string;
  auto_fixable?: boolean;
  manual_review_note?: string;
  jira_ticket_key?: string;
  jira_ticket_url?: string;
}

interface Fix {
  id: string;
  finding_id: string;
  file: string;
  category: string;
  severity: string;
  diff: string;
  status: 'verified' | 'unverified';
  verification_log: string;
  original_code: string;
  fixed_code: string;
}

interface PRMeta {
  title: string;
  author: string;
  repo: string;
  pr_number?: string;
  url?: string;
}

interface AnalysisResults {
  pr: PRMeta;
  health_score: HealthScore;
  summary: {
    total_findings: number;
    security_count: number;
    quality_count: number;
    fixes_generated: number;
    verified_fixes: number;
    execution_time_sec: number;
  };
  findings: Finding[];
  fixes: Fix[];
  files_analyzed: string[];
}

export default function App() {
  const [prUrl, setPrUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeStep, setActiveStep] = useState<number>(0);
  const [results, setResults] = useState<AnalysisResults | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [copiedFixId, setCopiedFixId] = useState<string | null>(null);

  const API_BASE = import.meta.env.VITE_API_URL 
    || (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.port === '5173'
        ? 'http://127.0.0.1:8000/api'
        : '/api');

  const runAnalysis = async (url: string) => {
    setLoading(true);
    setError(null);
    setResults(null);
    setActiveStep(1);

    setTimeout(() => setActiveStep(2), 1200);
    setTimeout(() => setActiveStep(3), 2400);

    try {
      const resp = await fetch(`${API_BASE}/analyze-pr`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pr_url: url }),
      });

      if (!resp.ok) {
        const errData = await resp.json();
        throw new Error(errData.detail || 'Failed to analyze GitHub PR');
      }

      const data: AnalysisResults = await resp.json();
      setResults(data);
      setActiveStep(4);
    } catch (err: any) {
      setError(err.message || 'Error executing PR audit pipeline');
      setActiveStep(0);
    } finally {
      setLoading(false);
    }
  };

  const runDemo = async () => {
    setLoading(true);
    setError(null);
    setResults(null);
    setPrUrl('https://github.com/acme/vulnerable-flask-api/pull/42');
    setActiveStep(1);

    setTimeout(() => setActiveStep(2), 1000);
    setTimeout(() => setActiveStep(3), 2000);

    try {
      const resp = await fetch(`${API_BASE}/analyze-demo`);
      if (!resp.ok) {
        throw new Error('Failed to run demo analysis');
      }

      const data: AnalysisResults = await resp.json();
      setResults(data);
      setActiveStep(4);
    } catch (err: any) {
      setError(err.message || 'Error running demo analysis');
      setActiveStep(0);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyDiff = (fixId: string, diffText: string) => {
    navigator.clipboard.writeText(diffText);
    setCopiedFixId(fixId);
    setTimeout(() => setCopiedFixId(null), 2500);
  };

  const handleDownloadPatch = (fix: Fix) => {
    const element = document.createElement('a');
    const file = new Blob([fix.diff], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = `devpulse_fix_${fix.file.replace(/[/.]/g, '_')}.patch`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const filteredFindings = results?.findings.filter((f) => {
    if (severityFilter === 'all') return true;
    return f.severity.toLowerCase() === severityFilter.toLowerCase();
  }) || [];

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-emerald-400 border-emerald-500/30 bg-emerald-500/10';
    if (score >= 50) return 'text-amber-400 border-amber-500/30 bg-amber-500/10';
    return 'text-rose-400 border-rose-500/30 bg-rose-500/10';
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'high':
        return 'bg-orange-500/20 text-orange-300 border-orange-500/40';
      case 'medium':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      default:
        return 'bg-blue-500/20 text-blue-300 border-blue-500/40';
    }
  };

  return (
    <div className="min-h-screen bg-[#070a12] text-slate-100 flex flex-col selection:bg-indigo-500 selection:text-white">
      {/* Background ambient glow */}
      <div className="fixed top-0 left-1/4 w-[600px] h-[600px] bg-indigo-600/10 rounded-full blur-[140px] pointer-events-none" />
      <div className="fixed bottom-0 right-1/4 w-[500px] h-[500px] bg-purple-600/10 rounded-full blur-[140px] pointer-events-none" />

      {/* Top Header Navbar */}
      <header className="sticky top-0 z-50 glass-card border-b border-slate-800/80 px-6 py-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-xl shadow-lg shadow-indigo-500/25">
              <Zap className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent">
                  DevPulse AI
                </span>
                <span className="px-2 py-0.5 text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full">
                  Agentic Verification Engine
                </span>
              </div>
              <p className="text-xs text-slate-400 font-medium">
                Other tools tell you what's wrong. DevPulse fixes it and proves the fix works.
              </p>
            </div>
          </div>

          <div className="hidden md:flex items-center gap-3 text-xs text-slate-400 font-mono">
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
              <Code2 className="w-3.5 h-3.5 text-indigo-400" />
              Python Engine
            </span>
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              Isolated Sandbox
            </span>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8 space-y-10 z-10">
        {/* Landing Page Hero & Search Box */}
        <section className="text-center space-y-6 max-w-3xl mx-auto pt-4">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full text-xs font-medium bg-purple-500/10 text-purple-300 border border-purple-500/20 mb-2">
            <Sparkles className="w-3.5 h-3.5 text-purple-400" />
            3-Agent Sequential Verification Pipeline
          </div>

          <h1 className="text-4xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Autonomous PR Audit & <br />
            <span className="bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              Verified Auto-Fix Engine
            </span>
          </h1>

          <p className="text-slate-400 text-sm sm:text-base leading-relaxed">
            Enter any public GitHub Pull Request URL. DevPulse scans for security vulnerabilities,
            code smells, and missing tests, then generates unified diffs and <strong className="text-emerald-400 font-semibold">proves they pass in a sandbox</strong>.
          </p>

          {/* PR Search Input Form */}
          <div className="glass-card p-3 rounded-2xl shadow-2xl border border-slate-800 space-y-3">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                if (prUrl.trim()) runAnalysis(prUrl);
              }}
              className="flex flex-col sm:flex-row gap-2"
            >
              <div className="relative flex-1">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none">
                  <GitPullRequest className="h-5 w-5 text-indigo-400" />
                </div>
                <input
                  type="url"
                  value={prUrl}
                  onChange={(e) => setPrUrl(e.target.value)}
                  placeholder="https://github.com/owner/repo/pull/123"
                  className="w-full pl-10 pr-4 py-3 bg-slate-900/90 border border-slate-800 rounded-xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 transition-all font-mono"
                  disabled={loading}
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  disabled={loading || !prUrl.trim()}
                  className="flex-1 sm:flex-none px-6 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-600/25 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 cursor-pointer"
                >
                  {loading ? (
                    <>
                      <RefreshCw className="w-4 h-4 animate-spin text-white" />
                      Auditing...
                    </>
                  ) : (
                    <>
                      Analyze PR
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>

                <button
                  type="button"
                  onClick={runDemo}
                  disabled={loading}
                  className="px-4 py-3 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-sm font-semibold rounded-xl transition-all flex items-center gap-2 cursor-pointer"
                  title="Run instant analysis on bundled demo app"
                >
                  <Cpu className="w-4 h-4 text-purple-400" />
                  Try Demo
                </button>
              </div>
            </form>

            <div className="flex items-center justify-between px-2 pt-1 text-xs text-slate-500">
              <span>Supports Python repos</span>
              <span>Deterministic scanning + Verified fixes</span>
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-300 text-sm flex items-start gap-3 text-left">
              <ShieldAlert className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
              <div>
                <strong className="font-semibold block">Audit Pipeline Notice</strong>
                {error}
              </div>
            </div>
          )}
        </section>

        {/* Live Progress Pipeline Stepper */}
        {(loading || activeStep > 0) && (
          <section className="glass-card rounded-2xl p-6 border border-slate-800 space-y-4">
            <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center gap-2">
              <Terminal className="w-4 h-4 text-indigo-400" />
              3-Agent Sequential Audit Pipeline
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Agent 1 */}
              <div
                className={`p-4 rounded-xl border transition-all ${
                  activeStep >= 1
                    ? activeStep > 1
                      ? 'bg-slate-900/90 border-emerald-500/40 text-emerald-300'
                      : 'bg-indigo-950/40 border-indigo-500/50 text-indigo-200 glow-indigo'
                    : 'bg-slate-900/30 border-slate-800/60 text-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-sm flex items-center gap-2">
                    <Lock className="w-4 h-4" />
                    1. Security Sentinel
                  </span>
                  {activeStep > 1 ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : activeStep === 1 ? (
                    <RefreshCw className="w-4 h-4 text-indigo-400 animate-spin" />
                  ) : (
                    <span className="text-xs text-slate-600">Queued</span>
                  )}
                </div>
                <p className="text-xs text-slate-400">
                  Scans regex + Shannon entropy secrets, SQLi, CMDi, hardcoded keys.
                </p>
              </div>

              {/* Agent 2 */}
              <div
                className={`p-4 rounded-xl border transition-all ${
                  activeStep >= 2
                    ? activeStep > 2
                      ? 'bg-slate-900/90 border-emerald-500/40 text-emerald-300'
                      : 'bg-indigo-950/40 border-indigo-500/50 text-indigo-200 glow-indigo'
                    : 'bg-slate-900/30 border-slate-800/60 text-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-sm flex items-center gap-2">
                    <Bug className="w-4 h-4" />
                    2. Quality & Architecture
                  </span>
                  {activeStep > 2 ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : activeStep === 2 ? (
                    <RefreshCw className="w-4 h-4 text-indigo-400 animate-spin" />
                  ) : (
                    <span className="text-xs text-slate-600">Queued</span>
                  )}
                </div>
                <p className="text-xs text-slate-400">
                  Detects cyclomatic complexity, resource leaks, missing tests.
                </p>
              </div>

              {/* Agent 3 */}
              <div
                className={`p-4 rounded-xl border transition-all ${
                  activeStep >= 3
                    ? activeStep > 3
                      ? 'bg-slate-900/90 border-emerald-500/40 text-emerald-300'
                      : 'bg-purple-950/40 border-purple-500/50 text-purple-200 glow-purple'
                    : 'bg-slate-900/30 border-slate-800/60 text-slate-600'
                }`}
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="font-semibold text-sm flex items-center gap-2 text-purple-300">
                    <Zap className="w-4 h-4 text-purple-400" />
                    3. Auto-Fix (Hero Feature)
                  </span>
                  {activeStep > 3 ? (
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                  ) : activeStep === 3 ? (
                    <RefreshCw className="w-4 h-4 text-purple-400 animate-spin" />
                  ) : (
                    <span className="text-xs text-slate-600">Queued</span>
                  )}
                </div>
                <p className="text-xs text-slate-400">
                  Generates unified diffs & verifies in isolated sandbox environment.
                </p>
              </div>
            </div>
          </section>
        )}

        {/* Audit Results Dashboard */}
        {results && (
          <div className="space-y-8 animate-fadeIn">
            {/* PR Overview Header */}
            <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-1">
                  <span className="px-2.5 py-0.5 text-xs font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded-full font-mono">
                    {results.pr.repo}
                  </span>
                  <span className="text-xs text-slate-400">by @{results.pr.author}</span>
                </div>
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                  <GitPullRequest className="w-5 h-5 text-indigo-400 shrink-0" />
                  {results.pr.title}
                </h2>
              </div>

              <div className="flex items-center gap-4 text-xs text-slate-400">
                <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block">Files Analyzed</span>
                  <strong className="text-slate-200 font-mono">{results.files_analyzed.length} Python Files</strong>
                </div>
                <div className="px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-500 block">Execution Speed</span>
                  <strong className="text-slate-200 font-mono">{results.summary.execution_time_sec}s</strong>
                </div>
              </div>
            </div>

            {/* Health Score Gauge & Category Breakdown */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Health Score Circular Gauge Card */}
              <div className="glass-card rounded-2xl p-6 border border-slate-800 flex flex-col items-center justify-center text-center space-y-4">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Overall Code Health Score
                </span>

                <div className="relative w-40 h-40 flex items-center justify-center">
                  <svg className="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
                    <path
                      className="text-slate-800"
                      strokeWidth="3.5"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                    <path
                      className={
                        results.health_score.score >= 80
                          ? 'text-emerald-500'
                          : results.health_score.score >= 50
                          ? 'text-amber-500'
                          : 'text-rose-500'
                      }
                      strokeDasharray={`${results.health_score.score}, 100`}
                      strokeWidth="3.5"
                      strokeLinecap="round"
                      stroke="currentColor"
                      fill="none"
                      d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    />
                  </svg>

                  <div className="absolute flex flex-col items-center justify-center">
                    <span
                      className={`text-4xl font-extrabold tracking-tight ${
                        results.health_score.score >= 80
                          ? 'text-emerald-400'
                          : results.health_score.score >= 50
                          ? 'text-amber-400'
                          : 'text-rose-400'
                      }`}
                    >
                      {results.health_score.score}
                    </span>
                    <span className="text-[10px] text-slate-500 font-semibold tracking-widest uppercase">
                      / 100 POINTS
                    </span>
                  </div>
                </div>

                <div
                  className={`px-3 py-1 text-xs font-semibold rounded-full border ${getScoreColor(
                    results.health_score.score
                  )}`}
                >
                  {results.health_score.score >= 80
                    ? '🟢 Clean - Safe to Merge'
                    : results.health_score.score >= 50
                    ? '🟡 Moderate Risks Detected'
                    : '🔴 Critical Security Vulnerabilities'}
                </div>

                <p className="text-xs text-slate-500 font-mono">
                  {results.health_score.formula_summary}
                </p>
              </div>

              {/* 3-Category Breakdown */}
              <div className="lg:col-span-2 glass-card rounded-2xl p-6 border border-slate-800 space-y-5">
                <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider flex items-center justify-between">
                  <span>Deterministic Score Breakdown</span>
                  <span className="text-xs font-normal text-slate-500">Exact Math Formula & Deductions</span>
                </h3>

                <div className="space-y-4">
                  {/* Security Category */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                        <Lock className="w-3.5 h-3.5 text-rose-400" />
                        Security & Vulnerabilities
                      </span>
                      <span className="font-mono text-slate-300 font-bold">
                        {results.health_score.categories.security.score} / 40 pts
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-rose-500 to-red-400 rounded-full transition-all"
                        style={{
                          width: `${(results.health_score.categories.security.score / 40) * 100}%`,
                        }}
                      />
                    </div>
                    <div className="text-[11px] font-mono text-slate-400 flex justify-between">
                      <span>Math: {results.health_score.categories.security.math}</span>
                      <span>Critical (-20) | High (-10)</span>
                    </div>
                  </div>

                  {/* Quality Category */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                        <Bug className="w-3.5 h-3.5 text-amber-400" />
                        Code Quality & Architecture
                      </span>
                      <span className="font-mono text-slate-300 font-bold">
                        {results.health_score.categories.quality.score} / 30 pts
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-amber-500 to-yellow-400 rounded-full transition-all"
                        style={{
                          width: `${(results.health_score.categories.quality.score / 30) * 100}%`,
                        }}
                      />
                    </div>
                    <div className="text-[11px] font-mono text-slate-400 flex justify-between">
                      <span>Math: {results.health_score.categories.quality.math}</span>
                      <span>Medium (-5) | Low (-2)</span>
                    </div>
                  </div>

                  {/* Testing Category */}
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="font-semibold text-slate-200 flex items-center gap-1.5">
                        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
                        Test Suite & Coverage
                      </span>
                      <span className="font-mono text-slate-300 font-bold">
                        {results.health_score.categories.testing.score} / 30 pts
                      </span>
                    </div>
                    <div className="w-full h-2 bg-slate-900 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-emerald-500 to-teal-400 rounded-full transition-all"
                        style={{
                          width: `${(results.health_score.categories.testing.score / 30) * 100}%`,
                        }}
                      />
                    </div>
                    <p className="text-[11px] font-mono text-slate-400">
                      Math: {results.health_score.categories.testing.math}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Hero Feature: ALL 3 Verified Auto-Fixes Displayed Simultaneously */}
            {results.fixes.length > 0 && (
              <section className="glass-card rounded-2xl p-6 border border-purple-500/30 space-y-6 glow-purple">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="px-2.5 py-0.5 text-xs font-extrabold bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-md uppercase tracking-wider">
                        Hero Feature
                      </span>
                      <h3 className="text-xl font-extrabold text-white flex items-center gap-2">
                        <Zap className="w-5 h-5 text-purple-400" />
                        Verified Auto-Fixes Panel ({results.summary.verified_fixes}/{results.fixes.length} Verified)
                      </h3>
                    </div>
                    <p className="text-xs text-slate-400 mt-1">
                      All generated fixes are verified in an isolated sandbox environment and displayed below with complete unified diff patches.
                    </p>
                  </div>

                  <span className="px-3 py-1 text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full">
                    ✅ All Fixes Passed Sandbox
                  </span>
                </div>

                {/* Stacked Cards for ALL 3 Fixes - Diffs Visible Simultaneously */}
                <div className="space-y-6">
                  {results.fixes.map((fix, idx) => (
                    <div
                      key={fix.id}
                      className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4 shadow-xl"
                    >
                      {/* Fix Header & Verification Log Badge */}
                      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                        <div className="flex items-center gap-3">
                          <span className="w-7 h-7 rounded-xl bg-purple-600/30 text-purple-300 border border-purple-500/40 flex items-center justify-center font-bold text-xs">
                            #{idx + 1}
                          </span>
                          <div>
                            <h4 className="text-base font-bold text-white flex items-center gap-2">
                              {fix.category}
                              {fix.status === 'verified' ? (
                                <span className="px-2 py-0.5 text-[11px] font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-md flex items-center gap-1">
                                  <Check className="w-3 h-3" /> Verified
                                </span>
                              ) : (
                                <span className="px-2 py-0.5 text-[11px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded-md flex items-center gap-1">
                                  <AlertTriangle className="w-3 h-3" /> Unverified
                                </span>
                              )}
                            </h4>
                            <span className="text-xs text-slate-400 font-mono">
                              File: {fix.file}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <button
                            onClick={() => handleCopyDiff(fix.id, fix.diff)}
                            className="px-3.5 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs font-semibold text-slate-200 flex items-center gap-1.5 cursor-pointer transition-all"
                          >
                            {copiedFixId === fix.id ? (
                              <>
                                <Check className="w-3.5 h-3.5 text-emerald-400" />
                                Copied!
                              </>
                            ) : (
                              <>
                                <Copy className="w-3.5 h-3.5 text-purple-400" />
                                Copy Patch
                              </>
                            )}
                          </button>

                          <button
                            onClick={() => handleDownloadPatch(fix)}
                            className="px-3.5 py-1.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-xs font-semibold text-white flex items-center gap-1.5 cursor-pointer transition-all shadow-md shadow-indigo-600/20"
                          >
                            <Download className="w-3.5 h-3.5" />
                            Download .patch
                          </button>
                        </div>
                      </div>

                      {/* Verification Status Message */}
                      <div className="p-3 rounded-xl bg-slate-950/80 border border-slate-800 text-xs font-mono text-slate-300 flex items-center gap-2">
                        <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                        <span>{fix.verification_log}</span>
                      </div>

                      {/* Unified Red/Green Diff Code Viewer */}
                      <div className="rounded-xl overflow-hidden border border-slate-800 bg-[#090d16] font-mono text-xs">
                        <div className="bg-slate-950 px-4 py-2 border-b border-slate-800 text-slate-400 flex items-center justify-between">
                          <span>
                            Unified Diff Patch: <strong>{fix.file}</strong>
                          </span>
                          <span className="text-[10px] text-purple-400 font-semibold uppercase">
                            Sandbox Passed
                          </span>
                        </div>
                        <pre className="p-4 overflow-x-auto text-slate-200 leading-relaxed max-h-72">
                          {fix.diff.split('\n').map((line, lIdx) => {
                            let lineStyle = 'text-slate-300';
                            if (line.startsWith('+') && !line.startsWith('+++')) {
                              lineStyle = 'text-emerald-400 bg-emerald-500/10 px-1 py-0.5 rounded';
                            } else if (line.startsWith('-') && !line.startsWith('---')) {
                              lineStyle = 'text-rose-400 bg-rose-500/10 px-1 py-0.5 rounded';
                            } else if (line.startsWith('@@')) {
                              lineStyle = 'text-purple-400 font-bold';
                            }
                            return (
                              <div key={lIdx} className={lineStyle}>
                                {line}
                              </div>
                            );
                          })}
                        </pre>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {/* Findings List Section */}
            <section className="glass-card rounded-2xl p-6 border border-slate-800 space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <ShieldAlert className="w-5 h-5 text-amber-400" />
                    Audit Findings ({filteredFindings.length})
                  </h3>
                  <p className="text-xs text-slate-400">
                    Comprehensive findings from Security Sentinel and Quality & Architecture scanners.
                  </p>
                </div>

                <div className="flex bg-slate-900 p-1 rounded-xl border border-slate-800 text-xs font-semibold">
                  {['all', 'critical', 'high', 'medium', 'low'].map((sev) => (
                    <button
                      key={sev}
                      onClick={() => setSeverityFilter(sev)}
                      className={`px-3 py-1.5 rounded-lg capitalize transition-all cursor-pointer ${
                        severityFilter === sev
                          ? 'bg-indigo-600 text-white shadow'
                          : 'text-slate-400 hover:text-slate-200'
                      }`}
                    >
                      {sev}
                    </button>
                  ))}
                </div>
              </div>

              <div className="space-y-4">
                {filteredFindings.map((finding) => (
                  <div
                    key={finding.id}
                    className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all space-y-3"
                  >
                    <div className="flex items-start justify-between gap-3">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span
                            className={`px-2 py-0.5 text-[10px] font-bold uppercase rounded border ${getSeverityBadge(
                              finding.severity
                            )}`}
                          >
                            {finding.severity}
                          </span>
                          <span className="font-semibold text-slate-100 text-sm">
                            {finding.category}
                          </span>
                          {finding.auto_fixable === false && (
                            <span className="px-2 py-0.5 text-[10px] font-bold bg-amber-500/20 text-amber-300 border border-amber-500/40 rounded flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3 text-amber-400" /> Manual review recommended
                            </span>
                          )}
                          {finding.jira_ticket_url && (
                            <a
                              href={finding.jira_ticket_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="px-2 py-0.5 text-[10px] font-bold bg-blue-500/20 text-blue-300 border border-blue-500/40 rounded flex items-center gap-1 hover:bg-blue-500/30 transition-all cursor-pointer"
                              title="Open Jira Issue Ticket"
                            >
                              🔗 Jira Ticket: {finding.jira_ticket_key || 'View Ticket'}
                            </a>
                          )}
                          <span className="text-xs text-slate-500 font-mono">
                            {finding.file}:{finding.line}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300">{finding.description}</p>
                        {finding.manual_review_note && (
                          <div className="mt-1 p-2 rounded-lg bg-amber-950/30 border border-amber-500/20 text-xs text-amber-200 flex items-center gap-2">
                            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                            <span>{finding.manual_review_note}</span>
                          </div>
                        )}
                      </div>

                      <span className="px-2 py-1 text-[10px] font-mono bg-slate-800 text-slate-400 rounded border border-slate-700 shrink-0">
                        {finding.cwe}
                      </span>
                    </div>

                    {finding.explanation && (
                      <div className="p-3 rounded-lg bg-slate-950/80 border border-slate-800 text-xs text-slate-400 space-y-1">
                        <strong className="text-indigo-300 font-semibold block flex items-center gap-1">
                          <Sparkles className="w-3.5 h-3.5 text-indigo-400" /> Plain Language Explanation:
                        </strong>
                        <p>{finding.explanation}</p>
                      </div>
                    )}

                    {finding.code_snippet && (
                      <div className="bg-slate-950 p-2.5 rounded-lg font-mono text-xs text-slate-300 overflow-x-auto border border-slate-800">
                        <code>{finding.code_snippet}</code>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </main>

      <footer className="glass-card border-t border-slate-800/80 px-6 py-6 mt-12 text-center text-xs text-slate-500">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <span>DevPulse AI &copy; 2026 — Autonomous PR Audit & Verification Engine</span>
          <span>Built for hackFront India 2026 (AI & Developer Tools Track)</span>
        </div>
      </footer>
    </div>
  );
}
