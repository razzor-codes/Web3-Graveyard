const input = document.querySelector(".finder__input");
const finder = document.querySelector(".finder");
const form = document.querySelector("form");
const elem = document.getElementById("about");
const footer = document.getElementById("footer");
const about_list = document.getElementById("about-list");
const title = document.getElementById("project-title");
const table = document.getElementById("showData");
const add_note = document.getElementById("add_note");
const inp = document.getElementById("q");
const nodes = document.getElementById('nodes');

elem.style.display = "none";
footer.style.display = "none";
about_list.style.display = "none";

var attacks;
var keys;
fetch('assets/exploit-database.json')
  .then(res => res.json())
  .then(data =>
     {
      attacks = data;
      keys = Object.keys(attacks);
  });

// const keys = Object.keys(attacks);
input.addEventListener("focus", () => {
  finder.classList.add("active");
});

input.addEventListener("blur", () => {
  if (input.value.length === 0) {
    finder.classList.remove("active");
  }
});

function searchDatabase(input){
  let attack = attacks[input];
  try{
    if(attack != undefined){
      title.innerHTML = input;
      let values = JSON.parse(JSON.stringify(attack));
      let keys = Object.keys(values);
      let date = values[keys[0]];
      let loss = values[keys[1]];
      let attacker_add = values[keys[2]];
      let attacker_cont = values[keys[3]];
      let project_cont = values[keys[4]];
      let postmortem = values[keys[5]];
      let poc = values[keys[6]];
      let chain = values[keys[7]];
      let bugtype = values[keys[8]];
      let project_type = values[keys[9]];
      let tags = values[keys[10]];
      let note = values[keys[11]];
      table.innerHTML += 

      "<tr><td><b>Date</b></td><td>" +  date + "</td></tr>" +
      "<tr><td><b>Estimated Loss</b></td><td>" +  loss + "</td></tr>" +
      "<tr><td><b>Attacker's Address</b></td><td>" +  attacker_add + "</td></tr>" +
      "<tr><td><b>Attacker's Contract</b></td><td>" +  attacker_cont + "</td></tr>" + 
      "<tr><td><b>Project Contract(s)</b></td></tr>" ;

      let project_cont_values = JSON.parse(JSON.stringify(project_cont));
      let project_cont_keys = Object.keys(project_cont_values);

      for(let i=0 ; i<project_cont_keys.length; i++){
        table.innerHTML += "<tr><td><b>&emsp;&emsp;&emsp;" + project_cont_keys[i] + "</b></td><td>"+ project_cont_values[project_cont_keys[i]] + "</td></tr>"
      }

      table.innerHTML += 

      "<tr><td><b>Postmortem</b></td><td> " + postmortem + "</td></tr>" +
      "<tr><td><b>PoC</b></td><td><a href='" +  poc + "'/>" + poc + "</td></tr>" +
      "<tr><td><b>Chain</b></td><td>" +  chain + "</td></tr>" +
      "<tr><td><b>BugType</b></td><td>" +  bugtype + "</td></tr>" + 
      "<tr><td><b>Project Type</b></td><td>" +  project_type + "</td></tr>" +
      "<tr><td><b>Tags</b></td><td>" + tags + "</td></tr>";

      if(note != ""){
        add_note.innerHTML += "<i><b>Note: </b>" + note + "</i>";
      }
    }
    else{
      title.innerHTML = "Project Not Found";
    }
  }
  catch (error){
    console.log(error)
  }
}

form.addEventListener("submit", (ev) => {
  ev.preventDefault();
  finder.classList.add("processing");
  finder.classList.remove("active");
  input.disabled = true;
  if(elem.style.display === "none") {
    elem.style.display = "block";
    footer.style.display = "block";
    about_list.style.display = "block";
    
  }
  table.innerHTML = "";
  add_note.innerHTML = "";
  searchDatabase(finder.querySelector(".finder__input").value.trim().toLowerCase());
  setTimeout(() => {
    finder.classList.remove("processing");
    input.disabled = false;
    if (input.value.length > 0) {
      finder.classList.add("active");
    }
    elem.scrollIntoView();

  }, 1000);
});

inp.oninput = function () {
  let results = [];
  const userInput = this.value;
  nodes.innerHTML = "";
  nodes.style.borderLeft = 'none';
  if (userInput.length > 0) {
    results = getResults(userInput);
    nodes.style.display = "block";
    for (i = 0; i < results.length; i++) {
      nodes.innerHTML += "<li>" + results[i] + "</li>";
      nodes.style.borderLeft = '5px solid red';

    }
  }
};
function getResults(input) {
  const results = [];
  for (i = 0; i < keys.length; i++) {
    if (input === keys[i].slice(0, input.length)) {
      results.push(keys[i]);
    }
  }
  return results;
}
nodes.onclick = function (event) {
  const setValue = event.target.innerText;
  inp.value = setValue;
  this.innerHTML = "";
};