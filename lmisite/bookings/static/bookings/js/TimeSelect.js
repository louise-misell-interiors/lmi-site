import React, {Component} from 'react';
import moment from 'moment';
import {fetchGQL} from "./main";
import {Loader} from "./Loader";

class Time extends Component {
    render() {
        return (
            <button className="Time" onClick={this.props.onClick}>
                {this.props.time.clone().local().format("h:mm A")}
            </button>
        );
    }
}

export class TimeSelect extends Component {
    constructor(props) {
        super(props);

        this.state = {
            currentTimes: [],
            loading: true,
            queryError: null
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
            {id: this.props.type.id, day: start.format("Y-MM-DD")})
            .then(res => self.setState({
                currentTimes: res.data.bookingType.bookingTimes.map(time => moment.utc(time, "HH:mm:ss")),
                loading: false,
            }))
            .catch(err => this.setState({
                queryError: err,
            }))
    }


    render() {
        if (this.state.queryError) throw this.state.queryError;

        const times = this.state.currentTimes.map((time, i) => {
            return <Time time={time} key={i} onClick={() => {
                this.props.onSelect(time)
            }}/>
        });

        let content = null;

        if (!this.state.loading) {
            content = <div className="TimeSelect">
                {times}
            </div>
        } else {
            content = <Loader/>
        }

        return (
            <React.Fragment>
                <div onClick={this.props.onBack} className="back-button"><i className="fas fa-chevron-left"/></div>
                <h2>{this.props.date.clone().local().format("dddd Do MMMM Y")}</h2>
                <p>{this.props.type.name}</p>
                <hr/>
                <h2>Select a time</h2>
                {content}
            </React.Fragment>
        );
    }
}