import React, {Component} from 'react';
import {Loader} from "./Loader";
import {fetchGQL} from "./main";
import {ElementsConsumer, CardElement} from "@stripe/react-stripe-js";
import Dropzone from 'react-dropzone-uploader';
import 'react-dropzone-uploader/dist/styles.css';

const CARD_OPTIONS = {
    iconStyle: 'solid',
    style: {
        base: {
            fontSize: '20px',
            fontFamily: '"Raleway", sans-serif',
            fontWeight: 'normal',
        }
    }
};

class BaseCustomerDetails extends Component {
    constructor(props) {
        super(props);

        this.state = {
            questions: [],
            questionAnswers: {},
            first_name: "",
            last_name: "",
            email: "",
            phone: "",
            newsletter: null,
            loading: true,
            error: [],
            queryError: null,
            fileObjs: [],
            initialfileObjs: [],
            files: [],
            filesCanSubmit: true,
            hasPr: false,
            price: null,
        };

        this.pr = null;
        this.stripeInFlight = false;
        this.paymentIntentId = null;

        this.scheduleEvent = this.scheduleEvent.bind(this);
        this.setQuestionAnswer = this.setQuestionAnswer.bind(this);
        this.getUploadParams = this.getUploadParams.bind(this);
        this.onUploadStatus = this.onUploadStatus.bind(this);
    }

    componentDidMount() {
        const self = this;
        if (this.props.stripe) {
            fetchGQL(
                `query ($id: ID!) {
                bookingType(id: $id) {
                    price
                    questions {
                        id
                        question
                        required
                        questionType
                    }
                }       
            }`,
                {id: this.props.type.id})
                .then(res => {
                    if (res.data.bookingType.price) {
                        this.pr = self.props.stripe.paymentRequest({
                            country: 'GB',
                            currency: 'gbp',
                            total: {
                                amount: Math.round(parseFloat(res.data.bookingType.price) * 100),
                                label: 'Louise Misell Interiors'
                            },
                            displayItems: [{
                                amount: Math.round(parseFloat(res.data.bookingType.price) * 100),
                                label: this.props.type.name
                            }],
                            requestPayerName: true,
                            requestPayerEmail: true,
                            requestPayerPhone: true,
                            requestShipping: false,
                        });
                        this.pr.canMakePayment().then(prRes => {
                            self.setState({
                                questions: res.data.bookingType.questions,
                                price: res.data.bookingType.price,
                                questionAnswers: {},
                                loading: false,
                                hasPr: !!prRes,
                            });
                        });
                    } else {

                        self.setState({
                            questions: res.data.bookingType.questions,
                            questionAnswers: {},
                            loading: false,
                            hasPr: false,
                        });
                    }
                })
                .catch(err => this.setState({
                    queryError: err,
                }))
        }
    }

    confirmPaymentIntent(prEv, paymentData) {
        let self = this;
        this.props.stripe.confirmCardPayment(
            this.paymentIntentId, paymentData, {
                handleActions: false
            }
        )
            .then(({paymentIntent, error: confirmError}) => {
                if (confirmError) {
                    if (prEv) {
                        prEv.complete('fail');
                    }
                    self.setState({
                        loading: false,
                        error: [{
                            field: "__all__",
                            errors: [confirmError.message]
                        }],
                        initialFileObjs: self.state.fileObjs
                    })
                    self.stripeInFlight = false;
                } else {
                    if (prEv) {
                        prEv.complete('success');
                    }
                    if (paymentIntent.status === "requires_action") {
                        self.props.stripe.confirmCardPayment(self.paymentIntentId)
                            .then(({error}) => {
                                if (error) {
                                    self.setState({
                                        loading: false,
                                        error: [{
                                            field: "__all__",
                                            errors: [error.message]
                                        }],
                                        initialFileObjs: self.state.fileObjs
                                    })
                                } else {
                                    self.props.onComplete();
                                }
                                self.stripeInFlight = false;
                            })
                    } else {
                        self.props.onComplete();
                    }
                }
            })
    }

