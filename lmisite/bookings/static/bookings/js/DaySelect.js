import React, {Component} from 'react';
import moment from 'moment';
import {fetchGQL} from "./main";
import {Loader} from "./Loader";

class Day extends Component {
    render() {
        return (
            <div className="Day">
                <h3>{this.props.date.clone().local().format("ddd Do MMM")}</h3>
                <div className="button-div">
                    <button onClick={() => {
                        this.props.onClick(this.props.date)
                    }}>Select
                    </button>
                </div>
            </div>
        );
    }
}

export class DaySelect extends Component {
    constructor(props) {
        super(props);

        this.state = {
            currentDays: [],
            loading: true,
            queryError: null
        };

        this.nextDays = this.nextDays.bind(this);
        this.prevDays = this.prevDays.bind(this);
    }

    componentDidMount() {
        this.getNewDays(moment.utc());
    }

    nextDays() {
        if (this.state.currentDays.length !== 0) {
            const lastDay = this.state.currentDays[this.state.currentDays.length - 1].clone();
            lastDay.add('1', 'd');
            this.getNewDays(lastDay)
        }
    }

    prevDays() {
        if (this.state.currentDays.length !== 0) {
            const firstDay = this.state.currentDays[0].clone();
            firstDay.subtract(5, 'd');
            this.getNewDays(firstDay)
        }
    }

    getNewDays(start) {
        const self = this;
        this.setState({
            loading: true,
        });
        fetchGQL(
            `query ($id: ID!, $day: Date!) {
            bookingType(id: $id) {
                bookingDays(start: $day, num: 5)
            }
        }`,
            {id: this.props.type.id, day: start.format("Y-MM-DD")})
            .then(res => self.setState({
                currentDays: res.data.bookingType.bookingDays.map(day => moment.utc(day, "Y-MM-DD")),
                loading: false,
            }))
            .catch(err => this.setState({
                queryError: err,
            }))
    }


    render() {
        if (this.state.queryError) throw this.state.queryError;

        const self = this;
        const days = this.state.currentDays.map((day, i) =>
            <Day date={day} key={i} onClick={self.props.onSelect}/>
        );

        let content = null;

        if (!this.state.loading) {
            if (days.length !== 0) {
                content = <div className="DaySelect">
                    <i className="fas fa-chevron-left" onClick={this.prevDays}/>
                    {days}
                    <i className="fas fa-chevron-right" onClick={this.nextDays}/>
                </div>;
            } else {
                content = <h3>No days are available for booking at the moment, please try again later.</h3>
            }
        } else {
            content = <Loader/>
        }

        return (
            <React.Fragment>
                {this.props.noBack ?
                    null :
                    <div onClick={this.props.onBack} className="back-button"><i className="fas fa-chevron-left"/></div>
                }
                <h2 className="lead">{this.props.type.name}</h2>
                <p>{this.props.type.description}</p>
                <hr/>
                <h2>Select a day</h2>
                {content}
            </React.Fragment>
        );
    }
}