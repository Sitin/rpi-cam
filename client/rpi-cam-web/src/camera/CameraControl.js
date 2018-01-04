import React, { Component } from 'react';

import { Button, Checkbox, Col, ControlLabel, Form, FormControl, FormGroup, Panel } from 'react-bootstrap';
import './CameraControl.css'

import { FPS } from './FPS';
import { cameraApi } from './api';

class CameraControl extends Component {
  constructor(props) {
    super(props);

    this.handleInputChange = this.handleInputChange.bind(this);
    this.handleSubmit = this.handleSubmit.bind(this);
  }

  componentDidMount() {
    cameraApi.subscribeToSettings(this.handleSettingsChange.bind(this));
  }

  componentWillUnmount() {
    cameraApi.unsubscribeFromSettings(this.handleSettingsChange);
  }

  handleSettingsChange() {
    this.setState({
      settings: cameraApi.getSettings()
    });
  }

  handleSubmit(event) {
    cameraApi.updateSettings(this.state.settings);
    event.preventDefault();
  }

  handleInputChange(event) {
    const target = event.target;
    const value = target.type === 'checkbox' ? Number(target.checked) : target.value;
    const name = target.name;

    this.setState(prevState => {
      let settings = prevState.settings;
      settings[name] = value;

      return {
        settings: settings
      }
    });
  }

  render() {
    return this.state.settings ? (
      <Panel header={<h3 onClick={() => this.setState({ expanded: !this.state.expanded })}>Camera settings</h3>}
             collapsible expanded={this.state.expanded}>

        <Form horizontal onSubmit={this.handleSubmit} className="CameraControl-form">
          <FormGroup controlId="frameRate">
            <Col componentClass={ControlLabel} sm={4}>
              Frame Rate (current FPS=<FPS/>)
            </Col>
            <Col sm={8}>
              <FormControl type="text" value={this.state.settings.frameRate}
                           name="frameRate" onChange={this.handleInputChange}/>
            </Col>
          </FormGroup>

          <FormGroup controlId="autoShoot">
            <Col smOffset={4} sm={8}>
              <Checkbox checked={this.state.settings.autoShoot === 1}
                        name="autoShoot" onChange={this.handleInputChange}>
                Auto Shoot <em>(off by default)</em>
              </Checkbox>
            </Col>
          </FormGroup>

          <FormGroup controlId="shootTimeout">
            <Col componentClass={ControlLabel} sm={4}>
              Shoot Timeout
            </Col>
            <Col sm={8}>
              <FormControl type="text" value={this.state.settings.shootTimeout}
                           name="shootTimeout" onChange={this.handleInputChange}/>
            </Col>
          </FormGroup>

          <FormGroup controlId="idleWhenAlone">
            <Col smOffset={4} sm={8}>
              <Checkbox checked={this.state.settings.idleWhenAlone === 1}
                        name="idleWhenAlone" onChange={this.handleInputChange}>
                Stop camera when all clients disconnected <em>(on by default)</em>
              </Checkbox>
            </Col>
          </FormGroup>

          <FormGroup controlId="submit">
            <Col smOffset={4} sm={8}>
              <Button type="submit">
                Update
              </Button>
            </Col>
          </FormGroup>
        </Form>

      </Panel>
    ) : null;
  }

  state = {
    settings: null,
    expanded: false,
  };
}

export { CameraControl }
