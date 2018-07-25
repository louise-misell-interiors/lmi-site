import React, {Component} from 'react';

class BookingInfo extends Component {
    render() {
        return (
            <div className="col">
                <h2>{this.props.type.name}</h2>
                <p>{this.props.type.afterBookingMessage}</p>
                <h3>{dateformat(this.props.time, "ddd dd mmmm yyyy hh:MM TT")}</h3>
            </div>
        )
    }
}

export class Conformation extends Component {
    render() {
        const date = new Date(this.props.date);
        date.setHours(this.props.time.getHours());
        date.setMinutes(this.props.time.getMinutes());
        date.setSeconds(this.props.time.getSeconds());

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