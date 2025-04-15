"use strict";

export class EventList{
    date=new Date();
    eventList;
    #eventListContainer;

    constructor(domElem){
        this.eventListContainer = document.createElement("div");
        this.eventListContainer.className="event-list";
        domElem.appendChild(this.eventListContainer);
    }

    #generateEventList(date){
        // Logic to generate event list based on the date
    }

    updateEventList(date){
        this.#eventListContainer.remove();
        this.#eventListContainer = this.#generateEventList(date);
        this.date=date;
    }

    addEvent(event){
        // Logic to add an event to the list
    }

    removeEvent(eventId){
        // Logic to remove an event from the list
    }
}