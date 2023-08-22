function user(){
    const userIcon = document.querySelector('.user-icon')
    const welcomeText = document.querySelector('.welcome-text')
        if(welcomeText.style.display =='none'){
            welcomeText.style.display='block'
        }
        else{
            welcomeText.style.display='none'
 
    }
}

// ----------create form start

function familyForm(){
    document.querySelector('.family-form-con').style.display='block'
    document.querySelector('.create-staff-form-con').style.display='none'
}
function personalback(){
    document.querySelector('.family-form-con').style.display='none'
    document.querySelector('.create-staff-form-con').style.display='block'
}
function bankForm(){
    document.querySelector('.family-form-con').style.display='none'
    document.querySelector('.bankform-con').style.display='block'
}
function backbank(){
    document.querySelector('.family-form-con').style.display='block'
    document.querySelector('.bankform-con').style.display='none'
}
function govt(){
    document.querySelector('.govt-form-con').style.display='block'
    document.querySelector('.bankform-con').style.display='none'
}
function backgovt(){
    document.querySelector('.govt-form-con').style.display='none'
    document.querySelector('.bankform-con').style.display='block'
}