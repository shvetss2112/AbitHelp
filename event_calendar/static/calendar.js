"use strict";
function generateDiv(parent,className="",textContent="") {
    let div = document.createElement("div");
    div.className = className;
    div.textContent = textContent;
    parent.appendChild(div);
    return div;
}

export class EventCalendar {
    date = new Date();
    calendar;
    _eventList;
    _monthTitle;
    _weekBar;
    _dayGrid;
    _container;
    _events=[];

    constructor(domElem, currentDate = this.date) {
        this._container=domElem;
        this.date = currentDate;
        this.updateCalendar(this.date);
        this._makeRequest();
    }

    async _makeRequest(newDate=this.date){
        this._events = [];
        let url = this._requestUrl(newDate);
        let response = await fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                for(let event of data){
                    let eventDate = new Date(event.date);
                    if(!this._events[eventDate.getDate()]){
                        this._events[eventDate.getDate()] = [];

                    }
                    this._events[eventDate.getDate()].push(event);
                }
                this.updateCalendar();
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });

    }

    _requestUrl(newDate) {
        let gte_date = new Date(newDate.getFullYear(),newDate.getMonth(),1);
        let lte_date = new Date(newDate.getFullYear(),newDate.getMonth()+1,1);
        let str_gte_date = gte_date.toLocaleString('sv-SE',{hour12:false}).split(" ")[0];
        let str_lte_date = lte_date.toLocaleString('sv-SE',{hour12:false}).split(" ")[0];
        let params = new URLSearchParams({date__gte: str_gte_date, date__lte: str_lte_date});
        return '/api/events/?' + params.toString();
    }

    addEventList(newEventList) {
        this._eventList = newEventList;
    }

    updateCalendar(newDate = this.date) {
        this.remove();
        if(this.date.getMonth()!==newDate.getMonth() || this.date.getFullYear() !== newDate.getFullYear()){
            this._makeRequest(newDate);
        }
        this.date = new Date(newDate);
        this.calendar =generateDiv(this._container, "container cal-calendar");
        this._monthTitle = this._generateMonthBar(this.date);
        this._weekBar = this._generateWeekBar(this.date);
        this._dayGrid = this._generateDayGrid(this.date);
        if(this._eventList){
            this._eventList.updateEventList(this._events[this.date.getDate()]);
        }
    }

    _generateMonthBar(date) {
        let month = this._getMonthTitle(date);
        let year = this.date.getFullYear();
        let monthTitle =generateDiv(this.calendar,"row justify-content-center cal-month-header");
        let leftB = generateDiv(monthTitle,"col cal-month-button cal-month-button-left cal-btn",'<');
        leftB.addEventListener("click", () => {
            let upDate = new Date(this.date.getFullYear(), this.date.getMonth() - 1, this.date.getDate());
            this.updateCalendar(upDate);
        })
        let title = generateDiv(monthTitle,"col",`${month} ${year}`);
        let rightB = generateDiv(monthTitle,"col cal-month-button cal-month-button-right cal-btn",'>');
        rightB.addEventListener("click", () => {
            let upDate = new Date(this.date.getFullYear(), this.date.getMonth() + 1, this.date.getDate());
            this.updateCalendar(upDate);
        })
        return monthTitle;
    }

    _generateWeekBar() {
        let weekBar = generateDiv(this.calendar, "row justify-content-center cal-week");
        let weekDayTitleList = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
        for (const day of weekDayTitleList) {
            let weekDay = generateDiv(weekBar, "col cal-сell");
            let innerBuf = generateDiv(weekDay, "cal-week-day",day);
        }
        return weekBar;
    }

    _generateDayGrid(currentDate) {
        let container =generateDiv(this.calendar,);
        let iteratorSunday = this._getFirstSunday(currentDate);
        do {
            let calRow = generateDiv(container, "row justify-content-center");
            let iteratorDay = new Date(iteratorSunday);

            for (let j = 0; j < 7; j++) {
                let day = generateDiv(calRow, "col cal-сell");
                let innerBuf = generateDiv(day, "cal-day");

                if(this._events[iteratorDay.getDate()]){
                    innerBuf.classList.add("cal-cell-marked");
                }

                if (currentDate.getMonth() !== iteratorDay.getMonth()) {
                    innerBuf.classList.add("cal-inactive");
                } else if (currentDate.getDate() === iteratorDay.getDate()) {
                    innerBuf.classList.add("cal-cell-selected");
                }

                innerBuf.textContent = iteratorDay.getDate();
                if (!innerBuf.classList.contains("cal-inactive")) {
                    innerBuf.addEventListener("click", () => {
                        let upDate = new Date(currentDate);
                        upDate.setDate(innerBuf.textContent);
                        this.updateCalendar(upDate);
                    });
                }
                iteratorDay.setDate(iteratorDay.getDate() + 1);
            }
            iteratorSunday.setDate(iteratorSunday.getDate() + 7);
        } while (iteratorSunday.getMonth() === currentDate.getMonth())
        return container;
    }

    _getFirstSunday(date) {
        let res = new Date(date);
        res.setDate(1);
        res.setDate(res.getDate() - res.getDay());
        return res;
    }

    _getMonthTitle(date) {
        let indexTitles = ['Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень', 'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'];
        return indexTitles[date.getMonth()];
    }

    remove() {
        if(this.calendar){
            this.calendar.remove();
        }
    }
}

export class EventList {
    _container;
    eventList;
    constructor(domElem) {
        this._container = domElem;
        this._generateEventList(this.date);
    }

    updateEventList(data) {
        this.remove();
        this._generateEventList(data);
    }

    _generateEventList(data) {
        this.eventList = document.createElement("div");
        this.eventList.className = "container cal-event-list";
        this._container.appendChild(this.eventList);
        if(!data){
            this._generateNoEeventElem();
        }
        else{
            for(let event of data){
                this._generateEventElem(event);
            }
        }
    }

    _generateEventElem(new_event) {
        let event = generateDiv(this.eventList, "cal-event");
        event.textContent = new_event["content"];
    }

    _generateNoEeventElem() {
        generateDiv(this.eventList, "cal-event","Немає запланованих подій на цей період");
    }
    remove(){
        this.eventList.remove();
    }
}