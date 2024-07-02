import React, { Component } from "react";
import Axios from "axios";
import "./userinput.css";

class UserForm extends Component {
    constructor(props) {
        super(props);

        // Calculate one year ago from today
        const today = new Date();
        const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());

        // Calculate yesterday's date
        const yesterday = new Date(today);
        yesterday.setDate(today.getDate() - 1);

        this.state = {
            stockName: this.props.stockName,
            startDate: oneYearAgo.toISOString().substr(0, 10), // Set start date to one year ago
            endDate: yesterday.toISOString().substr(0, 10) // Set end date to yesterday
        };

        // Binding event handlers
        this.handleSubmit = this.handleSubmit.bind(this);
        this.handleChange = this.handleChange.bind(this);
        this.handleChange1 = this.handleChange1.bind(this);
        this.handleChange2 = this.handleChange2.bind(this);
    }

    handleSubmit(e) {
        e.preventDefault();
        const stockName = e.target.elements.stockName.value;
        this.props.onStockNameChange(stockName);
    }

    handleChange(e) {
        const stockName = e.target.value;
        this.setState({
            stockName: stockName
        });
        this.props.onStockNameChange(stockName);
    }

    handleChange1(e) {
        let startDate = e.target.value;
        const today = new Date().toISOString().substr(0, 10);
        const oneYearAgo = new Date(new Date().setFullYear(new Date().getFullYear() - 1)).toISOString().substr(0, 10);

        // Check if selected startDate is beyond one year ago or today
        if (startDate < oneYearAgo) {
            startDate = oneYearAgo; // Set startDate to one year ago if it's beyond one year ago
        } else if (startDate > today) {
            startDate = today; // Set startDate to today if it's beyond today
        }

        this.setState({
            startDate: startDate
        });
        this.props.onStartDateChange(startDate);
    }

    handleChange2(e) {
        let endDate = e.target.value;
        const today = new Date().toISOString().substr(0, 10);
        const yesterday = new Date();
        yesterday.setDate(new Date().getDate() - 1);

        // Check if selected endDate is beyond today or before startDate
        if (endDate > today) {
            endDate = today; // Set endDate to today if it's beyond today
        } else if (endDate < this.state.startDate) {
            endDate = this.state.startDate; // Set endDate to startDate if it's before startDate
        }

        this.setState({
            endDate: endDate
        });
        this.props.onEndDateChange(endDate);
    }

    render() {
        const { stockName, startDate, endDate } = this.state;

        return (
            <div className="userform" style={{ width: "40%" }}>
                <form onSubmit={this.handleSubmit}>
                    <fieldset>
                        <div style={{ display: "flex", justifyContent: "space-between" }}>
                            <div className="mb-3">
                                <label htmlFor="stockName" className="form-label">
                                    Stock Name
                                </label>
                                <select
                                    name="stockName"
                                    className="form-control"
                                    id="stockName"
                                    required
                                    onChange={this.handleChange}
                                    value={stockName}
                                >
                                    <option value="">Select Stock</option>
                                    <option value="AAPL">AAPL</option>
                                    <option value="AMD">AMD</option>
                                    <option value="AMZN">AMZN</option>
                                    <option value="GOOG">GOOG</option>
                                    <option value="META">META</option>
                                    <option value="MSFT">MSFT</option>
                                    <option value="NVDA">NVDA</option>
                                </select>
                            </div>

                            <div className="mb-3">
                                <label htmlFor="startDate" className="form-label">
                                    Start Date
                                </label>
                                <input
                                    type="date"
                                    name="startDate"
                                    className="form-control"
                                    id="startDate"
                                    required
                                    value={startDate}
                                    onChange={this.handleChange1}
                                    max={new Date().toISOString().substr(0, 10)} // Set max attribute to today's date
                                />
                            </div>

                            <div className="mb-3">
                                <label htmlFor="endDate" className="form-label">
                                    End Date
                                </label>
                                <input
                                    type="date"
                                    name="endDate"
                                    className="form-control"
                                    id="endDate"
                                    required
                                    value={endDate}
                                    onChange={this.handleChange2}
                                    max={new Date().toISOString().substr(0, 10)} // Set max attribute to today's date
                                />
                            </div>
                        </div>
                    </fieldset>
                </form>
            </div>
        );
    }
}

export default UserForm;
