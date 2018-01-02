import React, { Component } from 'react';
import { cameraApi } from './api';
import { Image } from '../shared/Image';

import { Panel } from 'react-bootstrap';

class LastShot extends Component {
  componentDidMount() {
    cameraApi.subscribeToLastImageChange(this.handleLastImageChange.bind(this));
  }

  componentWillUnmount() {
    cameraApi.unsubscribeFromLastImageChange(this.handleLastImageChange);
  }

  handleLastImageChange() {
    this.setState({
      lastShot: cameraApi.getLastImage()
    });
  }

  render() {
    return <Panel collapsible expanded={!!this.state.lastShot} onClick={() => this.setState({lastShot: null})}>
      <Image img={this.state.lastShot} width={this.props.imageWidth} openable={true} />
    </Panel>;
  }

  state = {
    lastShot: null,
  };
}

export { LastShot }
