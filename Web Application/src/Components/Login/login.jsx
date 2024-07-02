import React, { Component } from 'react';
import { GoogleOAuthProvider, GoogleLogin } from '@react-oauth/google';
import { Navigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';

const CLIENT_ID = '407240196859-30rjkune4eqd19mgv8rnok2eqh16ug16.apps.googleusercontent.com'; // Replace with your actual client ID

class LoginPage extends Component {
  constructor(props) {
    super(props);

    this.state = {
      isLoggedIn: false,
      userData: {},
    };
  }

  onSuccess = (response) => {
    const credentialDecoded = jwtDecode(response.credential);

    // Save userData in localStorage
    localStorage.setItem('userData', JSON.stringify({
      name: credentialDecoded.name,
      imageUrl: credentialDecoded.picture,
    }));

    this.setState({
      isLoggedIn: true,
      userData: {
        name: credentialDecoded.name,
        imageUrl: credentialDecoded.picture,
      },
    });
  };

  onFailure = (response) => {
    console.log('Login failed:', response);
    this.setState({
      isLoggedIn: false,
      userData: {},
    });
  };

  render() {
    const { isLoggedIn } = this.state;

    if (isLoggedIn) {
      return <Navigate to="/dashboard" />;
    }

    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: 'black' }}>
        <div style={{ backgroundColor: 'black', padding: '2rem', borderRadius: '8px', border: '1px solid white', textAlign: 'center' }}>
          <h2 style={{ color: 'white' }}>Sign in to ORLANDO</h2>
          <br />
          <div style={{ display: 'flex', justifyContent: 'center' }}>
            <GoogleOAuthProvider clientId={CLIENT_ID}>
              <GoogleLogin
                onSuccess={this.onSuccess}
                onFailure={this.onFailure}
                cookiePolicy={'single_host_origin'}
                responseType='code,token'
                accessType='offline'
                render={renderProps => (
                  <button onClick={renderProps.onClick} disabled={renderProps.disabled} className="btn btn-primary">
                    Sign in with Google
                  </button>
                )}
              />
            </GoogleOAuthProvider>
          </div>
        </div>
      </div>
    );
  }
}

export default LoginPage;
