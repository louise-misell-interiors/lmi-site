"use strict";

Object.defineProperty(exports, "__esModule", {
    value: true
});
exports.Step = undefined;

var _jsx = function () { var REACT_ELEMENT_TYPE = typeof Symbol === "function" && Symbol.for && Symbol.for("react.element") || 0xeac7; return function createRawReactElement(type, props, key, children) { var defaultProps = type && type.defaultProps; var childrenLength = arguments.length - 3; if (!props && childrenLength !== 0) { props = {}; } if (props && defaultProps) { for (var propName in defaultProps) { if (props[propName] === void 0) { props[propName] = defaultProps[propName]; } } } else if (!props) { props = defaultProps || {}; } if (childrenLength === 1) { props.children = children; } else if (childrenLength > 1) { var childArray = Array(childrenLength); for (var i = 0; i < childrenLength; i++) { childArray[i] = arguments[i + 3]; } props.children = childArray; } return { $$typeof: REACT_ELEMENT_TYPE, type: type, key: key === undefined ? null : '' + key, ref: null, props: props, _owner: null }; }; }();

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

var _react = require("react");

var _react2 = _interopRequireDefault(_react);

function _interopRequireDefault(obj) { return obj && obj.__esModule ? obj : { default: obj }; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Step = exports.Step = function (_Component) {
    _inherits(Step, _Component);

    function Step(props) {
        _classCallCheck(this, Step);

        var _this = _possibleConstructorReturn(this, (Step.__proto__ || Object.getPrototypeOf(Step)).call(this, props));

        _this.state = {
            selectedAnswers: new Set()
        };

        _this.nextStep = _this.nextStep.bind(_this);
        _this.selectAnswer = _this.selectAnswer.bind(_this);
        return _this;
    }

    _createClass(Step, [{
        key: "nextStep",
        value: function nextStep() {
            if (this.state.selectedAnswers.size >= 1) {
                this.props.nextStep(Array.from(this.state.selectedAnswers));
            }
        }
    }, {
        key: "selectAnswer",
        value: function selectAnswer(id) {
            if (this.state.selectedAnswers.has(id)) {
                this.state.selectedAnswers.delete(id);
                this.setState({
                    selectedAnswers: this.state.selectedAnswers
                });
            } else {
                if (this.props.step.maxChoices && this.state.selectedAnswers.size >= this.props.step.maxChoices) {
                    if (this.props.step.maxChoices === 1) {
                        this.state.selectedAnswers.clear();
                        this.state.selectedAnswers.add(id);
                        this.setState({
                            selectedAnswers: this.state.selectedAnswers
                        });
                    }
                } else {
                    this.state.selectedAnswers.add(id);
                    this.setState({
                        selectedAnswers: this.state.selectedAnswers
                    });
                }
            }
        }
    }, {
        key: "render",
        value: function render() {
            var _this2 = this;

            return _jsx("div", {
                className: "StepPage"
            }, void 0, _jsx("h2", {}, void 0, this.props.step.questionText), this.props.step.style === "RB" ? _jsx("div", {
                className: "StepAnswers StepRadio"
            }, void 0, this.props.step.answers.edges.map(function (e) {
                return _jsx("div", {
                    className: "StepAnswer" + (_this2.state.selectedAnswers.has(e.node.id) ? " AnswerSelected" : ""),
                    onClick: function onClick() {
                        return _this2.selectAnswer(e.node.id);
                    }
                }, void 0, e.node.image ? _jsx("img", {
                    src: e.node.image,
                    alt: ""
                }) : null, e.node.text);
            })) : null, this.props.step.style === "MB" ? _jsx("div", {
                className: "StepAnswers StepMoodBoard"
            }, void 0, this.props.step.answers.edges.map(function (e) {
                return _jsx("div", {
                    className: "StepAnswer" + (_this2.state.selectedAnswers.has(e.node.id) ? " AnswerSelected" : ""),
                    onClick: function onClick() {
                        return _this2.selectAnswer(e.node.id);
                    }
                }, void 0, _jsx("img", {
                    src: e.node.image,
                    alt: e.node.text
                }));
            })) : null, this.props.step.style === "IG" ? _jsx("div", {
                className: "StepAnswers StepImageGrid"
            }, void 0, this.props.step.answers.edges.map(function (e) {
                return _jsx("div", {
                    className: "StepAnswer" + (_this2.state.selectedAnswers.has(e.node.id) ? " AnswerSelected" : ""),
                    onClick: function onClick() {
                        return _this2.selectAnswer(e.node.id);
                    }
                }, void 0, _jsx("img", {
                    src: e.node.image,
                    alt: ""
                }), e.node.text);
            })) : null, _jsx("p", {}, void 0, _jsx("a", {
                className: "button dark",
                onClick: this.nextStep
            }, void 0, "Next")));
        }
    }]);

    return Step;
}(_react.Component);

//# sourceMappingURL=Step-compiled.js.map