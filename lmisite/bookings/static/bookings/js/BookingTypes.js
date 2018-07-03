import React, {Component} from 'react';
import {fetchGQL} from "./main";
import {Loader} from "./Loader";


class BookingType extends React.Component {
    render() {
        return (
            <div>
                <h2>{this.props.data.name}</h2>
                <p>{this.props.data.description}</p>
                <button onClick={this.props.onClick}>Book</button>
            </div>
        );
    }
}

export class BookingTypes extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            types: [],
            loading: true,
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
                } 
            }`)
            .then(res => res.json())
            .then(res => self.setState({
                types: res.data.bookingTypes,
                loading: false
            }));
    }

    render() {
        let types = null;
        if (!this.state.loading) {
            types = this.state.types.map(type =>
                <div className="col" key={type.id}>
                    <BookingType data={type} onClick={() => {
                        this.props.onSelect(type)
                    }}/>
                </div>
            );
        } else {
            types = <div className="col">
                <Loader />
            </div>
        }

        return (
            <div>
                <h1>Make a booking</h1>
                <hr/>
                <div className="row">
                    {types}
                </div>
            </div>
        );
    }
}