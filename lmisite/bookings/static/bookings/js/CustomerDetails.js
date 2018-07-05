import React, {Component} from 'react';
import dateformat from 'dateformat';
import {Loader} from "./Loader";
import {fetchGQL} from "./main";

export class BookingInfo extends Component {
    render() {
        return (
            <div className="col">
                <h2>{this.props.type.name}</h2>
                <p>{this.props.type.description}</p>
                <h3>{dateformat(this.props.time, "ddd dd mmmm yyyy hh:MM TT")}</h3>
            </div>
        )
    }
}

export class CustomerDetails extends Component {
    constructor(props) {
        super(props);

        this.state = {
            questions: null,
            questionAnswers: {},
            loading: false,
        };

        this.scheduleEvent = this.scheduleEvent.bind(this);
        this.setQuestionAnswer = this.setQuestionAnswer.bind(this);
    }

    componentWillMount() {
        const self = this;
        this.setState({
            questions: null,
            error: null,
        });
        fetchGQL(
            `query ($id: ID!) {
                bookingType(id: $id) {
                    questions {
                        id
                        question
                        required
                        questionType
                    }
                }       
            }`,
            {id: this.props.type.id})
            .then(res => res.json())
            .then(res => self.setState({
                questions: res.data.bookingType.questions,
                questionAnswers: {},
            }));
    }

    scheduleEvent() {
        const self = this;
        this.setState({
            loading: true,
        });
        fetchGQL(
            `mutation ($id: ID!, $date: Date!, $time: Time!, $name: String!, $email: String!, $phone: String!) {
              createBooking(id: $id, date: $date, time: $time, name: $name, email: $email, phone: $phone, questions: []) {
                ok
                error
              }
            }`,
            {
                id: this.props.type.id,
                date: this.props.date.toISOString().split("T")[0],
                time: this.props.time.toISOString().split("T")[1].split(".")[0],
                name: this.refs.name.value,
                email: this.refs.email.value,
                phone: this.refs.phone.value,
            }
        )
            .then(res => res.json())
            .then(res => {
                this.setState({
                    loading: false,
                });
                if (!res.data.createBooking.ok) {
                    self.setState({
                        error: res.data.createBooking.error
                    })
                } else {
                    self.props.onComplete();
                }
            })
    }

    setQuestionAnswer(question, value) {
        this.setState({
            questionAnswers: {
                question: value
            }
        })
    }

    render() {
        const date = new Date(this.props.date);
        date.setHours(this.props.time.getHours());
        date.setMinutes(this.props.time.getMinutes());
        date.setSeconds(this.props.time.getSeconds());

        let disp = null;

        if (this.state.questions == null || this.state.loading) {
            disp = <div className="col">
                <Loader/>
            </div>
        } else {
            const questions = this.state.questions.map(question => {
                let input = null;
                if (question.questionType === "T") {
                    input = <input type="text" placeholder={question.question} required={question.required}
                                   onChange={val => this.setQuestionAnswer(question.id, val)}
                                   value={this.state.questionAnswers[question.id]}/>
                } else if (question.questionType === "M") {
                    input = <textarea placeholder={question.question} required={question.required} rows="7"
                                      onChange={val => this.setQuestionAnswer(question.id, val)}
                                      value={this.state.questionAnswers[question.id]}/>
                }

                return <div className="row" key={question.id}>
                    <div className="col">
                        {input}
                    </div>
                </div>
            });

            let error = null;
            if (this.state.error !== null) {
                const errors = this.state.error.map(error => <li>{error}</li>);

                error = <div className="row">
                    <div className="col">
                        <h4>Errors:</h4>
                        <ul>
                            {errors}
                        </ul>
                    </div>
                </div>
            }

            disp = [
                <BookingInfo type={this.props.type} time={date} key="1"/>,
                <div className="col" key="2">
                    {error}
                    <div className="row">
                        <div className="col">
                            <input type="text" ref="name" placeholder="Name"/>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col">
                            <input type="text" ref="email" placeholder="Email"/>
                        </div>
                    </div>
                    <div className="row">
                        <div className="col">
                            <input type="phone" ref="phone" placeholder="Phone Number"/>
                        </div>
                    </div>
                    {questions}
                    <div className="row">
                        <div className="col">
                            <button onClick={this.scheduleEvent}>Schedule</button>
                        </div>
                    </div>
                </div>
            ];
        }

        return (
            <div className="back-wrapper">
                <div onClick={this.props.onBack} className="back-button"><i className="fas fa-chevron-left"/></div>
                <h1>Your details</h1>
                <hr/>
                <div className="row">
                    {disp}
                </div>
            </div>
        )
    }
}