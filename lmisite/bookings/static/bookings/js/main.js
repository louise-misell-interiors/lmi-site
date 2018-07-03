'use strict';
import React, { Component } from 'react';
import ReactDom from 'react-dom';
import {BookingTypes} from './BookingTypes';
import {DaySelect} from './DaySelect';

const apiUrl = "/bookings/graphql";

export const fetchGQL = (query, variables) =>
    fetch(apiUrl, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({query: query, variables: variables}),
    });

class BookingApp extends Component {
  constructor(props) {
      super(props);
      this.state = {
          selectedType: null,
          selectedDay: null,
      };

      this.selectType = this.selectType.bind(this);
      this.selectDay = this.selectDay.bind(this);
  }

  selectType(type) {
      this.setState({
          selectedType: type,
          selectDay: null,
      })
  }

  selectDay(day) {
      this.setState({
          selectedDay: day,
      })
  }

  render() {
    let disp = null;

    if (this.state.selectedType === null) {
        disp = <BookingTypes onSelect={this.selectType}/>
    } else if (this.state.selectedDay === null) {
        disp = <DaySelect onSelect={this.selectDay} type={this.state.selectedType} onBack={() => {this.setState({selectedType: null})}
        }/>
    }

    return disp;
  }
}

const domContainer = document.querySelector('#wrapper');
ReactDom.render(<BookingApp/>, domContainer);