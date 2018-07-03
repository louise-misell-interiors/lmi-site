import React, { Component } from 'react';
import {fetchGQL} from "./main";

class Day extends Component {
    render() {
        const date = new Date(this.props.date);

        return (
          <div>
              <h2>{date.toDateString()}</h2>
              <button>Select</button>
          </div>
        );
    }
}

export class DaySelect extends Component {
    constructor(props) {
        super(props);

        this.state = {
          currentDays: [],
        };

        this.nextDays = this.nextDays.bind(this);
        this.prevDays = this.prevDays.bind(this);
    }

    componentWillMount() {
        this.getNewDays(new Date());
    }

    nextDays() {
        if (this.state.currentDays.length !== 0) {
            const lastDay = new Date(this.state.currentDays[this.state.currentDays.length-1]);
            lastDay.setDate(lastDay.getDate() + 1);
            this.getNewDays(lastDay)
        }
    }

    prevDays() {
        if (this.state.currentDays.length !== 0) {
            const firstDay = new Date(this.state.currentDays[0]);
            firstDay.setDate(firstDay.getDate() - 5);
            this.getNewDays(firstDay)
        }
    }

    getNewDays(start) {
        const self = this;
        fetchGQL(
        `query ($id: ID!, $day: Date!) {
            bookingType(id: $id) {
                bookingDays(start: $day, num: 5)
            }
        }`,
        {id: this.props.type.id, day: start.toISOString().split("T")[0]})
        .then(res => res.json())
        .then(res => self.setState({
            currentDays: res.data.bookingType.bookingDays
        }));
    }


    render() {
        const days = this.state.currentDays.map((day, i) =>
            <div className="col" key={i}>
                <Day date={day}/>
            </div>
        );

        return (
            <div className="back-wrapper">
                <div onClick={this.props.onBack} className="back-button"><i className="fas fa-chevron-left"/></div>
                <h1>{this.props.type.name}</h1>
                <p>{this.props.type.description}</p>
                <hr/>
                <h2>Select a day</h2>
                <div className="row">
                    <div className="col slider-button" onClick={this.prevDays}>
                        <i className="fas fa-chevron-left"/>
                    </div>
                    {days}
                    <div className="col slider-button" onClick={this.nextDays}>
                        <i className="fas fa-chevron-right"/>
                    </div>
                </div>
            </div>
        );
    }
}