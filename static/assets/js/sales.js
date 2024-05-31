function filterToggler() {
    document.getElementById("filterToggler").classList.toggle("collapse");
}

function filterCategory() {
    let filter = document.getElementById("inputGroupSelect04").value;
    console.log(filter);
    window.location.href=`/sales?category=${filter}`
}

/**
 * Reset filter at sales.html
 */
function resetCategory() {
    window.location.href=`/sales`
}

function filterStatus() {
    let status = document.getElementById("inputGroupSelect05").value;
    console.log(status)
    window.location.href=`/sales?status=${status}`
}

function exportCSV() {
    let param = window.location.search;
    let path = window.location.pathname;
    if (param) {
        alert(path + param + "&download=true");
        window.location.href= path + param + "&download=true";
    }
    else {
        window.location.href=path + "?download=true"
    }
}