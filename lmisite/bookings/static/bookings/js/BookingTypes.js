import React, {Component} from 'react';
import {fetchGQL} from "../../../../common_js/graphql";
import {Loader} from "../../../../common_js/Loader";


class BookingType extends React.Component {
    render() {
        return (
            <div className="box BookingType">
                <h3>{this.props.data.name}</h3>
                <p>{this.props.data.description}</p>
                <button onClick={this.props.onClick}>Book</button>
            </div>
        );
    }
}

export class BookingTypes extends Component {
    constructor(props) {
        super(props);
        this.state = {
            types: [],
            loading: true,
            queryError: null,
            notice: null
        }
    }

    componentDidMount() {
        const self = this;
        fetchGQL(
            `{
                booking_config {
                    bookingNotice
                }
                bookingTypes {
                    id
                    name
                    description
                    whilstBookingMessage
                    afterBookingMessage
                    icon
                } 
            }`)
            .then(res => self.setState({
                types: res.data.bookingTypes,
                notice: res.data.config.bookingNotice,
                loading: false,
            }))
            .catch(err => this.setState({
                queryError: err,
            }))
    }

    render() {
        if (this.state.queryError) throw this.state.queryError;

        let types = null;
        if (!this.state.loading) {
            types = this.state.types.map(type =>
                <BookingType data={type} key={type.id} onClick={() => {
                    this.props.onSelect(type)
                }}/>
            );
        } else {
            types = <Loader/>
        }

        return (
            <React.Fragment>
                <h2 className="lead">Book an appointment with me</h2>
                {this.state.notice ? <h3 className="notice">{this.state.notice}</h3> : null}
                <div className="BookingTypes">
                    {types}
                </div>
            </React.Fragment>
        );
    }
}