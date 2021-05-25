'use strict';
import 'whatwg-fetch';
import * as Sentry from '@sentry/browser';
import React, {Component} from 'react';
import ReactDom from 'react-dom';
import {fetchGQL} from "../../../../../common_js/graphql";
import {Loader} from "../../../../../common_js/Loader";
import {Step} from "./Step";


class QuizApp extends Component {
    constructor(props) {
        super(props);
        this.state = {
            quiz: null,
            loading: true,
            result: null,
            error: null,
            has_user: false,
            sent_to_user: false,
            session_id: null,
            current_step: null,
        };

        this.startQuiz = this.startQuiz.bind(this);
        this.nextStep = this.nextStep.bind(this);
        this.saveToEmail = this.saveToEmail.bind(this);
    }

    componentDidMount() {
        if (this.props.quizId) {
            fetchGQL(`query ($id: UUID!) {
                allQuizzes(id: $id) {
                    edges {
                        node {
                            id
                            name
                            introText
                        }
                    }
                } 
            }`,
                {id: this.props.quizId})
                .then(res => {
                    this.setState({
                        quiz: res.data.allQuizzes.edges[0] ? res.data.allQuizzes.edges[0].node : null
                    });
                    this.startQuiz();
                })
                .catch(err => {
                    console.error(err);
                    this.setState({
                        error: err,
                    })
                })
        }
    }

    componentDidCatch(error, errorInfo) {
        this.setState({error});
        Sentry.withScope(scope => {
            Object.keys(errorInfo).forEach(key => {
                scope.setExtra(key, errorInfo[key]);
            });
            Sentry.captureException(error);
        });
    }

    startQuiz() {
        fetchGQL(`mutation ($input: CreateQuizSessionMutationInput!) {
                createQuizSession(input: $input) {
                    session {
                        id
                        hasUser
                        currentStep {
                            id
                            style
                            questionText
                            maxChoices
                            answers {
                                edges {
                                    node {
                                        id
                                        text
                                        image
                                    }
                                }
                            }
                        }
                    }
                } 
            }`,
            {
                input: {
                    quizId: this.state.quiz.id
                }
            })
            .then(res => this.setState({
                session_id: res.data.createQuizSession.session.id,
                has_user: res.data.createQuizSession.session.hasUser,
                current_step: res.data.createQuizSession.session.currentStep,
                loading: false
            }))
            .catch(err => {
                console.error(err);
                this.setState({
                    error: err,
                })
            })
    }

    nextStep(answers) {
        this.setState({
            loading: true
        })
        fetchGQL(`mutation ($input: ProgressQuizSessionMutationInput!) {
                progressQuizSession(input: $input) {
                    session {
                        currentStep {
                            id
                            style
                            questionText
                            maxChoices
                            answers {
                                edges {
                                    node {
                                        id
                                        text
                                        image
                                    }
                                }
                            }
                        }
                    }
                } 
            }`,
            {
                input: {
                    sessionId: this.state.session_id,
                    answerIds: answers
                }
            })
            .then(res => {
                let nextStep = res.data.progressQuizSession.session.currentStep;
                if (nextStep) {
                    this.setState({
                        current_step: nextStep,
                        loading: false
                    });
                } else {
                    fetchGQL(`query ($id: ID!) {
                            quizSession(id: $id) {
                                result {
                                    id
                                    text
                                    image
                                    link
                                    linkText
                                }
                            } 
                        }`,
                        {
                            id: this.state.session_id
                        })
                        .then(res => {
                            this.setState({
                                current_step: null,
                                result: res.data.quizSession.result,
                                loading: false
                            });
                        })
                        .catch(err => {
                            console.error(err);
                            this.setState({
                                error: err,
                            })
                        });
                }
            })
            .catch(err => {
                console.error(err);
                this.setState({
                    error: err,
                })
            });
    }

    saveToEmail(answers) {
        this.setState({
            loading: true
        });
        fetchGQL(`mutation ($input: SaveToEmailQuizSessionMutationInput!) {
                saveToEmailQuizSession(input: $input) {
                    ok
                    error
                } 
            }`,
            {
                input: {
                    sessionId: this.state.session_id,
                    userInfo: this.state.has_user ? null : {
                        name: this.refs.user_name.value,
                        email: this.refs.user_email.value,
                    }
                }
            })
            .then(res => {
                if (res.data.saveToEmailQuizSession.ok) {
                    this.setState({
                        sent_to_user: true,
                        loading: false
                    });
                } else {
                    this.setState({
                        error: "unknown error"
                    })
                }
            })
            .catch(err => {
                console.error(err);
                this.setState({
                    error: err,
                })
            });
    }

    render() {
        if (this.state.error) {
            return (
                <React.Fragment>
                    <h2>Sorry, there was an error</h2>
                    <p><a className="button dark" onClick={() => Sentry.showReportDialog()}>Report feedback</a></p>
                </React.Fragment>
            );
        } else if (this.state.loading) {
            return <Loader/>;
        } else if (this.state.current_step) {
            return <Step step={this.state.current_step} nextStep={this.nextStep}/>;
        } else if (this.state.result) {
            return (
                <div className="StartPage">
                    <h2>Here's your result!</h2>
                    <p>{this.state.result.text}</p>
                    {this.state.result.link ? <p>
                        <a className="button dark" href={this.state.result.link}>{this.state.result.linkText}</a>
                    </p> : null}
                    {this.state.sent_to_user ? <p>
                        We've sent your results to your email, they should be with you shortly.
                    </p> : (this.state.has_user ?
                            <div className="form">
                                <p>Click below to save this to your email</p>

                                <button type="button" onClick={this.saveToEmail}>
                                    Send to email
                                </button>
                            </div> :
                            <div className="form">
                                <p>Enter your details below to save this to your email</p>

                                <form>
                                    <div>
                                        <label htmlFor="user_name">Your name:</label>
                                        <input type="text" id="user_name" required={true} ref="user_name"/>
                                    </div>
                                    <div>
                                        <label htmlFor="user_email">Your email:</label>
                                        <input type="email" id="user_email" required={true} ref="user_email"/>
                                    </div>

                                    <button type="button" onClick={this.saveToEmail}>
                                        Send to email
                                    </button>
                                </form>
                            </div>
                    )}
                </div>
            );
        } else if (!this.state.result && this.state.session_id) {
            return (
                <div className="StartPage">
                    <h2>Oh no!</h2>
                    <p>Looks like we can't find a result to match your answers.</p>
                    <p><a className="button dark" onClick={this.startQuiz}>Try again?</a></p>
                </div>
            );
        } else {
            return null;
        }
    }
}

function QuizzBaseApp() {
    let quizId = null;
    if (window.quizConf) {
        quizId = window.quizConf.id
    }

    return (
        <QuizApp quizId={quizId}/>
    );
}

Sentry.init({
    dsn: "https://b147c96f835d46178e4690cbe872a4d7@sentry.io/1370209"
});

const domContainer = document.querySelector('#quiz-wrapper');

ReactDom.render(<QuizzBaseApp/>, domContainer);
