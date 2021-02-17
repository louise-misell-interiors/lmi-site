'use strict';
import 'whatwg-fetch';
import * as Sentry from '@sentry/browser';
import React, {Component} from 'react';
import ReactDom from 'react-dom';
import {Elements} from '@stripe/react-stripe-js';
import {loadStripe} from '@stripe/stripe-js';
import {BookingTypes} from './BookingTypes';
import {DaySelect} from './DaySelect';
import {TimeSelect} from "./TimeSelect";
import {CustomerDetails} from "./CustomerDetails";
import {Conformation} from "./Conformation";

const apiUrl = "/bookings/graphql";
const stripePromise = loadStripe(
    process.env.NODE_ENV === 'production' ?
        'pk_live_51IJ0ExINXWHtO11z4UC4ySDoqsL5Mo79lnJOw5C4RvDwEsEXw5PZu0aYFpLp1TsnUvVdUGP8QC5pdrsdGbucW5xc00WT7USUxF' :
        'pk_test_51IJ0ExINXWHtO11zeUzKO2Oq4XJOJcCznP3ph99mT43Rhp1TrZC6tmjBQzS61PmQCWPWbHXUTCKm8BtEhpvkW9lr008uuQmLUo',
    {
        apiVersion: "2020-08-27"
    }
)


class GraphQLError extends Error {
    constructor(result, ...args) {
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

    componentDidMount() {
        if (this.props.type) {
            const self = this;
            fetchGQL(
                `query ($id: ID!) {
                bookingType(id: $id) {
                    id
                    name
                    description
                    whilstBookingMessage
                    afterBookingMessage
                    icon
                } 
            }`,
                {id: this.props.type})
                .then(res => self.setState({
                    selectedType: res.data.bookingType,
                }))
                .catch(err => this.setState({
                    error: err,
                }))
        }
    }

    componentDidCatch(error, errorInfo) {
        this.setState({error});
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
                <React.Fragment>
                    <h2>Sorry, there was an error</h2>
                    <div className="box">
                        <p>Please contact Louise using the email below</p>
                        <a onClick={() => Sentry.showReportDialog()}>Report feedback</a>
                    </div>
                </React.Fragment>
            );
        } else {
            let disp = null;

            if (this.state.selectedType === null) {
                disp = <BookingTypes onSelect={this.selectType}/>
            } else if (this.state.selectedDay === null) {
                disp = <DaySelect onSelect={this.selectDay} type={this.state.selectedType} onBack={() => {
                    this.setState({selectedType: null})
                }} noBack={!!this.props.type}/>
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

function BaseApp() {
    let bookingId = null;
    if (window.bookingConf) {
        bookingId = window.bookingConf.id
    }

    return (
        <Elements stripe={stripePromise} options={{
            fonts: [{
                cssSrc: 'https://fonts.googleapis.com/css?family=Raleway'
            }]
        }}>
            <BookingApp type={bookingId}/>
        </Elements>
    );
}

Sentry.init({
    dsn: "https://b147c96f835d46178e4690cbe872a4d7@sentry.io/1370209"
});

const domContainer = document.querySelector('#booking-wrapper');

ReactDom.render(<BaseApp />, domContainer);
