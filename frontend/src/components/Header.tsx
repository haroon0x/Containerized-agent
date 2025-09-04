
import { Link } from 'react-router-dom';

const Header = () => (
  <header className="py-3 mb-4 border-bottom" style={{ borderColor: 'var(--border)' }}>
    <div className="container d-flex flex-wrap justify-content-center">
      <Link to="/" className="d-flex align-items-center mb-3 mb-lg-0 me-lg-auto text-decoration-none">
        <span className="font-monospace fs-4" style={{ color: 'var(--primary)' }}>AJO</span>
        <span className="ms-2 fs-5" style={{ color: 'var(--foreground)' }}>Agent Job Orchestrator</span>
      </Link>
      <ul className="nav nav-pills">
        <li className="nav-item"><Link to="/" className="nav-link" style={{ color: 'var(--foreground-muted)' }}>Home</Link></li>
        <li className="nav-item"><Link to="/stats" className="nav-link" style={{ color: 'var(--foreground-muted)' }}>System Stats</Link></li>
      </ul>
    </div>
  </header>
);

export default Header;
