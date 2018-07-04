'use strict';
import React, {Component} from 'react';
import ReactDom from 'react-dom';
import {BookingTypes} from './BookingTypes';
import {DaySelect} from './DaySelect';
import {TimeSelect} from "./TimeSelect";
import {CustomerDetails} from "./CustomerDetails";
import {Conformation} from "./Conformation";

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
            selectedTime: null,
            complete: false,
        };

        this.selectType = this.selectType.bind(this);
        this.selectDay = this.selectDay.bind(this);
        this.selectTime = this.selectTime.bind(this);
    }

    selectType(type) {
        this.setState({
            selectedType: type,
            selectedDay: null,
        })
    }

    selectDay(day) {
        this.setState({
            selectedDay: day,
            selectedTime: null,
        })
    }

    selectTime(time) {
        this.setState({
            selectedTime: time,
        })
    }

    render() {
        let disp = null;

        if (this.state.selectedType === null) {
            disp = <BookingTypes onSelect={this.selectType}/>
        } else if (this.state.selectedDay === null) {
            disp = <DaySelect onSelect={this.selectDay} type={this.state.selectedType} onBack={() => {
                this.setState({selectedType: null})
            }
            }/>
        } else if (this.state.selectedTime === null) {
            disp = <TimeSelect onSelect={this.selectTime} type={this.state.selectedType} date={this.state.selectedDay}
                               onBack={() => {
                                   this.setState({selectedDay: null})
                               }}/>
        } else if (!this.state.complete) {
            disp = <CustomerDetails type={this.state.selectedType} date={this.state.selectedDay}
                                    time={this.state.selectedTime}
                                    onBack={() => {
                                        this.setState({selectedTime: null})
                                    }}
                                    onComplete={() => {
                                        this.setState({complete: true})
                                    }}
            />
        } else {
            disp = <Conformation type={this.state.selectedType} date={this.state.selectedDay}
                                 time={this.state.selectedTime}/>
        }

        return disp;
    }
}

const domContainer = document.querySelector('#wrapper');
ReactDom.render(<BookingApp/>, domContainer);