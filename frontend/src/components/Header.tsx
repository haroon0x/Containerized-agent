
import React from 'react';
import { FiMoon, FiSun } from 'react-icons/fi';

const Header = ({ theme, toggleTheme }) => (
  <header className="py-3 mb-4">
    <div className="container d-flex justify-content-between align-items-center">
      <h1 className="h5 mb-0 fw-bold">Agent Control Deck</h1>
      <button className="btn-ghost" onClick={toggleTheme}>
        {theme === 'dark' ? <FiSun size={20} /> : <FiMoon size={20} />}
      </button>
    </div>
  </header>
);

export default Header;
