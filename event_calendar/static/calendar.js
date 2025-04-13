"use strict";
function generateCalendar(domElem,currentDate){
    let calendar = document.createElement("div");
    calendar.className="container calendar";
    domElem.appendChild(calendar);

    generateMonthTitle(calendar,currentDate);

    generateWeekBar(calendar);

    generateDays(calendar,currentDate);

    return calendar;
}
function generateDays(calendar,currentDate){
    let iteratorSunday=getFirstSunday(currentDate);
    do{
        let calRow = document.createElement("div");
        calRow.className="row justify-content-center";
        let iteratorDay=  new Date(iteratorSunday);
        for(let j=0;j<7;j++){

            let day = document.createElement("div");
            day.className="col cal-сell";

            let innerBuf = document.createElement("div");
            innerBuf.className="cal-day";
            if(currentDate.getMonth()!=iteratorDay.getMonth()){
                innerBuf.classList.add("cal-inactive");
            }
            if(currentDate.getDate()==iteratorDay.getDate()){
                innerBuf.classList.add("cal-cell-selected");
            }
            innerBuf.textContent=iteratorDay.getDate();
            calRow.appendChild(day);
            day.appendChild(innerBuf);
            iteratorDay.setDate(iteratorDay.getDate()+1);
        }
        calendar.appendChild(calRow);
        iteratorSunday.setDate(iteratorSunday.getDate()+7);
    }while(iteratorSunday.getMonth() == currentDate.getMonth())
}
function getFirstSunday(date){
    let res = new Date(date);
    res.setDate(1);
    res.setDate(res.getDate()-res.getDay());
    return res;
}
function generateWeekBar(calendar){
    let weekBar = document.createElement("div");
    weekBar.className="row justify-content-center cal-week";
    calendar.appendChild(weekBar);
    let linkDayTitleList=['Вс','Пн','Вт','Ср','Чт','Пт','Сб'];
    for(const day of linkDayTitleList){
        let weekDay = document.createElement("div");
        weekDay.className="col cal-сell";
        let innerBuf=document.createElement("div"); innerBuf.className = "cal-week-day";
        innerBuf.textContent=day;
        weekDay.appendChild(innerBuf);
        weekBar.appendChild(weekDay);
    }
}
function generateMonthTitle(calendar,date){
    let month = getMonthTitle(date);
    let monthTitle = document.createElement("div");
    monthTitle.className="row justify-content-center cal-header";
    calendar.appendChild(monthTitle);
    let leftB= document.createElement("div");
    leftB.className="col cal-month-button cal-month-button-left";
    leftB.textContent='<';
    let title= document.createElement("div");
    title.className="col";
    title.textContent=month;
    let rightB= document.createElement("div");
    rightB.className="col cal-month-button cal-month-button-right";
    rightB.textContent='>';
    monthTitle.appendChild(leftB);
    monthTitle.appendChild(title);
    monthTitle.appendChild(rightB);
}
function getMonthTitle(date){
    let indexTitles=[
        'Січень',
        'Лютий',
        'Березень',
        'Квітень',
        'Травень',
        'Червень',
        'Липень',
        'Серпень',
        'Вересень',
        'Жовтень',
        'Листопад',
        'Грудень'];
    return indexTitles[date.getMonth()];
}
let container = document.getElementById("cal-container");

let calendar = generateCalendar(container,new Date(2025,2,8));