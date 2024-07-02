import React from "react";
import "./cards.css";

class Cards extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            cardData: [
                { title: "Open Price", value: props.open },
                { title: "Close Price", value: props.close },
                { title: "Low Price", value: props.low },
                { title: "High Price", value: props.high },
                { title: "News Sentiment", value: props.sentiment }
            ],
        };
    }

    componentDidUpdate(prevProps) {

        if (this.props.open !== prevProps.open ||
            this.props.close !== prevProps.close ||
            this.props.low !== prevProps.low ||
            this.props.high !== prevProps.high ||
            this.props.sentiment !== prevProps.sentiment) {
            this.setState({
                cardData: [
                    { title: "Open Price", value: this.props.open },
                    { title: "Close Price", value: this.props.close },
                    { title: "Low Price", value: this.props.low },
                    { title: "High Price", value: this.props.high },
                    { title: "News Sentiment", value: this.props.sentiment }
                ]
            });
        }

        //console.log(this.props)
    }

    render() {
        const formattedCardData = this.state.cardData.map((card) => ({
            ...card,
            value: card.title === "News Sentiment" ? card.value : parseFloat(card.value).toFixed(2) // Format value to 2 decimal places
        }));

        return (
            <div className="container mt-1">
                <div className="row justify-content-between">
                    {formattedCardData.map((card, index) => (
                        <div key={index} className="col-md-2">
                            <div className="card text-center custom-card">
                                <div className="card-body">
                                    <h5 className="card-title">{card.title}</h5>
                                    <p className="card-text display-1"><b>{card.title === "News Sentiment" ? card.value : `$${card.value}`}</b></p>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    }
}

export default Cards;
