import React from 'react';
import CompanyRow from './CompanyRow';
import './CompanyCard.css';

const CompanyCard = ({ companies, onCompanyClick }) => {
  if (!companies || companies.length === 0) return null;

  const handleDownloadCSV = () => {
    const headers = ['Company', 'Domain', 'Location', 'Lead Score'];
    const rows = companies.map((company) => {
      const latestScore = company.lead_scores?.[0];
      const score = latestScore?.score ?? 'N/A';
      return [
        `"${company.name}"`,
        `"${company.domain}"`,
        `"${company.location}"`,
        `"${score}"`
      ];
    });

    const csvContent =
      'data:text/csv;charset=utf-8,' +
      [headers, ...rows].map(e => e.join(',')).join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', 'companies.csv');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="company-table-container">
      <h2 className="table-heading">Company Search Results</h2>
      <table className="company-table">
        <thead>
          <tr>
            <th>Company</th>
            <th>Domain</th>
            <th>Location</th>
            <th>Lead Score</th>
          </tr>
        </thead>
        <tbody>
          {companies.map((company) => (
            <CompanyRow
              key={company.id}
              company={company}
              onClick={onCompanyClick}
            />
          ))}
        </tbody>
      </table>

      {/* Download Button */}
      <div style={{ marginTop: '20px', textAlign: 'right' }}>
        <button onClick={handleDownloadCSV} className="download-btn">
          Download CSV
        </button>
      </div>
    </div>
  );
};

export default CompanyCard;
