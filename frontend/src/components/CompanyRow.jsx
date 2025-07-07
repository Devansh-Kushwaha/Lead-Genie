import React from 'react';

const toTitleCase = (str) =>
  str
    ?.toLowerCase()
    .split(' ')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

const CompanyRow = ({ company, onClick }) => {
  const latestScore = company.lead_scores?.[0]; // most recent
  const score = latestScore?.score ?? "N/A";
  const reason = latestScore?.reason ?? "No scoring reason available.";



  return (
    <tr className='company-row' onClick={() => onClick(company)} style={{ cursor: 'pointer' }}>
      <td>{toTitleCase(company.name)}</td>
      <td>{company.domain}</td>
      <td>{company.location}</td>
      <td title={reason}>
        {score} ⭐
      </td>
    </tr>
  );
};

export default CompanyRow;
