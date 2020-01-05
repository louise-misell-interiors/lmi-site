import React, {Component} from 'react';
import {Loader} from "./Loader";
import {fetchGQL} from "./main";

class BookingInfo extends Component {
    render() {
        return (
            <div className="BookingInfo">
                <h2>{this.props.type.name}</h2>
                <p>{this.props.type.whilstBookingMessage}</p>
                <h3>{this.props.time.clone().local().format("dddd Do MMMM Y h:mm\xa0A")}</h3>
                <button onClick={this.props.onSchedule}>Schedule</button>
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
            first_name: "",
            last_name: "",
            email: "",
            phone: "",
            loading: true,
            error: [],
            queryError: null
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
            .catch(err => this.setState({
                queryError: err,
            }))
    }

    scheduleEvent() {
        const self = this;
        this.setState({
            loading: true,
        });
        fetchGQL(
            `mutation ($id: ID!, $date: Date!, $time: Time!, $first_name: String!, $last_name: String!, 
            $email: String!, $phone: String!, $questions: [QuestionInput!]!) {
              createBooking(id: $id, date: $date, time: $time, firstName: $first_name, lastName: $last_name,
               email: $email, phone: $phone, questions: $questions) {
                ok
                error {
                  field
                  errors
                }
              }
            }`,
            {
                id: this.props.type.id,
                date: this.props.date.format("Y-MM-DD"),
                time: this.props.time.format("HH:mm:ss"),
                first_name: this.state.first_name,
                last_name: this.state.last_name,
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
            .catch(err => this.setState({
                queryError: err,
            }))
    }

    setQuestionAnswer(question, event) {
        const questionAnswers = this.state.questionAnswers;
        questionAnswers[question] = event.target.value;

        this.setState({
            questionAnswers: questionAnswers
        })
    }

    render() {
        if (this.state.queryError) throw this.state.queryError;

        const date = this.props.date.clone();
        date.hours(this.props.time.hours());
        date.minutes(this.props.time.minutes());
        date.seconds(this.props.time.seconds());
        date.milliseconds(this.props.time.milliseconds());

        let disp = null;

        if (this.state.loading) {
            disp = <Loader/>
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
                        .map((error, i) => <span className="error" key={i}>{error}<br/></span>);
                }

                return <div key={question.id}>
                        {input}
                        {errors}
                </div>
            });

            let firstNameErrors = null;
            let lastNameErrors = null;
            let emailErrors = null;
            let phoneErrors = null;
            if (this.state.error !== null) {
                let firstNameError = this.state.error.filter(error => error.field === "first_name");
                if (firstNameError.length !== 0) {
                    firstNameErrors = firstNameError[0].errors
                        .map((error, i) => <span className="error" key={i}>{error}<br/></span>);
                }
                let lastNameError = this.state.error.filter(error => error.field === "last_name");
                if (lastNameError.length !== 0) {
                    lastNameErrors = lastNameError[0].errors
                        .map((error, i) => <span className="error" key={i}>{error}<br/></span>);
                }
                let emailError = this.state.error.filter(error => error.field === "email");
                if (emailError.length !== 0) {
                    emailErrors = emailError[0].errors
                        .map((error, i) => <span className="error" key={i}>{error}<br/></span>);
                }
                let phoneError = this.state.error.filter(error => error.field === "phone");
                if (phoneError.length !== 0) {
                    phoneErrors = phoneError[0].errors
                        .map((error, i) => <span className="error" key={i}>{error}<br/></span>);
                }
            }

            disp = <div className="CustomerDetails">
                <BookingInfo type={this.props.type} time={date} key="1" onSchedule={this.scheduleEvent}/>
                <div className="Form">
                    <div>
                            <input type="text" value={this.state.first_name}
                                   onChange={e => this.setState({first_name: e.target.value})} placeholder="First name"/>
                            {firstNameErrors}
                    </div>
                    <div>
                            <input type="text" value={this.state.last_name}
                                   onChange={e => this.setState({last_name: e.target.value})} placeholder="Last name"/>
                            {lastNameErrors}
                    </div>
                    <div>
                            <input type="text" value={this.state.email}
                                   onChange={e => this.setState({email: e.target.value})} placeholder="Email"/>
                            {emailErrors}
                    </div>
                    <div>
                            <input type="phone" value={this.state.phone}
                                   onChange={e => this.setState({phone: e.target.value})}
                                   placeholder="Phone Number"/>
                            {phoneErrors}
                    </div>
                    {questions}
                </div>
            </div>;
        }

        return (
            <React.Fragment>
                <div onClick={this.props.onBack} className="back-button"><i className="fas fa-chevron-left"/></div>
                <h2>Your details</h2>
                <hr/>
                {disp}
            </React.Fragment>
        )
    }
}