import React from "react";
import ReactDOM from "react-dom";

const Frontend = () => (
  <p>Hello! It works!</p>
);

const wrapper = document.getElementById("frontend");
wrapper ? ReactDOM.render(<Frontend />, wrapper) : null;