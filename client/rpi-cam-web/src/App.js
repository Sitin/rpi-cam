import React, { Component } from 'react';

import { PageHeader } from 'react-bootstrap';
import './App.css';

import { Camera } from './camera/Camera';
import { LatestShots } from './camera/LatestShots';
import { CameraControl } from './camera/CameraControl';

class App extends Component {
  render() {
    return (
      <div className="App">
        <PageHeader className="App-header">RPI Camera</PageHeader>
        <Camera imageWidth={320} />
        <LatestShots imageWidth={160} />
        <CameraControl />
        <footer className="App-footer">
          <p>Created by <a href="https://github.com/Sitin">Mikhail Zyatin</a>.</p>
          <p><a href="https://github.com/Sitin/rpi-cam">Source code</a></p>
        </footer>
      </div>
    );
  }
}

export default App;
