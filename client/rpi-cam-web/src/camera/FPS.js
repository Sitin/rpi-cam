import React, { Component } from 'react';
import { cameraApi } from './api';

class FPS extends Component {
  componentDidMount() {
    cameraApi.subscribeToFPS(this.handleFPSChange.bind(this));
  }

  componentWillUnmount() {
    cameraApi.unsubscribeFromFPS(this.handleFPSChange);
  }

  handleFPSChange() {
    this.setState({
      fps: cameraApi.getFPS().toFixed(1)
    });
  }

  render() {
    return <span>{this.state.fps}</span>;
  }

  state = {
    fps: null,
  };
}

export { FPS }
