export default function StatusBar({ healthOk, versionInfo, verifyOk, settingsOpen, onToggleSettings }) {
  return (
    <div className="status-bar glass-panel status-bar-inner">
      <div className="status-chips">
        <span
          className={`chip ${healthOk === true ? 'chip-ok' : healthOk === false ? 'chip-bad' : 'chip-pending'}`}
        >
          API {healthOk === true ? 'online' : healthOk === false ? 'offline' : '…'}
        </span>
        {versionInfo && (
          <span className="chip chip-muted">
            v{versionInfo.version} · {versionInfo.name}
          </span>
        )}
        {verifyOk === true && <span className="chip chip-ok">Auth OK</span>}
        {verifyOk === false && <span className="chip chip-bad">Auth failed</span>}
      </div>
      <button type="button" className="btn-ghost" onClick={onToggleSettings}>
        {settingsOpen ? 'Hide settings' : 'Settings'}
      </button>
    </div>
  );
}
