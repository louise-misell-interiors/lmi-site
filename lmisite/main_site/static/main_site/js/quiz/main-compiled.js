'use strict';

var _jsx = function () { var REACT_ELEMENT_TYPE = typeof Symbol === "function" && Symbol.for && Symbol.for("react.element") || 0xeac7; return function createRawReactElement(type, props, key, children) { var defaultProps = type && type.defaultProps; var childrenLength = arguments.length - 3; if (!props && childrenLength !== 0) { props = {}; } if (props && defaultProps) { for (var propName in defaultProps) { if (props[propName] === void 0) { props[propName] = defaultProps[propName]; } } } else if (!props) { props = defaultProps || {}; } if (childrenLength === 1) { props.children = children; } else if (childrenLength > 1) { var childArray = Array(childrenLength); for (var i = 0; i < childrenLength; i++) { childArray[i] = arguments[i + 3]; } props.children = childArray; } return { $$typeof: REACT_ELEMENT_TYPE, type: type, key: key === undefined ? null : '' + key, ref: null, props: props, _owner: null }; }; }();

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

require('whatwg-fetch');

var _browser = require('@sentry/browser');

var Sentry = _interopRequireWildcard(_browser);

var _react = require('react');

var _react2 = _interopRequireDefault(_react);

var _reactDom = require('react-dom');

var _reactDom2 = _interopRequireDefault(_reactDom);

var _graphql = require('../../../../../common_js/graphql');

var _Loader = require('../../../../../common_js/Loader');

var _Step = require('./Step');

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _interopRequireWildcard(obj) { if (obj && obj.__esModule) { return obj; } else { var newObj = {}; if (obj != null) { for (var key in obj) { if (Object.prototype.hasOwnProperty.call(obj, key)) newObj[key] = obj[key]; } } newObj.default = obj; return newObj; } }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var _ref = _jsx('h2', {}, void 0, 'Sorry, there was an error');

var _ref2 = _jsx(_Loader.Loader, {});

var QuizApp = function (_Component) {
    _inherits(QuizApp, _Component);

    function QuizApp(props) {
        _classCallCheck(this, QuizApp);

        var _this = _possibleConstructorReturn(this, (QuizApp.__proto__ || Object.getPrototypeOf(QuizApp)).call(this, props));

        _this.state = {
            quiz: null,
            loading: true,
            error: null,
            session_id: null,
            current_step: null
        };

        _this.startQuiz = _this.startQuiz.bind(_this);
        _this.nextStep = _this.nextStep.bind(_this);
        return _this;
    }

    _createClass(QuizApp, [{
        key: 'componentDidMount',
        value: function componentDidMount() {
            var _this2 = this;

            if (this.props.quizId) {
                (0, _graphql.fetchGQL)('query ($id: UUID!) {\n                allQuizzes(id: $id) {\n                    edges {\n                        node {\n                            id\n                            name\n                            introText\n                        }\n                    }\n                } \n            }', { id: this.props.quizId }).then(function (res) {
                    return _this2.setState({
                        quiz: res.data.allQuizzes.edges[0] ? res.data.allQuizzes.edges[0].node : null,
                        loading: false
                    });
                }).catch(function (err) {
                    console.error(err);
                    _this2.setState({
                        error: err
                    });
                });
            }
        }
    }, {
        key: 'componentDidCatch',
        value: function componentDidCatch(error, errorInfo) {
            this.setState({ error: error });
            Sentry.withScope(function (scope) {
                Object.keys(errorInfo).forEach(function (key) {
                    scope.setExtra(key, errorInfo[key]);
                });
                Sentry.captureException(error);
            });
        }
    }, {
        key: 'startQuiz',
        value: function startQuiz() {
            var _this3 = this;

            this.setState({
                loading: true
            });
            (0, _graphql.fetchGQL)('mutation ($input: CreateQuizSessionMutationInput!) {\n                createQuizSession(input: $input) {\n                    session {\n                        id\n                        currentStep {\n                            id\n                            style\n                            questionText\n                            maxChoices\n                            answers {\n                                edges {\n                                    node {\n                                        id\n                                        text\n                                        image\n                                    }\n                                }\n                            }\n                        }\n                    }\n                } \n            }', { input: {
                    quizId: this.state.quiz.id
                } }).then(function (res) {
                return _this3.setState({
                    session_id: res.data.createQuizSession.session.id,
                    current_step: res.data.createQuizSession.session.currentStep,
                    loading: false
                });
            }).catch(function (err) {
                console.error(err);
                _this3.setState({
                    error: err
                });
            });
        }
    }, {
        key: 'nextStep',
        value: function nextStep(answers) {
            var _this4 = this;

            console.log(answers);
            this.setState({
                loading: true
            });
            (0, _graphql.fetchGQL)('mutation ($input: ProgressQuizSessionMutationInput!) {\n                progressQuizSession(input: $input) {\n                    session {\n                        currentStep {\n                            id\n                            style\n                            questionText\n                            maxChoices\n                            answers {\n                                edges {\n                                    node {\n                                        id\n                                        text\n                                        image\n                                    }\n                                }\n                            }\n                        }\n                    }\n                } \n            }', { input: {
                    sessionId: this.state.session_id,
                    answerIds: answers
                } }).then(function (res) {
                return _this4.setState({
                    current_step: res.data.progressQuizSession.session.currentStep,
                    loading: false
                });
            }).catch(function (err) {
                console.error(err);
                _this4.setState({
                    error: err
                });
            });
        }
    }, {
        key: 'render',
        value: function render() {
            if (this.state.error) {
                return _jsx(_react2.default.Fragment, {}, void 0, _ref, _jsx('p', {}, void 0, _jsx('a', {
                    className: 'button dark',
                    onClick: function onClick() {
                        return Sentry.showReportDialog();
                    }
                }, void 0, 'Report feedback')));
            } else if (this.state.loading) {
                return _ref2;
            } else if (this.state.current_step) {
                return _jsx(_Step.Step, {
                    step: this.state.current_step,
                    nextStep: this.nextStep
                });
            } else if (this.state.quiz) {
                return _jsx('div', {
                    className: 'StartPage'
                }, void 0, _jsx('h2', {}, void 0, this.state.quiz.name), _jsx('p', {}, void 0, this.state.quiz.introText), _jsx('p', {}, void 0, _jsx('a', {
                    className: 'button dark',
                    onClick: this.startQuiz
                }, void 0, 'Take the quiz')));
            } else {
                return null;
            }
        }
    }]);

    return QuizApp;
}(_react.Component);

function QuizzBaseApp() {
    var quizId = null;
    if (window.quizConf) {
        quizId = window.quizConf.id;
    }

    return _jsx(QuizApp, {
        quizId: quizId
    });
}

Sentry.init({
    dsn: "https://b147c96f835d46178e4690cbe872a4d7@sentry.io/1370209"
});

var domContainer = document.querySelector('#quiz-wrapper');

_reactDom2.default.render(_jsx(QuizzBaseApp, {}), domContainer);

//# sourceMappingURL=main-compiled.js.map