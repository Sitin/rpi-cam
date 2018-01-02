import React, { Component } from 'react';

import { Panel } from 'react-bootstrap';

import { cameraApi } from './api';
import { Image } from '../shared/Image';

class LatestShots extends Component {
  componentDidMount() {
    cameraApi.subscribeToLatestImagesChange(this.handleLatestImagesChange.bind(this));
  }

  componentWillUnmount() {
    cameraApi.unsubscribeFromLatestImagesChange(this.handleLatestImagesChange);
  }

  handleLatestImagesChange() {
    this.setState({
      images: cameraApi.getLatestImages()
    });
  }

  render() {
    return <Panel>
      {this.state.images.map(img =>
        <span key={img.src}>
          <Image img={img} width={this.props.imageWidth} preview={true} openable={true} />
        </span>
      )}
    </Panel>;
  }

  state = {
    images: [],
  };
}

export { LatestShots }
