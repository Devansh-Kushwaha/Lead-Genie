import React from 'react';
import './CompanyDetail.css';

// Capitalize first letter only
const capitalizeFirst = (text) => {
  if (!text) return '';
  return text.charAt(0).toUpperCase() + text.slice(1).toLowerCase();
};

const parseList = (raw) => {
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    try {
      const fixed = raw.replace(/'/g, '"');
      const parsed = JSON.parse(fixed);
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  }
};

const CompanyDetail = ({ company }) => {
  if (!company)
    return (
      <div className="company-detail-empty">
        Select a company to view details
      </div>
    );

  const painPoints = parseList(company.pain_points);
  const values = parseList(company.values);
  const services = parseList(company.services_suggestions);

  return (
    <div className="company-detail-box">
      <h2 className="company-name">{capitalizeFirst(company.name)}</h2>
      <div className="company-info-grid">
        <p><span className="label">Domain:</span> {company.domain}</p>
        <p><span className="label">Location:</span> {capitalizeFirst(company.location)}</p>
        <p><span className="label">Founded:</span> {company.found_in || "N/A"}</p>
        <p><span className="label">Description:</span> {capitalizeFirst(company.description)}</p>

        <div>
          <p className="label">Pain Points:</p>
          <ul>
            {painPoints.map((point, i) => (
              <li key={i}>{capitalizeFirst(point)}</li>
            ))}
          </ul>
        </div>

        <div>
          <p className="label">Values:</p>
          <ul>
            {values.map((value, i) => (
              <li key={i}>{capitalizeFirst(value)}</li>
            ))}
          </ul>
        </div>

        <div>
          <p className="label">Suggested Services:</p>
          <ul>
            {services.map((service, i) => (
              <li key={i}>{capitalizeFirst(service)}</li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default CompanyDetail;
