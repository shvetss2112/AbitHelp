"use strict";

export class EventCalendar {
    date = new Date();

    calendar;
    #eventList;
    #monthTitle;
    #weekBar;
    #dayGrid;

    constructor(domElem, currentDate = this.date) {
        this.date = currentDate;
        this.calendar = document.createElement("div");
        this.calendar.className = "container calendar";
        domElem.appendChild(this.calendar);
        this.#monthTitle = this.#generateMonthTitle(currentDate);
        this.#weekBar = this.#generateWeekBar();
        this.#dayGrid = this.#generateDays(currentDate);
    }

    addEventList(newEventList) {
        this.#eventList = newEventList;
    }

    updateCalendar(newDate) {
        this.#dayGrid.remove();
        this.#weekBar.remove();
        this.#monthTitle.remove();
        this.#monthTitle = this.#generateMonthTitle(newDate);
        this.#weekBar = this.#generateWeekBar(newDate);
        this.#dayGrid = this.#generateDays(newDate);
        this.date = newDate;
    }

    #generateMonthTitle(date) {
        let month = this.#getMonthTitle(date);
        let year = this.date.getFullYear();
        let monthTitle = document.createElement("div");
        monthTitle.className = "row justify-content-center cal-month-header";
        this.calendar.appendChild(monthTitle);
        let leftB = document.createElement("div");
        leftB.className = "col cal-month-button cal-month-button-left cal-btn";
        leftB.textContent = '<';
        leftB.addEventListener("click", () => {
            this.updateCalendar(new Date(this.date.getFullYear(), this.date.getMonth() - 1, this.date.getDate()));
        })
        let title = document.createElement("div");
        title.className = "col";
        title.textContent = `${month} ${year}`;
        let rightB = document.createElement("div");
        rightB.className = "col cal-month-button cal-month-button-right";
        rightB.textContent = '>';
        rightB.addEventListener("click", () => {
            this.updateCalendar(new Date(this.date.getFullYear(), this.date.getMonth() + 1, this.date.getDate()));
        })
        monthTitle.appendChild(leftB);
        monthTitle.appendChild(title);
        monthTitle.appendChild(rightB);
        return monthTitle;
    }

    #generateWeekBar() {
        let weekBar = document.createElement("div");
        weekBar.className = "row justify-content-center cal-week";
        this.calendar.appendChild(weekBar);
        let linkDayTitleList = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб'];
        for (const day of linkDayTitleList) {
            let weekDay = document.createElement("div");
            weekDay.className = "col cal-сell";
            let innerBuf = document.createElement("div");
            innerBuf.className = "cal-week-day";
            innerBuf.textContent = day;
            weekDay.appendChild(innerBuf);
            weekBar.appendChild(weekDay);
        }
        return weekBar;
    }

    #generateDays(currentDate) {
        let container = document.createElement('div');
        let iteratorSunday = this.#getFirstSunday(currentDate);
        do {
            let calRow = document.createElement("div");
            calRow.className = "row justify-content-center";
            let iteratorDay = new Date(iteratorSunday);

            for (let j = 0; j < 7; j++) {
                let day = document.createElement("div");
                day.className = "col cal-сell";

                let innerBuf = document.createElement("div");
                innerBuf.className = "cal-day";

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
                        if (this.#eventList) {
                            this.#eventList.updateEventList(this.date);
                        }
                    });
                }
                calRow.appendChild(day);
                day.appendChild(innerBuf);
                iteratorDay.setDate(iteratorDay.getDate() + 1);
            }
            container.appendChild(calRow);
            iteratorSunday.setDate(iteratorSunday.getDate() + 7);
        } while (iteratorSunday.getMonth() === currentDate.getMonth())
        this.calendar.appendChild(container);
        return container;
    }

    #getFirstSunday(date) {
        let res = new Date(date);
        res.setDate(1);
        res.setDate(res.getDate() - res.getDay());
        return res;
    }

    #getMonthTitle(date) {
        let indexTitles = ['Січень', 'Лютий', 'Березень', 'Квітень', 'Травень', 'Червень', 'Липень', 'Серпень', 'Вересень', 'Жовтень', 'Листопад', 'Грудень'];
        return indexTitles[date.getMonth()];
    }

    remove() {
        this.calendar.remove();
    }
}

export class EventList {
    date = new Date();
    eventList;
    #eventListContainer;

    constructor(domElem) {
        this.#eventListContainer = domElem;
        this.#generateEventList(this.date);
    }

    updateEventList(date) {
        this.eventList.remove();
        this.#generateEventList(date);

    }

    async #generateEventList(date) {
        this.eventList = document.createElement("div");
        this.eventList.className = "container cal-event-list";
        this.#eventListContainer.appendChild(this.eventList);
        this.date = date;
        let event = this.#getEventByDate();
        let url = this.#requestUrl();
        this.#generateNoEeventElem();
        let response = await fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                if (data.length != 0) {
                    this.eventList.firstChild.remove();
                    for (event of data) {
                        this.#generateEventElem(event);
                    }
                }
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
            });

    }

    #requestUrl() {
        let str_date = this.date.toISOString().split('T')[0];
        let lte_date = new Date(this.date);
        lte_date.setDate(lte_date.getDate() + 1);
        let str_lte_date = lte_date.toISOString().split('T')[0];
        let params = new URLSearchParams({date__gte: str_date, date__lte: str_lte_date});
        return '/api/events/?' + params.toString();
    }

    #generateEventElem(json_event) {
        let event = document.createElement('div');
        event.className = 'cal-event';
        event.textContent = json_event.content;
        this.eventList.appendChild(event);
    }

    #generateNoEeventElem() {
        let event = document.createElement('div');
        event.className = 'cal-event';
        event.textContent = "Немає запланованих подій на цей період";
        this.eventList.appendChild(event);
    }

    #getEventByDate() {
        let json_text = '{"content":"test content"}';
        return JSON.parse(json_text);
    }


}