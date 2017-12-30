import React, { Component } from 'react';

import { Button, Row } from 'react-bootstrap';

import { Image } from '../shared/Image';
import { LastShot } from './LastShot';
import { subscribeToPreviews, shootImage } from './api';

import nothing from './nothing.png';

class Camera extends Component {
  constructor(props) {
    super(props);

    subscribeToPreviews((err, lastFrame) => this.setState({
      lastFrame: lastFrame
    }));
  }

  render() {
    return <Row>
      <Button onClick={shootImage} block>
        <Image img={this.state.lastFrame} width={this.props.imageWidth} />
      </Button>
      <LastShot imageWidth={this.props.imageWidth} />
    </Row>;
  }

  state = {
    lastFrame: {src: nothing, ratio: 4/3},
  };
}

export { Camera }
