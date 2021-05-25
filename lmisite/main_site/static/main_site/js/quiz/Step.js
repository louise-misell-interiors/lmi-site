import React, {Component} from 'react';


export class Step extends Component {
    constructor(props) {
        super(props);

        this.state = {
            selectedAnswers: new Set()
        }

        this.nextStep = this.nextStep.bind(this);
        this.selectAnswer = this.selectAnswer.bind(this);
    }

    nextStep() {
        if (this.state.selectedAnswers.size >= 1) {
            this.props.nextStep(Array.from(this.state.selectedAnswers));
        }
    }

    selectAnswer(id) {
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


    render() {
        return (
            <div className="StepPage">
                <h2>{this.props.step.questionText}</h2>

                {this.props.step.style === "RB" ? <div className="StepAnswers StepRadio">
                    {this.props.step.answers.edges.map(e => <div className={
                        "StepAnswer" + (this.state.selectedAnswers.has(e.node.id) ? " AnswerSelected" : "")
                    } onClick={() => this.selectAnswer(e.node.id)}>
                        {e.node.image ? <img src={e.node.image} alt=""/> : null}
                        {e.node.text}
                    </div>)}
                </div> : null}

                {this.props.step.style === "MB" ? <div className="StepAnswers StepMoodBoard">
                    {this.props.step.answers.edges.map(e => <div className={
                        "StepAnswer" + (this.state.selectedAnswers.has(e.node.id) ? " AnswerSelected" : "")
                    } onClick={() => this.selectAnswer(e.node.id)}>
                        <img src={e.node.image} alt={e.node.text}/>
                    </div>)}
                </div> : null}

                {this.props.step.style === "IG" ? <div className="StepAnswers StepImageGrid">
                    {this.props.step.answers.edges.map(e => <div className={
                        "StepAnswer" + (this.state.selectedAnswers.has(e.node.id) ? " AnswerSelected" : "")
                    } onClick={() => this.selectAnswer(e.node.id)}>
                        <img src={e.node.image} alt=""/>
                        {e.node.text}
                    </div>)}
                </div> : null}

                <p><a className="button dark" onClick={this.nextStep}>Next</a></p>
            </div>
        );
    }
}