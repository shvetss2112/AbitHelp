'use strict';
import { EventCalendar, EventList } from "./calendar.js";

let calendar_container = document.getElementById("cal-container");
let event_list_container = document.getElementById("cal-events-container");

let calendar = new EventCalendar(calendar_container);
let event_list = new EventList(event_list_container);

calendar.addEventList(event_list);