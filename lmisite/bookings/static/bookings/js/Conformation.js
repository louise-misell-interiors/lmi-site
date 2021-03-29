import React, {Component} from 'react';

class BookingInfo extends Component {
    render() {
        return (
            <div className="BookingInfo">
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
            <React.Fragment>
                <h1>Thank you for your booking</h1>
                <hr/>
                <BookingInfo type={this.props.type} time={date}/>
            </React.Fragment>
        )
    }
}