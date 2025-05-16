    "use strict";

function generateDiv(parent, className = "", textContent = "") {
    let div = document.createElement("div");
    div.className = className;
    div.innerHTML = textContent;
    parent.appendChild(div);
    return div;
}

export class EventCalendar {
    date = new Date();
    _container;
    _calendar;
    _monthTitle;
    _weekBar;
    _dayGrid;

    _eventList;
    _events = [];

    constructor(domElem, currentDate = this.date) {
        this._container = domElem;
        this.date = currentDate;
        this.updateCalendar(this.date);
        this._makeRequest();
    }

    updateCalendar(newDate = this.date) {
        this.remove();
        if (this.date.getMonth() !== newDate.getMonth() || this.date.getFullYear() !== newDate.getFullYear()) {
            this._makeRequest(newDate);
        }
        this.date = new Date(newDate);
        this._calendar = generateDiv(this._container, "container cal-calendar ps-0");
        this._monthTitle = this._generateMonthBar();
        this._weekBar = this._generateWeekBar();
        this._dayGrid = this._generateDayGrid();
        if (this._eventList) {
            this._eventList.updateEventList(this._events[this.date.getDate()]);
        }
    }

    _generateMonthBar() {
        let month = this._getMonthTitle(this.date);
        let year = this.date.getFullYear();

        let monthTitle = generateDiv(this._calendar, "row justify-content-center cal-month-bar");

        let leftB = generateDiv(monthTitle, "col cal-month-btn", '<');
        let title = generateDiv(monthTitle, "col", `${month} ${year}`);
        let rightB = generateDiv(monthTitle, "col cal-month-btn", '>');

        let leftUpDate = new Date(this.date.getFullYear(), this.date.getMonth() - 1, this.date.getDate());
        let rightUpDate = new Date(this.date.getFullYear(), this.date.getMonth() + 1, this.date.getDate());

        leftB.addEventListener("click", () => this.updateCalendar(leftUpDate));
        rightB.addEventListener("click", () => this.updateCalendar(rightUpDate));

        return monthTitle;
    }

    _generateWeekBar() {
        let weekBar = generateDiv(this._calendar, "row justify-content-center cal-week-bar");
        let weekDayTitleList = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
        for (const day of weekDayTitleList) {
            let weekDay = generateDiv(weekBar, "col cal-сell");
            let innerBuf = generateDiv(weekDay, "cal-week-day", day);
        }
        return weekBar;
    }

    _generateDayGrid() {
        let dayGrid = generateDiv(this._calendar, 'cal-day-grid');
        let iteratorSunday = this._getFirstSunday(this.date);
        do {
            let calRow = generateDiv(dayGrid, "row justify-content-center");
            let iteratorDay = new Date(iteratorSunday);

            for (let j = 0; j < 7; j++) {
                let cal_cell = generateDiv(calRow, "col cal-сell");
                let cal_day = generateDiv(cal_cell, "cal-day", iteratorDay.getDate());

                if (this._events[iteratorDay.getDate()]) {
                    cal_day.classList.add("cal-day-marked");
                }

                if (this.date.getMonth() !== iteratorDay.getMonth()) {
                    cal_day.classList.add("cal-day-inactive");
                } else if (this.date.getDate() === iteratorDay.getDate()) {
                    cal_day.classList.add("cal-day-selected");
                } else {
                    let upDate = new Date(this.date.getFullYear(), this.date.getMonth(), iteratorDay.getDate());
                    cal_cell.addEventListener("click", () => this.updateCalendar(upDate));
                }

                iteratorDay.setDate(iteratorDay.getDate() + 1);
            }
            iteratorSunday.setDate(iteratorSunday.getDate() + 7);
        } while (iteratorSunday.getMonth() === this.date.getMonth())
        return dayGrid;
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
        if (this._calendar) {
            this._calendar.remove();
        }
    }

    async _makeRequest(newDate = this.date) {
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
                for (let event of data) {
                    let eventDate = new Date(event.date);
                    if (!this._events[eventDate.getDate()]) {
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
        let gte_date = new Date(newDate.getFullYear(), newDate.getMonth(), 1);
        let lte_date = new Date(newDate.getFullYear(), newDate.getMonth() + 1, 1);
        let str_gte_date = gte_date.toLocaleString('sv-SE', {hour12: false}).split(" ")[0];
        let str_lte_date = lte_date.toLocaleString('sv-SE', {hour12: false}).split(" ")[0];
        let params = new URLSearchParams({date__gte: str_gte_date, date__lte: str_lte_date});
        return '/api/events/?' + params.toString();
    }

    addEventList(newEventList) {
        this._eventList = newEventList;
    }
}

export class EventList {
    _container;
    eventList;

    constructor(domElem) {
        this._container = domElem;
        this._generateEventList();
    }

    updateEventList(data) {
        this.remove();
        this._generateEventList(data);
    }

    _generateEventList(data) {
        this.eventList = document.createElement("div");
        this.eventList.className = "container cal-event-list";
        this._container.appendChild(this.eventList);
        if (!data) {
            this._generateNoEeventElem();
        } else {
            for (let event of data) {
                this._generateEventElem(event);
            }
        }
    }
    _listTimeString(new_event){
        let date = new Date(new_event.date);
        let buf_hour= (date.getHours()<10)?"0":'';
        let buf_min= (date.getMinutes()<10)?"0":'';
        let date_time = buf_hour+date.getHours()+':'+buf_min+date.getMinutes();
        return date_time;
    }
    _listDateString(new_event){
        let date = new Date(new_event.date);
        let buf_day= (date.getDate()<10)?"0":'';
        let buf_month= (date.getMonth()<10)?"0":'';
        let date_time = buf_day+date.getDate()+'.'+buf_month+date.getMonth()+'.'+date.getFullYear();
        return date_time;
    }
    _generateEventElem(new_event) {
        let date_time = this._listTimeString(new_event);
        let date_date=this._listDateString(new_event);
        let event = generateDiv(this.eventList, "cal-event row");
        let text_container = generateDiv(event,"col-sm-12 col-lg-10");
        let event_text = document.createElement("a");
        event.appendChild(event_text);
        event_text.setAttribute('href','/'+new_event.id);
        text_container.appendChild(event_text);
        let dop_col = generateDiv(event,"col col-lg-2");
        let dop_row = generateDiv(dop_col, "row h-100 align-items-stretch");
        let dop_date = generateDiv(generateDiv(dop_row,"col col col-lg-12 col-md-6"),"list-item-date",date_date+'<br>'+date_time);
        let like_btn = generateDiv(generateDiv(dop_row,"col col-lg-12 col-md-6 text-end d-flex"),"btn ms-auto mt-auto");
        let heart = document.createElement("i");
        heart.className = "bi bi-heart-fill";
        like_btn.appendChild(heart);


        event_text.textContent = new_event.content;
    }

    _generateNoEeventElem() {
        generateDiv(this.eventList, "cal-event", "Немає запланованих подій на цей період");
    }

    remove() {
        this.eventList.remove();
    }
}
