import React, {Component} from 'react';

export class Loader extends Component {
    render() {
        return (
            <div className="loader">
                <svg xmlnsXlink="http://www.w3.org/1999/xlink" width={40} height={40} viewBox="0 0 50 50" {...this.props}>
                    <path
                        d="M43.935 25.145c0-10.318-8.364-18.683-18.683-18.683-10.318 0-18.683 8.365-18.683 18.683h4.068c0-8.071 6.543-14.615 14.615-14.615s14.615 6.543 14.615 14.615h4.068z">
                        <animateTransform attributeType="xml" attributeName="transform" type="rotate" from="0 25 25"
                                          to="360 25 25" dur="0.6s" repeatCount="indefinite" />
                    </path>
                </svg>
            </div>
        );
    }
}