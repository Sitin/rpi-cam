import React, { Component } from 'react';

import { ListGroup, ListGroupItem, Panel } from 'react-bootstrap';
import './MessagePit.css'

import { cameraApi } from './api';

class MessagePit extends Component {
  componentDidMount() {
    cameraApi.subscribeToMessages(this.handleMessagesChange.bind(this));
  }

  componentWillUnmount() {
    cameraApi.unsubscribeFromErrors(this.handleMessagesChange);
  }

  handleMessagesChange() {
    this.setState({
      messages: cameraApi.getMessages()
    });
  }

  getBsStyle(msg) {
    if (msg.levelNo > 35) {
      return 'danger';
    }
    else if (msg.levelNo > 25) {
      return 'warning';
    }
    else if (msg.levelNo > 15) {
      return 'info';
    }
    else {
      return undefined
    }
  }

  render() {
    return this.state.messages.length > 0 ? (
      <Panel header={<h3 onClick={() => this.setState({ expanded: !this.state.expanded })}>Server messages</h3>}
             collapsible expanded={this.state.expanded}>

        <ListGroup className="ErrorsPit-container">
          {
            this.state.messages.map((msg) =>
            <ListGroupItem bsStyle={this.getBsStyle(msg)} header={msg.title || '[No title]'}>{msg.text || 'no description'}</ListGroupItem>
          )
          }
        </ListGroup>

      </Panel>
    ) : null;
  }

  state = {
    messages: [],
    expanded: false,
  };
}

export { MessagePit }
