import React, {Component} from 'react';
import {BookingInfo} from "./CustomerDetails";

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
                    <BookingInfo type={this.props.type} time={date} timezone={this.props.timezone}/>
                </div>
            </div>
        )
    }
}