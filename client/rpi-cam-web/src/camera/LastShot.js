import React, { Component } from 'react';
import { subscribeToImages } from './api';
import { Image } from '../shared/Image';

class LastShot extends Component {
  constructor(props) {
    super(props);

    subscribeToImages((err, lastShot) => this.setState({
      lastShot: lastShot
    }));
  }

  render() {
    return <div>
      <Image img={this.state.lastShot} width={this.props.imageWidth} openable={true} />
    </div>;
  }

  state = {
    lastShot: null,
  };
}

export { LastShot }
