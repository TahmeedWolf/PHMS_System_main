function sayHi() {
    console.log("Hello!");
}

/**
 * used at nav-bar
 */
function sidenavToggler() {
    document.getElementById("navbarToggleExternalContent").classList.toggle("sidenav");
}

function adminToolToggler() {
    document.getElementById("navbarDropdownMenuLink").classList.toggle("collapse");
}

/**
 * used at all pages with pagination
 */
function goToPage(page) {
    let param = window.location.search;
    let path = window.location.pathname;
    if (param) {
        // alert(path + param + "&download=true");
        // window.location.href= path + param + "&download=true";
        window.location.href = path + param + "&page=" + page;
    }
    else {
        // window.location.href=path + "?download=true";
        window.location.href = path + "?page=" + page;
    }
    // document.getElementById("dropDownButtonDiv").classList.toggle("show");
}


/**
 * used at admin tools: email config
 * @param {*} sales_type_id 
 */
function modalSalesType(sales_type_id, sales_type, email_list) {
    console.log(`${sales_type_id}`);
    document.getElementById("salesTypeLabel").innerText= `${sales_type}`;
    document.getElementById("salesEmailList").value= `${email_list}`;
    document.getElementById("salesTypeForm").action = `/email_configuration?sales_type_id=${sales_type_id}`;
}

/**
 * used at payment page
 */
function generateInvoice(payment_id) {
    let param = window.location.search;
    let path = window.location.pathname;
    if (param) {
        alert(path + param + "&download=true");
        // window.location.href= path + param + "&download=true";
        window.open(path + param + "&download=true");
    }
    else {
        // window.location.href=path + "?download=true";
        window.open(path + "?download=true");
    }
}