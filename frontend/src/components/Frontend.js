import React from "react";
import ReactDOM from "react-dom";

const Frontend = () => (
	<div>
		<h1 className="display-1">Hello! It works!!</h1>
	</div>
);

const wrapper = document.getElementById("frontend");
wrapper ? ReactDOM.render(<Frontend />, wrapper) : null;