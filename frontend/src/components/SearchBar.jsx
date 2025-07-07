import React, { useState } from 'react';

const SearchBar = ({ onSearch }) => {
  const [industry, setIndustry] = useState('');
  const [location, setLocation] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSearch({ industry, location });
  };

  return (
    <form className="search-bar" onSubmit={handleSubmit}>
      <div className="search-fields">
        <div className="field">
          <label>Industry</label>
          <input
            type="text"
            placeholder="Enter industry (e.g. Software, Healthcare)"
            value={industry}
            onChange={(e) => setIndustry(e.target.value)}
          />
        </div>
        <div className="field">
          <label>Location</label>
          <input
            type="text"
            placeholder="Enter location (e.g. San Francisco, CA)"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
          />
        </div>
      </div>
      <div className="search-buttons">
        <button type="submit" className="btn primary" >Find Companies</button>
        <button type="button" className="btn danger" onClick={() => { setIndustry(''); setLocation(''); }}>Cancel</button>
      </div>
    </form>
  );
};

export default SearchBar;