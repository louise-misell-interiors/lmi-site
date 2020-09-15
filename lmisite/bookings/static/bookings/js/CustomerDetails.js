import React, {Component} from 'react';
import {Loader} from "./Loader";
import {fetchGQL} from "./main";
import Dropzone from 'react-dropzone-uploader';
import 'react-dropzone-uploader/dist/styles.css';

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
            newsletter: null,
            loading: true,
            error: [],
            queryError: null,
            fileObjs: [],
            initialfileObjs: [],
            files: [],
            filesCanSubmit: true,
        };

        this.scheduleEvent = this.scheduleEvent.bind(this);
        this.setQuestionAnswer = this.setQuestionAnswer.bind(this);
        this.getUploadParams = this.getUploadParams.bind(this);
        this.onUploadStatus = this.onUploadStatus.bind(this);
    }

    componentDidMount() {
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
        if (!this.state.first_name || !this.state.last_name || !this.state.email || !this.state.phone
            || this.state.newsletter === null || !this.state.filesCanSubmit) {
            return
        }
        const self = this;
        this.setState({
            loading: true,
        });
        fetchGQL(
            `mutation ($id: ID!, $date: Date!, $time: Time!, $first_name: String!, $last_name: String!, 
            $email: String!, $phone: String!, $questions: [QuestionInput!]!, $newsletter: Boolean!, $files: [String!]!) {
              createBooking(id: $id, date: $date, time: $time, firstName: $first_name, lastName: $last_name,
               email: $email, phone: $phone, questions: $questions, newsletter: $newsletter, files: $files) {
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
                newsletter: this.state.newsletter,
                files: this.state.files,
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
                        error: res.data.createBooking.error,
                        initialFileObjs: this.state.fileObjs
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
                        <input type="text" value={this.state.first_name} required
                               onChange={e => this.setState({first_name: e.target.value})} placeholder="First name"/>
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