    submitEvent(first_name, last_name, email, phone, prEv, paymentData) {
        let self = this;
        if (!this.paymentIntentId) {
            fetchGQL(
                `mutation ($id: ID!, $date: Date!, $time: Time!, $first_name: String!, $last_name: String!, 
                        $email: String!, $phone: String!, $questions: [QuestionInput!]!, $newsletter: Boolean!, $files: [String!]!) {
                          createBooking(id: $id, date: $date, time: $time, firstName: $first_name, lastName: $last_name,
                           email: $email, phone: $phone, questions: $questions, newsletter: $newsletter, files: $files) {
                            ok
                            paymentIntentId
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
                    first_name: first_name,
                    last_name: last_name,
                    email: email,
                    phone: phone,
                    newsletter: this.state.newsletter,
                    files: this.state.files,
                    questions: Object.keys(this.state.questionAnswers).map((key, i) => ({
                        id: key,
                        value: this.state.questionAnswers[key]
                    })),
                }
            )
                .then(res => {
                    if (!res.data.createBooking.ok) {
                        let errors = res.data.createBooking.error;
                        if (prEv) {
                            if (errors.filter(error => error.field === "email").length !== 0) {
                                prEv.complete('invalid_payer_email');
                            } else if (errors.filter(error => error.field === "phone").length !== 0) {
                                prEv.complete('invalid_payer_phone');
                            } else {
                                prEv.complete('fail');
                            }
                        }
                        self.setState({
                            loading: false,
                            error: errors,
                            initialFileObjs: self.state.fileObjs
                        })
                        self.stripeInFlight = false;
                    } else {
                        if (res.data.createBooking.paymentIntentId && paymentData) {
                            self.paymentIntentId = res.data.createBooking.paymentIntentId;
                            self.confirmPaymentIntent(prEv, paymentData);
                        } else {
                            if (prEv) {
                                prEv.complete('success');
                            }
                            self.props.onComplete();
                        }
                    }
                })
                .catch(err => {
                    self.setState({
                        queryError: err,
                    });
                    self.stripeInFlight = false;
                })
        } else {
            this.confirmPaymentIntent(prEv, paymentData);
        }
    }

    scheduleEvent() {
        if (this.state.newsletter === null) {
            this.setState({
                loading: false,
                error: [{
                    field: "__all__",
                    errors: ["Please select if you wish to be subscribed to the newsletter"]
                }],
                initialFileObjs: this.state.fileObjs
            });
            return;
        }
        if (!this.state.filesCanSubmit) {
            this.setState({
                loading: false,
                error: [{
                    field: "__all__",
                    errors: ["Files are still uploading"]
                }],
                initialFileObjs: this.state.fileObjs
            });
            return;
        }
        if (this.state.hasPr) {
            this.setState({
                loading: true,
            });
            this.pr.show();
            this.pr.on('paymentmethod', ev => {
                if (this.stripeInFlight) {
                    return;
                }
                this.stripeInFlight = true;
                console.log(ev);
                let name = ev.payerName.split(" ");
                let lastName = name.pop();
                let firstName = name.join(" ");
                if (!lastName || !firstName) {
                    ev.complete('invalid_payer_name');
                    this.stripeInFlight = false;
                    return;
                }
                this.submitEvent(firstName, lastName, ev.payerEmail, ev.payerPhone, ev, {
                    payment_method: ev.paymentMethod.id
                })
            });
            this.pr.on('cancel', () => {
                if (this.stripeInFlight) {
                    return;
                }
                this.setState({
                    loading: false,
                });
            })
        } else {
            if (!this.state.first_name || !this.state.last_name || !this.state.email || !this.state.phone) {
                this.setState({
                    loading: false,
                    error: [{
                        field: "__all__",
                        errors: ["Please complete all required fields"]
                    }],
                    initialFileObjs: this.state.fileObjs
                });
                return;
            }
            let paymentData = null;
            if (this.state.price) {
                let cardElement = this.props.elements.getElement(CardElement);
                paymentData = {
                    payment_method: {
                        card: cardElement,
                        billing_details: {
                            name: `${this.state.first_name} ${this.state.last_name}`,
                            email: this.state.email,
                            phone: this.state.phone
                        }
                    }
                }
            }
            this.submitEvent(this.state.first_name, this.state.last_name, this.state.email, this.state.phone, null, paymentData);
            this.setState({
                loading: true,
            });
        }
    }

    setQuestionAnswer(question, event) {
        const questionAnswers = this.state.questionAnswers;
        questionAnswers[question] = event.target.value;

        this.setState({
            questionAnswers: questionAnswers
        })
    }

    getUploadParams() {
        const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        return {
            url: '/bookings/upload',
            headers: {
                'X-CSRFToken': csrftoken
            }
        }
    }

    onUploadStatus(meta, status, files) {
        let statuses = files.map(f => f.meta.status);
        const canSubmit = !(statuses.includes("preparing") || statuses.includes("ready") || statuses.includes("started")
            || statuses.includes("getting_upload_params") || statuses.includes("uploading") || statuses.includes("restarted")
            || statuses.includes("headers_received"));
        const done_files = files.filter(f => f.meta.status === "done");
        const file_urls = done_files.map(f => JSON.parse(f.xhr.responseText).url);
        const file_objs = files.map(f => f.file);
        console.log(file_urls, canSubmit);
        this.setState({
            filesCanSubmit: canSubmit,
            files: file_urls,
            fileObjs: file_objs,
            initialFileObjs: []
        });
    }

    render() {
        if (this.state.queryError) throw this.state.queryError;

        const date = this.props.date.clone();
        date.hours(this.props.time.hours());
        date.minutes(this.props.time.minutes());
        date.seconds(this.props.time.seconds());
        date.milliseconds(this.props.time.milliseconds());

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
        let genericErrors = null;
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
            let genericError = this.state.error.filter(error => error.field === "__all__");
            if (genericError.length !== 0) {
                genericErrors = genericError[0].errors
                    .map((error, i) => <h3 className="error" key={i}>{error}</h3>);
            }
        }

        let disp = <div className="CustomerDetails">
            {this.state.loading ? <Loader/> : null}
            <div className="BookingInfo">
                <h2>{this.props.type.name}</h2>
                <p>{this.props.type.whilstBookingMessage}</p>
                <h3>{date.clone().local().format("dddd Do MMMM Y h:mm\xa0A")}</h3>
                {genericErrors}
                {this.state.price === null ?
                    <button onClick={this.scheduleEvent}>Schedule</button> : <React.Fragment>
                        <h3>Price: &pound;{this.state.price}</h3>
                        {
                            this.state.hasPr ? null : <div className="input-like">
                                <CardElement options={CARD_OPTIONS}/>
                            </div>
                        }
                        <button onClick={this.scheduleEvent}>Schedule and pay</button>
                        <p>
                            By continuing you authorize Louise Misell Interiors to send instructions to the
                            financial institution that issued your card to take payments from your card account in
                            accordance with the terms of your agreement with us.
                        </p>
                    </React.Fragment>
                }
            </div>
            <div className="Form">
                {this.state.hasPr ? null : <React.Fragment>
                    <div>
                        <input type="text" value={this.state.first_name} required
                               onChange={e => this.setState({first_name: e.target.value})}
                               placeholder="First name"/>
                        {firstNameErrors}
                    </div>
                    <div>
                        <input type="text" value={this.state.last_name} required
                               onChange={e => this.setState({last_name: e.target.value})} placeholder="Last name"/>
                        {lastNameErrors}
                    </div>
                    <div>
                        <input type="text" value={this.state.email} required
                               onChange={e => this.setState({email: e.target.value})} placeholder="Email"/>
                        {emailErrors}
                    </div>
                    <div>
                        <input type="phone" value={this.state.phone} required
                               onChange={e => this.setState({phone: e.target.value})}
                               placeholder="Phone Number"/>
                        {phoneErrors}
                    </div>
                </React.Fragment>}
                {questions}
                <div>
                    <div className="input-like">
                        <p>Please upload a picture or two of your project (optional)</p>
                        <Dropzone
                            getUploadParams={this.getUploadParams}
                            onChangeStatus={this.onUploadStatus}
                            initialFiles={this.state.initialfileObjs}
                            inputContent="Drag and drop files or click to browse"
                            accept="image/*"
                            submitButtonDisabled={true}
                        />
                    </div>
                </div>
                <div>
                    <div className="input-like">
                        <p>Would you like to receive my email newsletter?</p>
                        <div>
                            <input type="radio" name="newsletter" value="yes"
                                   checked={this.state.newsletter === true}
                                   required onChange={e => this.setState({newsletter: e.target.value === "yes"})}/>
                            <label>Yes</label>
                        </div>
                        <div>
                            <input type="radio" name="newsletter" value="no"
                                   checked={this.state.newsletter === false}
                                   required onChange={e => this.setState({newsletter: e.target.value === "yes"})}/>
                            <label>No</label>
                        </div>
                    </div>
                </div>
            </div>
        </div>;

        return (
            <React.Fragment>
                <div onClick={this.props.onBack} className="back-button"><i className="fas fa-chevron-left"/></div>
                <h2 className="lead">Your details</h2>
                <hr/>
                {disp}
            </React.Fragment>
        )
    }
}

export class CustomerDetails extends React.Component {
    render() {
        return <ElementsConsumer>
            {({elements, stripe}) => <BaseCustomerDetails elements={elements} stripe={stripe} {...this.props} />}
        </ElementsConsumer>
    }
}
