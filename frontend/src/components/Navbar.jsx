import React from 'react';
const Navbar = ({ menuItems, onSelect, selected }) => {
  return (
    <div className="topbar">
      <h2>SaaSquatch Leads</h2>
      <ul className="navbar">
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

export default Navbar;
