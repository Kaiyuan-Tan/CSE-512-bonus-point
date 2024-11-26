const container = d3.select("#search-container");

container.append("input")
    .attr("type", "text")
    .attr("id", "search-input")
    .attr("placeholder", "Enter search term");

container.append("button")
    .attr("id", "search-button")
    .text("Search")
    .on("click", function() {
        // 2. 捕获输入框内容
        const searchTerm = d3.select("#search-input").property("value");
        
        // 3. 显示搜索内容 (用于示例, 在实际应用中可以调用API)
        if (searchTerm) {
            alert("Searching for: " + searchTerm);
        } else {
            alert("Please enter a search term.");
        }
    });
