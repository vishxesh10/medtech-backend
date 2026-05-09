import { getAccessToken, getSavedAccessToken } from '../api';

export default function SettingsPanel({
  settingsPanelRef,
  userMe,
  authEmail,
  authPassword,
  baseInput,
  authBusy,
  verifyLoading,
  settingsSaved,
  onChangeAuthEmail,
  onChangeAuthPassword,
  onChangeBaseInput,
  onRegister,
  onLogin,
  onLogout,
  onSaveSettings,
  onVerifyAuth,
}) {
  return (
    <div ref={settingsPanelRef} className="glass-panel settings-panel">
      <h3 className="settings-title">Account</h3>
      <p className="settings-hint">
        The API uses JWT login. Register once, then use the same email/password to sign in. Server must
        have run <code>alembic upgrade head</code> and set <code>JWT_SECRET_KEY</code> in{' '}
        <code>.env</code> for production.
      </p>
      {userMe && (
        <p className="settings-note">
          Signed in as <strong>{userMe.email}</strong>
        </p>
      )}
      {getAccessToken() && !getSavedAccessToken() && (
        <p className="settings-note">Using JWT from <code>VITE_API_ACCESS_TOKEN</code> (env).</p>
      )}
      <label className="field-label">
        Email
        <input
          className="field-input"
          type="email"
          value={authEmail}
          onChange={(e) => onChangeAuthEmail(e.target.value)}
          placeholder="you@example.com"
          autoComplete="email"
        />
      </label>
      <label className="field-label">
        Password
        <input
          className="field-input"
          type="password"
          value={authPassword}
          onChange={(e) => onChangeAuthPassword(e.target.value)}
          placeholder="Min. 8 characters"
          autoComplete="current-password"
        />
      </label>
      <div className="settings-actions">
        <button type="button" className="btn-primary" onClick={onRegister} disabled={authBusy}>
          Register
        </button>
        <button type="button" className="btn-secondary" onClick={onLogin} disabled={authBusy}>
          {authBusy ? '…' : 'Log in'}
        </button>
        {userMe && (
          <button type="button" className="btn-secondary" onClick={onLogout}>
            Log out
          </button>
        )}
      </div>

      <h3 className="settings-title settings-title-spaced">Connection</h3>
      <p className="settings-hint">
        Base URL for the API (e.g. <code>http://127.0.0.1:8001</code> or <code>/api</code> with Vite
        proxy).
      </p>
      <label className="field-label">
        API base URL
        <input
          className="field-input"
          value={baseInput}
          onChange={(e) => onChangeBaseInput(e.target.value)}
          placeholder="http://127.0.0.1:8001"
          autoComplete="off"
        />
      </label>
      <div className="settings-actions">
        <button type="button" className="btn-primary" onClick={onSaveSettings}>
          Save URL
        </button>
        <button
          type="button"
          className="btn-secondary"
          onClick={onVerifyAuth}
          disabled={verifyLoading || !getAccessToken()}
        >
          {verifyLoading ? 'Checking…' : 'Test JWT'}
        </button>
        {settingsSaved && <span className="saved-toast">Saved</span>}
      </div>
    </div>
  );
}
