let links = document.querySelectorAll('.nav-link');
    for(let navLink of links){
        let location = window.location.pathname;
        let hash = window.location.hash;
        console.log(location);
        let linkHref=navLink.getAttribute('href');
        if(linkHref === location && hash === '' || linkHref ===  hash){
            navLink.classList.add('nav-active');
        }
    }