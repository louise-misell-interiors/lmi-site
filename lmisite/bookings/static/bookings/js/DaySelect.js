import React, {Component} from 'react';
import dateformat from 'dateformat';
import {fetchGQL} from "./main";
import {Loader} from "./Loader";

class Day extends Component {
    render() {
        const date = new Date(this.props.date);

        return (
            <div>
                <h2>{dateformat(date, "ddd d")}</h2>
                <div className="button-div">
                    <button onClick={() => {
                        this.props.onClick(date)
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
            error: false,
        };

        this.nextDays = this.nextDays.bind(this);
        this.prevDays = this.prevDays.bind(this);
    }

    componentWillMount() {
        this.getNewDays(new Date());
    }

    nextDays() {
        if (this.state.currentDays.length !== 0) {
            const lastDay = new Date(this.state.currentDays[this.state.currentDays.length - 1]);
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
        this.setState({
            loading: true,
        });
        fetchGQL(
            `query ($id: ID!, $day: Date!) {
            bookingType(id: $id) {
                bookingDays(start: $day, num: 5)
            }
        }`,
            {id: this.props.type.id, day: start.toISOString().split("T")[0]})
            .then(res => self.setState({
                currentDays: res.data.bookingType.bookingDays,
                loading: false,
                error: false,
            }))
            .catch(() => self.setState({
                loading: false,
                error: true,
            }));
    }


    render() {
        const self = this;
        const days = this.state.currentDays.map((day, i) =>
            <div className="col button-col" key={i}>
                <Day date={day} onClick={self.props.onSelect}/>
            </div>
        );

        let content = null;

        if (!this.state.loading) {
            if (this.state.error) {
                 content = <div className="col">
                    <h3>There was an error</h3>
                </div>
            } else {
                if (days.length !== 0) {
                    content = [
                        <div className="col slider-button" onClick={this.prevDays} key="prev">
                            <i className="fas fa-chevron-left"/>
                        </div>,
                        days,
                        <div className="col slider-button" onClick={this.nextDays} key="next">
                            <i className="fas fa-chevron-right"/>
                        </div>,
                    ];
                } else {
                    content = <div className="col">
                        <h3>No days available</h3>
                    </div>
                }
            }
        } else {
            content = <div className="col">
                <Loader/>
            </div>
        }

        return (
            <div className="back-wrapper">
                <div onClick={this.props.onBack} className="back-button"><i className="fas fa-chevron-left"/></div>
                <h1>{this.props.type.name}</h1>
                <p>{this.props.type.description}</p>
                <hr/>
                <h2>Select a day</h2>
                <div className="row">
                    {content}
                </div>
            </div>
        );
    }
}