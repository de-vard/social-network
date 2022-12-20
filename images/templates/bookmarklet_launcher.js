(function(){
    if (window.myBookmarklet !== undefined){
        myBookmarklet();
    }
    else {
        document.body.appendChild(document.createElement('script')).src='https://28cf-194-54-153-123.eu.ngrok.io/static/js/bookmarklet.js?r='
        + Math.floor(Math.random()*99999999999999999999);
    }
})();