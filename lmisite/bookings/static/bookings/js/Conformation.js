import React, {Component} from 'react';
import dateformat from 'dateformat';

class BookingInfo extends Component {
    render() {
        return (
            <div className="col">
                <h2>{this.props.type.name}</h2>
                <p>{this.props.type.afterBookingMessage}</p>
                <h3>{this.props.time.clone().local().format("dddd Do MMMM Y h:mm A")}</h3>
            </div>
        )
    }
}

export class Conformation extends Component {
    render() {
        const date = this.props.date.clone();
        date.hours(this.props.time.hours());
        date.minutes(this.props.time.minutes());
        date.seconds(this.props.time.seconds());
        date.milliseconds(this.props.time.milliseconds());

        return (
            <div>
                <h1>Thank you</h1>
                <hr/>
                <div className="row">
                    <BookingInfo type={this.props.type} time={date}/>
                </div>
            </div>
        )
    }
}