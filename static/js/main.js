async function nextProductPage(){
    current_page = parseInt(window.location.href.match("(\\d+).html")[1]);
    next_page = current_page + 1;
    next_page_url = window.location.href.replace(/\d+.html/g, `${next_page}.json`);
    resp = await fetch(next_page_url);
    data = await resp.json();
    console.log("got next page data", data)
    for (row of data._rendered){
        $('.content').append(row)
    }
}
