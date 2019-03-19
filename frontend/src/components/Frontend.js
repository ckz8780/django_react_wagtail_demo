import React from "react";
import ReactDOM from "react-dom";

const Frontend = () => (
	<div>
		<p>Hello! It works!</p>
	</div>
);

const wrapper = document.getElementById("frontend");
wrapper ? ReactDOM.render(<Frontend />, wrapper) : null;