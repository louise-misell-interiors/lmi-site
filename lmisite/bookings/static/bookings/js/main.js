'use strict';
import * as Sentry from '@sentry/browser';
import React, {Component} from 'react';
import ReactDom from 'react-dom';
import {BookingTypes} from './BookingTypes';
import {DaySelect} from './DaySelect';
import {TimeSelect} from "./TimeSelect";
import {CustomerDetails} from "./CustomerDetails";
import {Conformation} from "./Conformation";

const apiUrl = "/bookings/graphql";

class GraphQLError extends Error {
    constructor(result,...args) {
        super(...args);
        this.result = result;
    }
}

export const fetchGQL = (query, variables) =>
    fetch(apiUrl, {
        method: "POST",
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        },
        body: JSON.stringify({query: query, variables: variables}),
    })
        .then(res => {
            if (!res.ok) {
                throw new GraphQLError(res);
            }
            return res;
        })
        .then(res => res.json())
        .then(res => {
            if (typeof res.errors !== "undefined") {
                throw new GraphQLError(res);
            }
            return res
        });

class BookingApp extends Component {
    constructor(props) {
        super(props);
        this.state = {
            selectedType: null,
            selectedDay: null,
            selectedTime: null,
            complete: false,
            error: null,
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

    componentDidCatch(error, errorInfo) {
      this.setState({ error });
      Sentry.withScope(scope => {
        Object.keys(errorInfo).forEach(key => {
          scope.setExtra(key, errorInfo[key]);
        });
        Sentry.captureException(error);
      });
    }

    render() {
        if (this.state.error) {
            return (
                <div>
                <h1>Sorry, there was an error</h1>
                <hr/>
                <div className="row">
                    <div className="col">
                        <p>Please contact Louise using the email above</p>
                        <a onClick={() => Sentry.showReportDialog()}>Report feedback</a>
                    </div>
                </div>
            </div>
            );
        } else {
            let disp = null;

            if (this.state.selectedType === null) {
                disp = <BookingTypes onSelect={this.selectType}/>
            } else if (this.state.selectedDay === null) {
                disp = <DaySelect onSelect={this.selectDay} type={this.state.selectedType} onBack={() => {
                    this.setState({selectedType: null})
                }
                }/>
            } else if (this.state.selectedTime === null) {
                disp =
                    <TimeSelect onSelect={this.selectTime} type={this.state.selectedType} date={this.state.selectedDay}
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
}

Sentry.init({
 dsn: "https://b147c96f835d46178e4690cbe872a4d7@sentry.io/1370209"
});

const domContainer = document.querySelector('#wrapper');
ReactDom.render(<BookingApp/>, domContainer);