import React, {Component} from 'react';
import dateformat from 'dateformat';
import {fetchGQL} from "./main";
import {Loader} from "./Loader";

class Time extends Component {
    render() {
        return (
            <div className="time">
                <button onClick={this.props.onClick}>{dateformat(this.props.time, "hh:MM TT")}</button>
            </div>
        );
    }
}

export class TimeSelect extends Component {
    constructor(props) {
        super(props);

        this.state = {
            currentTimes: [],
            loading: true,
        };
    }

    componentWillMount() {
        this.getNewTimes(this.props.date);
    }

    getNewTimes(start) {
        const self = this;
        this.setState({
            loading: true,
        });
        fetchGQL(
            `query ($id: ID!, $day: Date!) {
                bookingType(id: $id) {
                    bookingTimes(date: $day)
                }
            }`,
            {id: this.props.type.id, day: start.toISOString().split("T")[0]})
            .then(res => res.json())
            .then(res => self.setState({
                currentTimes: res.data.bookingType.bookingTimes,
                loading: false,
            }));
    }


    render() {
        const times = this.state.currentTimes.map((time, i) => {
            const parsedTime = new Date('1970-01-01T' + time + 'Z');
            return <Time time={parsedTime} key={i} onClick={() => {
                this.props.onSelect(parsedTime)
            }}/>
        });

        let content = null;

        if (!this.state.loading) {
            content = <div className="times">
                {times}
            </div>
        } else {
            content = <div className="row">
                <div className="col">
                    <Loader/>
                </div>
            </div>
        }

        const date = new Date(this.props.date);

        return (
            <div className="back-wrapper">
                <div onClick={this.props.onBack} className="back-button"><i className="fas fa-chevron-left"/></div>
                <h1>{date.toDateString()}</h1>
                <p>{this.props.type.name}</p>
                <hr/>
                <h2>Select a time</h2>
                {content}
            </div>
        );
    }
}