import React, { Component } from 'react';

import { Button, Row } from 'react-bootstrap';

import { Image } from '../shared/Image';
import { LastShot } from './LastShot';
import { cameraApi } from './api';

import nothing from './nothing.png';

const imageOfNothing = {src: nothing, ratio: 4/3};

class Camera extends Component {
  constructor(props) {
    super(props);

    cameraApi.subscribeToPreview(this.handlePreviewChange.bind(this));
  }

  handlePreviewChange() {
    let preview = cameraApi.getPreview() || { lastFrame: imageOfNothing };

    this.setState({
      lastFrame: preview,
    });
  }

  componentDidMount() {
    cameraApi.subscribeToPreview(this.handlePreviewChange.bind(this));
  }

  componentWillUnmount() {
    cameraApi.unsubscribeFromPreview(this.handlePreviewChange);
  }

  render() {
    return <Row className="Camera">
      <Button onClick={cameraApi.shootImage} block>
        <Image img={this.state.lastFrame} width={this.props.imageWidth} />
      </Button>
      <LastShot imageWidth={this.props.imageWidth} />
    </Row>;
  }

  state = {
    lastFrame: imageOfNothing,
  };
}

export { Camera }
