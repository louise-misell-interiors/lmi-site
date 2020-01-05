import React, {Component} from 'react';
import {fetchGQL} from "./main";
import {Loader} from "./Loader";


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
            queryError: null
        }
    }

    componentWillMount() {
        const self = this;
        fetchGQL(
            `{
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
                <h2>Book an appointment with me</h2>
                <div className="BookingTypes">
                    {types}
                </div>
            </React.Fragment>
        );
    }
}