import React from 'react';

const Sidebar = ({ menuItems, onSelect, selected }) => {
  return (
    <div className="sidebar">
      <h2>SaaSquatch Leads</h2>
      <ul>
        {menuItems.map((item, index) => (
          <li
            key={index}
            className={selected === item ? 'active' : ''}
            onClick={() => onSelect(item)}
          >
            {item}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Sidebar;