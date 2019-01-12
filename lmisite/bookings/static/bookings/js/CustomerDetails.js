import React, {Component} from 'react';
import dateformat from 'dateformat';
import {Loader} from "./Loader";
import {fetchGQL} from "./main";

class BookingInfo extends Component {
    render() {
        return (
            <div className="col">
                <h2>{this.props.type.name}</h2>
                <p>{this.props.type.whilstBookingMessage}</p>
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
            name: "",
            email: "",
            phone: "",
            loading: true,
            error: [],
        };

        this.scheduleEvent = this.scheduleEvent.bind(this);
        this.setQuestionAnswer = this.setQuestionAnswer.bind(this);
    }

    componentWillMount() {
        const self = this;
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
            .then(res => self.setState({
                questions: res.data.bookingType.questions,
                questionAnswers: {},
                loading: false,
            }))
    }

    scheduleEvent() {
        const self = this;
        this.setState({
            loading: true,
        });
        fetchGQL(
            `mutation ($id: ID!, $date: Date!, $time: Time!, $name: String!, $email: String!, $phone: String!,
                       $questions: [QuestionInput!]!) {
              createBooking(id: $id, date: $date, time: $time, name: $name, email: $email, phone: $phone,
                            questions: $questions) {
                ok
                error {
                  field
                  errors
                }
              }
            }`,
            {
                id: this.props.type.id,
                date: this.props.date.toISOString().split("T")[0],
                time: this.props.time.toISOString().split("T")[1].split(".")[0],
                name: this.state.name,
                email: this.state.email,
                phone: this.state.phone,
                questions: Object.keys(this.state.questionAnswers).map((key, i) => ({
                    id: key,
                    value: this.state.questionAnswers[key]
                })),
            }
        )
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

    setQuestionAnswer(question, event) {
        const questionAnswers = this.state.questionAnswers;
        questionAnswers[question] = event.target.value;

        this.setState({
            questionAnswers: questionAnswers
        })
    }

    render() {
        const date = new Date(this.props.date);
        date.setHours(this.props.time.getHours());
        date.setMinutes(this.props.time.getMinutes());
        date.setSeconds(this.props.time.getSeconds());

        let disp = null;

        if (this.state.questions == null && this.state.loading) {
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
                let errors = null;
                let error = this.state.error.filter(error => error.field === question.id);
                if (error.length !== 0) {
                    errors = error[0].errors
                        .map((error, i) => <span key={i}>{error}<br/></span>);
                }

                return <div className="row" key={question.id}>
                    <div className="col">
                        {input}
                        {errors}
                    </div>
                </div>
            });

            let nameErrors = null;
            let emailErrors = null;
            let phoneErrors = null;
            if (this.state.error !== null) {
                let nameError = this.state.error.filter(error => error.field === "name");
                if (nameError.length !== 0) {
                    nameErrors = nameError[0].errors
                        .map((error, i) => <span key={i}>{error}<br/></span>);
                }
                let emailError = this.state.error.filter(error => error.field === "email");
                if (emailError.length !== 0) {
                    emailErrors = emailError[0].errors
                        .map((error, i) => <span key={i}>{error}<br/></span>);
                }
                let phoneError = this.state.error.filter(error => error.field === "phone");
                if (phoneError.length !== 0) {
                    phoneErrors = phoneError[0].errors
                        .map((error, i) => <span key={i}>{error}<br/></span>);
                }
            }

            disp = [
                <BookingInfo type={this.props.type} time={date} key="1"/>,
                <div className="col" key="2">
                    <div className="row">
                        <div className="col">
                            <input type="text" value={this.state.name}
                                   onChange={e => this.setState({name: e.target.value})} placeholder="Name"/>
                            {nameErrors}
                        </div>
                    </div>
                    <div className="row">
                        <div className="col">
                            <input type="text" value={this.state.email}
                                   onChange={e => this.setState({email: e.target.value})} placeholder="Email"/>
                            {emailErrors}
                        </div>
                    </div>
                    <div className="row">
                        <div className="col">
                            <input type="phone" value={this.state.phone}
                                   onChange={e => this.setState({phone: e.target.value})}
                                   placeholder="Phone Number"/>
                            {phoneErrors}
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