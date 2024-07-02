import React from "react";
import { useNavigate } from "react-router-dom";
import "./navbar.css";

const Navbar = () => {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear userData from localStorage
    localStorage.removeItem('userData');
    localStorage.removeItem('selectedStock');
    localStorage.removeItem('startDate');
    localStorage.removeItem('endDate');
    
    // Navigate to home page
    navigate('/');
  };

  // Fetch userData from localStorage
  const userData = JSON.parse(localStorage.getItem('userData')) || {};

  return (
    <div>
      <nav className="navbar navbar-expand-lg navbar-dark p-1 mynav" style={{ backgroundColor: "black" }}>
        <div className="container-fluid">
          <div className="d-flex justify-content-between align-items-center w-100 px-3">
            <h2 className="navbar-brand mb-0">ORLANDO</h2>
            
            <div className="d-flex align-items-center">
              <div className="me-3">
                <img src={userData.imageUrl} alt="User" className="rounded-circle" style={{ width: "40px", height: "40px" }} />
              </div>
              <div className="me-3">
                <span style={{ color: "white" }}>{userData.name}</span>
              </div>
              <button className="btn btn-danger" onClick={handleLogout}>Logout</button>
            </div>
          </div>
        </div>
      </nav>
    </div>
  );
};

export default Navbar;
