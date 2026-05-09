export default function ResultsPanel({ results, activeRecordId, copyJson, downloadJson }) {
  if (!results) return null;

  return (
    <div className="glass-panel results-container">
      <div className="results-toolbar">
        <div className="results-header-col">
          <div className="results-header">
            <span className="results-emoji">📋</span>
            <h2 className="results-title">Patient profile</h2>
            {activeRecordId != null && (
              <span className="chip chip-muted record-chip">Saved #{activeRecordId}</span>
            )}
          </div>
          <div className="patient-grid">
            <div>
              <strong className="label-muted">Patient name</strong> {results.patient_name || 'N/A'}
            </div>
            <div>
              <strong className="label-muted">Date</strong> {results.date || 'N/A'}
            </div>
          </div>
        </div>
        <div className="export-btns">
          <button type="button" className="btn-secondary" onClick={copyJson}>
            Copy JSON
          </button>
          <button type="button" className="btn-secondary" onClick={downloadJson}>
            Download JSON
          </button>
        </div>
      </div>

      <div className="results-header">
        <span className="results-emoji">💊</span>
        <h2 className="results-title">Extracted medicines</h2>
      </div>

      {results.medications && results.medications.length > 0 ? (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Medicine name</th>
                <th>Dosage</th>
                <th>Frequency</th>
                <th>Duration</th>
              </tr>
            </thead>
            <tbody>
              {results.medications.map((item, index) => (
                <tr key={index}>
                  <td className="med-name">{item.name || 'N/A'}</td>
                  <td>{item.dosage || 'N/A'}</td>
                  <td>
                    <span className="badge">{item.frequency || 'N/A'}</span>
                  </td>
                  <td>{item.duration || 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="empty-state">No medicines could be extracted from this image.</div>
      )}
    </div>
  );
}
