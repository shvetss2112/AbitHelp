let likes = document.querySelectorAll('.btn-like');
for (let likee of likes) {
    let id = likee.id;
    id = id.split(':')[1];
    let heart = likee.children[0];
    let csrfform= document.querySelectorAll("[name='csrfmiddlewaretoken']")[0]
    let token =csrfform.value;
    likee.addEventListener('click', () => {
        fetch('/handle-like/' + `${id}`, {headers:{csrfmiddlewaretoken:`${token}`}})
            .then(() => {
                if (heart.classList.contains('liked')) {
                    heart.style.color = 'white';
                    heart.classList.remove('liked')
                    console.log(`${id} disliked`);
                } else if(!heart.classList.contains('liked')){
                  heart.style.color = '#CA2424';
                  heart.classList.add('liked');
                  console.log(`${id} liked`);
                }
            })
    });
}