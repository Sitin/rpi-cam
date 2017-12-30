import React, { Component } from 'react';
import { subscribeToImages } from './api';
import { Image } from '../shared/Image';

import { Panel } from 'react-bootstrap';

class LastShot extends Component {
  constructor(props) {
    super(props);

    subscribeToImages((err, lastShot) => this.setState({
      lastShot: lastShot
    }));
  }

  render() {
    return <Panel collapsible expanded={!!this.state.lastShot} onClick={() => this.state.lastShot=null}>
      <Image img={this.state.lastShot} width={this.props.imageWidth} openable={true} />
    </Panel>;
  }

  state = {
    lastShot: null,
  };
}

export { LastShot }
