import { useState, useRef, useEffect, useCallback } from 'react';
import {
  getApiBase,
  getAccessToken,
  getSavedAccessToken,
  saveApiSettings,
  clearAuth,
  apiFetch,
  readErrorMessage,
  fetchBackendMeta,
  fetchPrescriptionList,
  authRegister,
  authLogin,
} from './api';
import './App.css';
import StatusBar from './components/StatusBar';
import SettingsPanel from './components/SettingsPanel';
import UploadPanel from './components/UploadPanel';
import HistoryPanel from './components/HistoryPanel';
import ResultsPanel from './components/ResultsPanel';

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  const [settingsOpen, setSettingsOpen] = useState(false);
  const [baseInput, setBaseInput] = useState(() => getApiBase());
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [userMe, setUserMe] = useState(null);
  const [authBusy, setAuthBusy] = useState(false);
  const [settingsSaved, setSettingsSaved] = useState(false);
  const settingsPanelRef = useRef(null);

  const [healthOk, setHealthOk] = useState(null);
  const [versionInfo, setVersionInfo] = useState(null);
  const [verifyOk, setVerifyOk] = useState(null);
  const [verifyLoading, setVerifyLoading] = useState(false);

  const [historyList, setHistoryList] = useState([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [activeRecordId, setActiveRecordId] = useState(null);

  const applyBackendMeta = (meta) => {
    setHealthOk(meta.healthOk);
    setVersionInfo(meta.version);
  };

  useEffect(() => {
    let cancelled = false;
    fetchBackendMeta().then((meta) => {
      if (!cancelled) applyBackendMeta(meta);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const refreshUser = useCallback(async () => {
    if (!getAccessToken()) {
      return { user: null };
    }

    try {
      const r = await apiFetch('/auth/me');
      if (r.ok) {
        return { user: await r.json() };
      }
      clearAuth();
      return { user: null };
    } catch {
      clearAuth();
      return { user: null };
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    refreshUser().then(({ user }) => {
      if (!cancelled) setUserMe(user);
    });
    return () => {
      cancelled = true;
    };
  }, [refreshUser]);

  const loadHistory = async () => {
    setHistoryLoading(true);
    try {
      const list = await fetchPrescriptionList();
      setHistoryList(list);
    } finally {
      setHistoryLoading(false);
    }
  };

  useEffect(() => {
    let cancelled = false;
    fetchPrescriptionList().then((list) => {
      if (!cancelled) setHistoryList(list);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!settingsOpen || !settingsPanelRef.current) return;
    settingsPanelRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }, [settingsOpen]);

  const handleSaveSettings = () => {
    saveApiSettings({ baseUrl: baseInput });
    setSettingsSaved(true);
    setVerifyOk(null);
    fetchBackendMeta().then(applyBackendMeta);
    loadHistory();
    setTimeout(() => setSettingsSaved(false), 2000);
  };

  const handleRegister = async () => {
    setError(null);
    if (!authEmail.trim() || !authPassword) {
      setError('Email and password are required.');
      return;
    }
    if (authPassword.length < 8) {
      setError('Password must be at least 8 characters.');
      return;
    }
    setAuthBusy(true);
    try {
      const res = await authRegister(authEmail, authPassword);
      if (!res.ok) {
        setError(await readErrorMessage(res));
        return;
      }
      const loginRes = await authLogin(authEmail, authPassword);
      if (!loginRes.ok) {
        setError(await readErrorMessage(loginRes));
        return;
      }
      const { user } = await refreshUser();
      setUserMe(user);
      loadHistory();
      setVerifyOk(true);
      setAuthPassword('');
    } catch (e) {
      setError(e.message || 'Registration failed');
    } finally {
      setAuthBusy(false);
    }
  };

  const handleLogin = async () => {
    setError(null);
    if (!authEmail.trim() || !authPassword) {
      setError('Email and password are required.');
      return;
    }
    setAuthBusy(true);
    try {
      const res = await authLogin(authEmail, authPassword);
      if (!res.ok) {
        setError(await readErrorMessage(res));
        setVerifyOk(false);
        return;
      }
      const { user } = await refreshUser();
      setUserMe(user);
      loadHistory();
      setVerifyOk(true);
      setAuthPassword('');
    } catch (e) {
      setError(e.message || 'Login failed');
      setVerifyOk(false);
    } finally {
      setAuthBusy(false);
    }
  };

  const handleLogout = () => {
    clearAuth();
    setUserMe(null);
    setVerifyOk(null);
    setAuthPassword('');
    loadHistory();
  };

  const handleVerifyAuth = async () => {
    setVerifyLoading(true);
    setVerifyOk(null);
    try {
      const res = await apiFetch('/auth/verify');
      setVerifyOk(res.ok);
      if (!res.ok) setError(await readErrorMessage(res));
      else loadHistory();
    } catch (e) {
      setVerifyOk(false);
      setError(e.message || 'Verify request failed');
    } finally {
      setVerifyLoading(false);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    e.preventDefault();
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (selectedFile) => {
    if (!selectedFile.type.startsWith('image/')) {
      setError('Please upload an image file.');
      return;
    }
    setFile(selectedFile);
    setPreview(URL.createObjectURL(selectedFile));
    setError(null);
    setResults(null);
  };

  const clearUploadOnly = () => {
    if (preview) URL.revokeObjectURL(preview);
    setFile(null);
    setPreview(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleClear = () => {
    clearUploadOnly();
    setResults(null);
    setActiveRecordId(null);
  };

  const openSavedPrescription = async (id) => {
    if (!getAccessToken()) return;
    setError(null);
    try {
      const res = await apiFetch(`/prescriptions/${id}`);
      if (!res.ok) {
        setError(await readErrorMessage(res));
        return;
      }
      const data = await res.json();
      clearUploadOnly();
      setResults(data.extracted_data);
      setActiveRecordId(data.id);
    } catch (e) {
      setError(e.message || 'Failed to load prescription');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    if (!getAccessToken()) {
      setError(
        'Sign in first. Open Settings → create an account or log in to get a JWT. For local dev you can set VITE_API_ACCESS_TOKEN in frontend/.env (same token as /auth/login response).',
      );
      setSettingsOpen(true);
      return;
    }

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await apiFetch('/extract-prescription', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(await readErrorMessage(response));
      }

      const data = await response.json();
      if (!data.extracted_data) {
        throw new Error('AI returned invalid data structure.');
      }

      setResults(data.extracted_data);
      setActiveRecordId(data.saved_id ?? null);
      loadHistory();
    } catch (err) {
      setError(err.message || 'Something went wrong during analysis.');
    } finally {
      setLoading(false);
    }
  };

  const rawJson = results ? JSON.stringify(results, null, 2) : '';

  const copyJson = async () => {
    if (!rawJson) return;
    try {
      await navigator.clipboard.writeText(rawJson);
    } catch {
      setError('Could not copy to clipboard.');
    }
  };

  const downloadJson = () => {
    if (!rawJson) return;
    const blob = new Blob([rawJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'prescription-extract.json';
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="app-container">
      <StatusBar
        healthOk={healthOk}
        versionInfo={versionInfo}
        verifyOk={verifyOk}
        settingsOpen={settingsOpen}
        onToggleSettings={() => setSettingsOpen((o) => !o)}
      />

      {settingsOpen && (
        <SettingsPanel
          settingsPanelRef={settingsPanelRef}
          userMe={userMe}
          authEmail={authEmail}
          authPassword={authPassword}
          baseInput={baseInput}
          authBusy={authBusy}
          verifyLoading={verifyLoading}
          settingsSaved={settingsSaved}
          onChangeAuthEmail={setAuthEmail}
          onChangeAuthPassword={setAuthPassword}
          onChangeBaseInput={setBaseInput}
          onRegister={handleRegister}
          onLogin={handleLogin}
          onLogout={handleLogout}
          onSaveSettings={handleSaveSettings}
          onVerifyAuth={handleVerifyAuth}
        />
      )}

      <UploadPanel
        fileInputRef={fileInputRef}
        preview={preview}
        isDragActive={isDragActive}
        error={error}
        loading={loading}
        onDrag={handleDrag}
        onDrop={handleDrop}
        onChange={handleChange}
        onUpload={handleUpload}
        onClear={handleClear}
        onOpenSettings={() => setSettingsOpen(true)}
      />

      <HistoryPanel
        historyLoading={historyLoading}
        historyList={historyList}
        loadHistory={loadHistory}
        openSavedPrescription={openSavedPrescription}
        activeRecordId={activeRecordId}
      />

      <ResultsPanel
        results={results}
        activeRecordId={activeRecordId}
        copyJson={copyJson}
        downloadJson={downloadJson}
      />
    </div>
  );
}

export default App;
