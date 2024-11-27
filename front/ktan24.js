const searchFields = ["subject", "code", "title", "instructor"];
// API = "http://127.0.0.1:8000/"
API = "http://121.41.33.45:31002"

container = d3.select("#search-container")

description = container.append("input")
    .attr("type", "text")
    .attr("class", "long-search")
    .attr("placeholder", "Search Courses")

const popup = d3.select("body")
    .append("div")
    .attr("class", "popup")
    .style("display", "none");

popup.append("button")
    .attr("id", "close-button")
    .text("X")
    .on("click", function() {
        ClosePop()
    });
searchFields.forEach(field => {
    popup.append("input")
        .attr("type", "text")
        .attr("class", "small-search")
        .attr("placeholder", field);
});
container.append("button")
    .attr("class", "search-button")
    .style("border-radius","15px")
    .text("Search by description")
    .on("click", function() {
        query = d3.select('.long-search').property('value');
        SemanticSearch(query)
    });
container.append("button")
    .attr("class", "search-button")
    .style("border-radius","15px")
    .text("Advanced Search")
    .on("click", function() {
        console.log("pressed")
        AdvancedSearch()
    });

popup.append("button")
    .attr("id", "confirm-button")
    .text("Search")
    .on("click", function() {
        const inputs = popup.selectAll(".small-search").nodes();
        const searchParams = {};
        inputs.forEach(input => {
            searchParams[input.placeholder] = input.value;
        });
        console.log("Searching with parameters:", searchParams);
        popup.style("display", "none");
        FilterSearch(searchParams)
        ClosePop()
    });
function AdvancedSearch() {
    popup.style("display", "block");
}
function FilterSearch(query){
    d3.select("#results").html("");
    subject = query['subject']
    code = query['code']
    title = query['title']
    instructor = query['instructor']
    fetch(API+`filter?subject=${subject}&code=${code}&title=${title}&instructor=${instructor}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Data received:', data);
        NewData(data)
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}
function SemanticSearch(query){
    d3.select("#results").html("");
    fetch(API+`search?description=${query}`)
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Data received:', data);
        NewData(data)
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}
function ClosePop(){
    d3.selectAll('.small-search').property('value', "")
    popup.style("display", "none");
}
function NewData(data){
    courses=data['data']
    courses.forEach((value, index) => {
        code = value['code']
        credit = value['credit']
        description = value['description']
        instructor = value['instructor']
        subject = value['subject']
        title = value['title']
        item = d3.select("#results")
            .append("div")
            // .attr("class","col-8")
            .attr("class", "result-item col-8")
        
        item.append("div")
            // .attr("class","col-8")
            .text(subject+" "+code+" : "+title)
            .style("font-weight", "bold")
            .style("font-size","18px")
        item.append("div")
            // .attr("class","col-8")
            .html(`<span class='bold-text'>Instructor: </span>${instructor}<span class='bold-text'> credit: </span>${credit}`);
        item.append("div")
            .attr("class","description")
            .text(description)
            // .style("font-weight", "bold")
            .style("font-size","14px")
        d3.selectAll(".bold-text")
            .style("font-weight", "bold");
    });
}