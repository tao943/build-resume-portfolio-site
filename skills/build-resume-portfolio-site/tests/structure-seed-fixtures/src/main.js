import React from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const h = React.createElement;
const projects = [
  ["01", "Signal atlas", "A navigable system for turning uncertain inputs into visible decisions."],
  ["02", "Living archive", "Evidence remains inspectable while the surrounding story changes."],
  ["03", "Field notes", "Small experiments connect into one coherent practice."],
  ["04", "Release map", "Delivery constraints become part of the visual language."],
];

function Evidence({ item }) {
  return h("article", { className: "evidence" }, h("span", null, item[0]), h("h2", null, item[1]), h("p", null, item[2]));
}

function Split() {
  return h("main", { className: "split", "data-seed": "split-narrative" },
    h("aside", { className: "thesis" }, h("small", null, "STRUCTURE STUDY / 01"), h("h1", null, "Proof moves. The thesis stays."), h("p", null, "An unequal pair of lanes keeps identity and evidence in tension.")),
    h("section", { className: "evidence-stream" }, ...projects.map((item) => h(Evidence, { item, key: item[0] }))));
}

function Stage() {
  return h("main", { className: "stage", "data-seed": "pinned-chapter-stage" },
    h("section", { className: "stage-visual" }, h("small", null, "SHARED STAGE"), h("div", { className: "stage-mark" }, "A→D"), h("p", null, "One field carries every chapter.")),
    h("section", { className: "chapters" }, h("header", null, h("h1", null, "Four acts, one evolving frame.")), ...projects.map((item) => h(Evidence, { item, key: item[0] }))));
}

function Constellation() {
  return h("main", { className: "constellation", "data-seed": "constellation-map" },
    h("header", null, h("small", null, "RELATIONSHIP STUDY / 03"), h("h1", null, "Work is a system, not a stack."), h("p", null, "Shared concerns become explicit paths between projects.")),
    h("section", { className: "map", "aria-label": "Project relationship overview" }, ...projects.map((item, index) => h("a", { href: `#project-${index}`, className: `node node-${index + 1}`, key: item[0] }, h("span", null, item[0]), item[1]))),
    h("section", { className: "linear" }, ...projects.map((item, index) => h("div", { id: `project-${index}`, key: item[0] }, h(Evidence, { item })))));
}

const seed = new URLSearchParams(location.search).get("seed") || "split-narrative";
const Component = seed === "pinned-chapter-stage" ? Stage : seed === "constellation-map" ? Constellation : Split;
createRoot(document.getElementById("root")).render(h(Component));
