$(document).ready(function () {
    if (window.location.pathname.includes('/products/list')){
        const pagination = document.querySelector('.pagination');
        if (pagination){
            pagination.style.display = 'inline-flex'
        }
    }
});